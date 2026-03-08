import asyncio
import logging
import os
import time
from typing import Any, Awaitable, Callable

from fastapi import FastAPI
from redis.asyncio import Redis

from app.clients.redis_client import (
    USAGE_KEY_PREFIX,
    create_usage_key,
    get_redis_session,
)
from app.data.user_billing_store import UserBillingStore
from app.db.connection import get_async_db_session
from app.models.user_billing import UserBillingUpdate
from app.services.user_token import (
    TokenUsageCache,
)
from app.utils import get_or_throw

logger = logging.getLogger(__name__)

USAGE_CACHE_TTL_SECONDS = int(get_or_throw("BILLING_CACHE_TTL_SECONDS"))
USAGE_FLUSH_INTERVAL_SECONDS = int(get_or_throw("BILLING_FLUSH_INTERVAL_SECONDS"))
TOKEN_USAGE_SYNC_POLLER_TASK_ATTR = "token_usage_sync_poller_task"
UPDATED_AT_EPOCH_FIELD = "updated_at_epoch"
SYNCED_AT_EPOCH_FIELD = "synced_at_epoch"
FLUSH_LOCK_SUFFIX = ":flush_lock"


async def flush_with_lock(
    redis: Redis,
    lock_key: str,
    lock_ttl_seconds: int,
    fn: Callable[[], Awaitable[None]],
    wait_timeout_seconds: float = 5.0,
) -> bool:
    lock = redis.lock(
        lock_key,
        timeout=lock_ttl_seconds,
        blocking=True,
        blocking_timeout=wait_timeout_seconds,
    )
    lock_acquired = await lock.acquire()
    if not lock_acquired:
        logger.error("Timed out waiting for flush lock: %s", lock_key)
        return False

    try:
        await fn()
        return True
    finally:
        await lock.release()


async def flush_user_token_usage(user_id: int) -> None:
    """Flush one user's pending Redis usage into DB."""
    async with get_redis_session() as redis:
        await _flush_user_token_usage(redis=redis, user_id=user_id)


async def _flush_user_token_usage(redis: Redis, user_id: int) -> None:
    """Flush one user's cached token usage snapshot into DB and refresh cache.

    Called directly from logout and injected as the per-user callback for lock-guarded
    periodic sync execution.
    """
    usage_key = create_usage_key(user_id=user_id)
    lock_key = f"{usage_key}{FLUSH_LOCK_SUFFIX}"

    async def _flush() -> None:
        usage_hash = await redis.hgetall(
            usage_key
        )  # pyright: ignore[reportGeneralTypeIssues]
        if not usage_hash:
            # This can happen if the flush trigger expires after the usage hash was deleted
            # (e.g., logout/cache clear) or evicted/expired between scheduling and handling.
            logger.error(f"Missing token usage cache for key {usage_key}")
            return

        usage_cache = TokenUsageCache.model_validate(usage_hash)

        async with get_async_db_session() as session:
            store = UserBillingStore(user_id=user_id, session=session)
            updated_billing = await store.apply_token_usage_snapshot(
                user_id=user_id,
                token_usage_update=UserBillingUpdate(
                    available_tokens=usage_cache.available_tokens,
                    last_used_tokens=usage_cache.last_used_tokens,
                    total_used_tokens=usage_cache.total_used_tokens,
                ),
            )

        updated_cache = TokenUsageCache(
            available_tokens=updated_billing.available_tokens,
            last_used_tokens=updated_billing.last_used_tokens,
            total_used_tokens=updated_billing.total_used_tokens,
            updated_at_epoch=usage_cache.updated_at_epoch,
            synced_at_epoch=int(time.time()),
        )

        async with redis.pipeline(transaction=True) as pipeline:
            pipeline.hset(
                usage_key,
                mapping=updated_cache.model_dump(),
            )
            pipeline.expire(usage_key, USAGE_CACHE_TTL_SECONDS)
            await pipeline.execute()

    await flush_with_lock(redis, lock_key, 30, _flush)


async def _sync_pending_token_usage() -> None:
    current_epoch = int(time.time())
    async with get_redis_session() as redis:
        async for usage_key in redis.scan_iter(match=f"{USAGE_KEY_PREFIX}*"):
            user_id = int(usage_key.removeprefix(USAGE_KEY_PREFIX))
            updated_at_value, synced_at_value = await redis.hmget(
                usage_key, UPDATED_AT_EPOCH_FIELD, SYNCED_AT_EPOCH_FIELD
            )  # pyright: ignore[reportGeneralTypeIssues]
            updated_at_epoch = int(updated_at_value)
            synced_at_epoch = int(synced_at_value)

            # Flush when there is new usage since last sync and sync interval elapsed.
            if (
                updated_at_epoch <= synced_at_epoch
                or current_epoch - synced_at_epoch < USAGE_FLUSH_INTERVAL_SECONDS
            ):
                continue

            await _flush_user_token_usage(redis=redis, user_id=user_id)


async def run_token_usage_sync_poller() -> None:
    while True:
        await _sync_pending_token_usage()
        await asyncio.sleep(USAGE_FLUSH_INTERVAL_SECONDS)


def _crash_on_token_sync_failure(task: asyncio.Task[Any]) -> None:
    if task.cancelled():
        return
    exc = task.exception()
    if exc:
        logger.critical("Periodic token sync poller crashed: %s", exc)
        os._exit(1)


def start_token_usage_sync_poller(app: FastAPI) -> asyncio.Task[Any]:
    task = asyncio.create_task(run_token_usage_sync_poller())
    task.add_done_callback(_crash_on_token_sync_failure)
    setattr(app.state, TOKEN_USAGE_SYNC_POLLER_TASK_ATTR, task)
    logger.info("Started periodic token usage sync poller task")
    return task


async def stop_token_usage_sync_poller(app: FastAPI) -> None:
    task: asyncio.Task[Any] | None = getattr(
        app.state, TOKEN_USAGE_SYNC_POLLER_TASK_ATTR, None
    )
    if not task:
        return

    if task.done() and not task.cancelled():
        exc = task.exception()
        if exc:
            logger.warning("Token usage sync poller failed before shutdown: %s", exc)
            raise exc

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Token usage sync poller task cancelled")
