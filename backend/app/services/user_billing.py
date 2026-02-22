import time

from app.clients.redis_client import (
    create_usage_flush_key,
    create_usage_key,
    get_redis_session,
)
from app.data.user_billing_store import UserBillingStore
from app.models.user_billing import UserBilling
from app.utils import get_or_throw

IGNORE_BILLING_BALANCE_CHECK = (
    get_or_throw("BILLING_IGNORE_BALANCE_CHECK").lower() == "true"
)

USAGE_CACHE_TTL_SECONDS = int(get_or_throw("BILLING_CACHE_TTL_SECONDS"))
USAGE_FLUSH_INTERVAL_SECONDS = int(get_or_throw("BILLING_FLUSH_INTERVAL_SECONDS"))


class UserBillingService:
    async def _get_db_billing(self, user_id: int) -> UserBilling:
        """Load persisted billing row, creating it when missing."""
        return await UserBillingStore(user_id=user_id).get_or_create(user_id=user_id)

    async def _usage_hash_exists(self, redis, usage_key: str) -> bool:
        """Treat hash as ready only when both runtime counters are present."""
        available_tokens = await redis.hget(usage_key, "available_tokens")
        previously_used = await redis.hget(usage_key, "previously_used")
        return available_tokens is not None and previously_used is not None

    async def _write_usage_from_db(self, redis, user_id: int) -> None:
        """Overwrite Redis counters from DB so runtime starts from source-of-truth."""
        billing = await self._get_db_billing(user_id=user_id)
        usage_key = create_usage_key(user_id=user_id)
        await redis.hset(
            usage_key,
            mapping={
                "available_tokens": billing.available_tokens,
                "previously_used": 0,
                "updated_at_epoch": int(time.time()),
            },
        )
        await redis.expire(usage_key, USAGE_CACHE_TTL_SECONDS)

    async def _hydrate_from_db_if_missing(self, redis, user_id: int) -> None:
        """Lazily hydrate Redis counters when cache is cold or incomplete."""
        usage_key = create_usage_key(user_id=user_id)
        if await self._usage_hash_exists(redis=redis, usage_key=usage_key):
            await redis.expire(usage_key, USAGE_CACHE_TTL_SECONDS)
            return
        await self._write_usage_from_db(redis=redis, user_id=user_id)

    async def overwrite_cache_from_db(self, user_id: int) -> None:
        """Force-refresh Redis counters from DB (used on login)."""
        async with get_redis_session() as redis:
            await self._write_usage_from_db(redis=redis, user_id=user_id)

    async def clear_cache(self, user_id: int) -> None:
        """Remove Redis usage/flush keys (used on logout)."""
        async with get_redis_session() as redis:
            await redis.delete(
                create_usage_key(user_id=user_id),
                create_usage_flush_key(user_id=user_id),
            )

    async def check_token_balance(self, user_id: int) -> bool:
        """Compare available tokens against unflushed usage to allow/block flow entry."""
        # Local dev escape hatch to bypass balance checks when explicitly enabled.
        if IGNORE_BILLING_BALANCE_CHECK:
            return True

        async with get_redis_session() as redis:
            await self._hydrate_from_db_if_missing(redis=redis, user_id=user_id)
            usage_key = create_usage_key(user_id=user_id)
            available_tokens = int(
                (await redis.hget(usage_key, "available_tokens")) or 0
            )
            previously_used = int((await redis.hget(usage_key, "previously_used")) or 0)
            return available_tokens > previously_used

    async def update_token_usage(self, user_id: int, usage_tokens: int) -> None:
        """Record usage in Redis and schedule async DB flush via expiry key."""
        if usage_tokens == 0:
            return

        now = int(time.time())
        async with get_redis_session() as redis:
            await self._hydrate_from_db_if_missing(redis=redis, user_id=user_id)
            usage_key = create_usage_key(user_id=user_id)
            flush_key = create_usage_flush_key(user_id=user_id)

            async with redis.pipeline(transaction=True) as pipeline:
                pipeline.hincrby(usage_key, "previously_used", usage_tokens)
                pipeline.hset(
                    usage_key,
                    mapping={"updated_at_epoch": now},
                )
                pipeline.expire(usage_key, USAGE_CACHE_TTL_SECONDS)
                pipeline.set(flush_key, "1", ex=USAGE_FLUSH_INTERVAL_SECONDS)
                await pipeline.execute()
