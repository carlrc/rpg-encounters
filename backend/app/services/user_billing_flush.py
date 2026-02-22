import asyncio
import logging
import os

from fastapi import FastAPI
from redis.asyncio import Redis

from app.clients.redis_client import (
    create_expired_events_channel,
    create_usage_key,
    get_redis_session,
    parse_usage_flush_user_id,
)
from app.data.user_billing_store import UserBillingStore
from app.db.connection import get_async_db_session
from app.utils import get_or_throw

logger = logging.getLogger(__name__)

USAGE_CACHE_TTL_SECONDS = int(get_or_throw("BILLING_CACHE_TTL_SECONDS"))


async def flush_user_usage(user_id: int) -> None:
    """Flush one user's pending Redis usage into DB."""
    async with get_redis_session() as redis:
        await _flush_user_usage_with_redis(redis=redis, user_id=user_id)


async def _flush_user_usage_with_redis(redis: Redis, user_id: int) -> None:
    """Atomically move one user's pending Redis usage delta into DB and reset counters."""
    usage_key = create_usage_key(user_id=user_id)
    lock_key = f"{usage_key}:flush_lock"

    lock_acquired = await redis.set(lock_key, "1", ex=30, nx=True)
    if not lock_acquired:
        logger.info("Skipping usage flush for user %s due to active lock", user_id)
        return

    try:
        pending_delta = int((await redis.hget(usage_key, "previously_used")) or 0)
        if pending_delta == 0:
            await redis.hset(usage_key, mapping={"previously_used": 0})
            return

        async with get_async_db_session() as session:
            store = UserBillingStore(user_id=user_id, session=session)
            updated_billing = await store.apply_usage_delta(
                user_id=user_id, usage_delta=pending_delta
            )

        async with redis.pipeline(transaction=True) as pipeline:
            pipeline.hset(
                usage_key,
                mapping={
                    "available_tokens": updated_billing.available_tokens,
                    "previously_used": 0,
                },
            )
            pipeline.expire(usage_key, USAGE_CACHE_TTL_SECONDS)
            await pipeline.execute()
    finally:
        await redis.delete(lock_key)


async def listen_for_usage_flush_events() -> None:
    """Continuously consume Redis expiry events and flush matching usage keys."""
    async with get_redis_session() as redis:
        pubsub = redis.pubsub()
        await pubsub.psubscribe(create_expired_events_channel())

        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if not message:
                await asyncio.sleep(0.1)
                continue

            expired_key = message.get("data")
            if isinstance(expired_key, bytes):
                expired_key = expired_key.decode()
            if not isinstance(expired_key, str):
                continue
            try:
                user_id = parse_usage_flush_user_id(expired_key=expired_key)
            except RuntimeError as e:
                logger.critical(str(e))
                os._exit(1)
            if user_id is None:
                continue

            try:
                await _flush_user_usage_with_redis(redis=redis, user_id=user_id)
            except Exception as e:
                logger.critical(f"Failed usage flush for user {user_id}: {e}")
                os._exit(1)


def _crash_on_flush_listener_failure(task: asyncio.Task) -> None:
    """Crash process if background listener exits unexpectedly."""
    if task.cancelled():
        return
    exc = task.exception()
    if exc:
        logger.critical(f"Background usage flush listener crashed: {exc}")
        os._exit(1)


def start_usage_flush_listener(app: FastAPI) -> asyncio.Task:
    """Start listener task and attach crash callback for fail-fast behavior."""
    task = asyncio.create_task(listen_for_usage_flush_events())
    task.add_done_callback(_crash_on_flush_listener_failure)
    app.state.usage_flush_listener_task = task
    logger.info("Started Redis usage flush listener task")
    return task


async def stop_usage_flush_listener(app: FastAPI) -> None:
    """Cancel listener task during app shutdown."""
    task = getattr(app.state, "usage_flush_listener_task", None)
    if not task:
        return

    if task.done() and not task.cancelled():
        exc = task.exception()
        if exc:
            logger.warning(f"Usage flush listener failed before shutdown: {exc}")
            raise exc

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Usage flush listener task cancelled")
