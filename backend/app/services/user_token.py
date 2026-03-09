import logging
import time

from pydantic import BaseModel
from redis.asyncio import Redis

from app.clients.redis_client import (
    create_usage_key,
    get_redis_session,
)
from app.data.user_billing_store import UserBillingStore
from app.models.user_billing import UserBilling
from app.utils import get_or_throw

logger = logging.getLogger(__name__)

IGNORE_BILLING_BALANCE_CHECK = (
    get_or_throw("BILLING_IGNORE_BALANCE_CHECK").lower() == "true"
)

USAGE_CACHE_TTL_SECONDS = int(get_or_throw("BILLING_CACHE_TTL_SECONDS"))


class TokenUsageCache(BaseModel):
    available_tokens: int
    last_used_tokens: int
    total_used_tokens: int
    updated_at_epoch: int
    synced_at_epoch: int


class UserTokenService:
    async def _get_db_billing(self, user_id: int) -> UserBilling:
        """Load persisted billing row, creating it when missing."""
        try:
            return await UserBillingStore(user_id=user_id).get_or_create(
                user_id=user_id
            )
        except Exception as e:
            logger.error(
                f"UserTokenService get db billing failed for user {user_id}: {e}"
            )
            raise

    async def _usage_hash_exists(
        self, redis: Redis, usage_key: str, user_id: int | None = None
    ) -> bool:
        """Treat hash as ready only when both runtime counters are present."""
        try:
            available_tokens = await redis.hget(
                usage_key, "available_tokens"
            )  # pyright: ignore[reportGeneralTypeIssues]
            last_used_tokens = await redis.hget(
                usage_key, "last_used_tokens"
            )  # pyright: ignore[reportGeneralTypeIssues]
            total_used_tokens = await redis.hget(
                usage_key, "total_used_tokens"
            )  # pyright: ignore[reportGeneralTypeIssues]
            updated_at_epoch = await redis.hget(
                usage_key, "updated_at_epoch"
            )  # pyright: ignore[reportGeneralTypeIssues]
            synced_at_epoch = await redis.hget(
                usage_key, "synced_at_epoch"
            )  # pyright: ignore[reportGeneralTypeIssues]
            return (
                available_tokens is not None
                and last_used_tokens is not None
                and total_used_tokens is not None
                and updated_at_epoch is not None
                and synced_at_epoch is not None
            )
        except Exception as e:
            logger.error(
                f"UserTokenService check usage hash failed for user {user_id}: {e}"
            )
            raise

    async def _write_usage_from_db(self, redis: Redis, user_id: int) -> None:
        """Overwrite Redis counters from DB so runtime starts from source-of-truth."""
        try:
            billing = await self._get_db_billing(user_id=user_id)
            usage_key = create_usage_key(user_id=user_id)
            now = int(time.time())
            usage_cache = TokenUsageCache(
                available_tokens=billing.available_tokens,
                last_used_tokens=billing.last_used_tokens,
                total_used_tokens=billing.total_used_tokens,
                updated_at_epoch=now,
                synced_at_epoch=now,
            )
            await redis.hset(
                usage_key,
                mapping=usage_cache.model_dump(),
            )  # pyright: ignore[reportGeneralTypeIssues]
            await redis.expire(usage_key, USAGE_CACHE_TTL_SECONDS)
        except Exception as e:
            logger.error(
                f"UserTokenService write usage from db failed for user {user_id}: {e}"
            )
            raise

    async def _hydrate_from_db_if_missing(self, redis: Redis, user_id: int) -> None:
        """Lazily hydrate Redis counters when cache is cold or incomplete."""
        try:
            usage_key = create_usage_key(user_id=user_id)
            if await self._usage_hash_exists(
                redis=redis, usage_key=usage_key, user_id=user_id
            ):
                await redis.expire(usage_key, USAGE_CACHE_TTL_SECONDS)
                return
            await self._write_usage_from_db(redis=redis, user_id=user_id)
        except Exception as e:
            logger.error(
                f"UserTokenService hydrate usage cache failed for user {user_id}: {e}"
            )
            raise

    async def overwrite_cache_from_db(self, user_id: int) -> None:
        """Force-refresh Redis counters from DB (used on login)."""
        try:
            async with get_redis_session() as redis:
                await redis.delete(create_usage_key(user_id=user_id))
                await self._write_usage_from_db(redis=redis, user_id=user_id)
        except Exception as e:
            logger.error(
                f"UserTokenService overwrite cache from db failed for user {user_id}: {e}"
            )
            raise

    async def clear_cache(self, user_id: int) -> None:
        """Remove Redis usage key (used on logout)."""
        try:
            async with get_redis_session() as redis:
                await redis.delete(create_usage_key(user_id=user_id))
        except Exception as e:
            logger.error(f"UserTokenService clear cache failed for user {user_id}: {e}")
            raise

    async def get_token_usage_summary(self, user_id: int) -> TokenUsageCache:
        """Return user billing counters from cache, hydrating from DB when missing."""
        try:
            async with get_redis_session() as redis:
                await self._hydrate_from_db_if_missing(redis=redis, user_id=user_id)
                usage_key = create_usage_key(user_id=user_id)
                usage_hash = await redis.hgetall(
                    usage_key
                )  # pyright: ignore[reportGeneralTypeIssues]
                return TokenUsageCache.model_validate(usage_hash)
        except Exception as e:
            logger.error(
                f"UserTokenService get token usage summary failed for user {user_id}: {e}"
            )
            raise

    async def check_token_balance(self, user_id: int) -> bool:
        """Compare available tokens against unflushed usage to allow/block flow entry."""
        # Ignore billing for local development
        if IGNORE_BILLING_BALANCE_CHECK:
            return True

        try:
            async with get_redis_session() as redis:
                await self._hydrate_from_db_if_missing(redis=redis, user_id=user_id)
                usage_key = create_usage_key(user_id=user_id)
                usage_hash = await redis.hgetall(
                    usage_key
                )  # pyright: ignore[reportGeneralTypeIssues]
                usage_cache = TokenUsageCache.model_validate(usage_hash)
                return usage_cache.available_tokens > 0
        except Exception as e:
            logger.error(
                f"UserTokenService check token balance failed for user {user_id}: {e}"
            )
            raise

    async def update_token_usage(self, user_id: int, usage_tokens: int) -> None:
        """Record usage in Redis and rely on periodic/background flush for DB sync."""
        if usage_tokens == 0:
            return

        try:
            now = int(time.time())
            async with get_redis_session() as redis:
                await self._hydrate_from_db_if_missing(redis=redis, user_id=user_id)
                usage_key = create_usage_key(user_id=user_id)

                async with redis.pipeline(transaction=True) as pipeline:
                    pipeline.hincrby(usage_key, "total_used_tokens", usage_tokens)
                    pipeline.hincrby(usage_key, "available_tokens", -usage_tokens)
                    pipeline.hset(
                        usage_key,
                        mapping={
                            "last_used_tokens": usage_tokens,
                            "updated_at_epoch": now,
                        },
                    )
                    pipeline.expire(usage_key, USAGE_CACHE_TTL_SECONDS)
                    await pipeline.execute()
        except Exception as e:
            logger.error(
                f"UserTokenService update token usage failed for user {user_id}: {e}"
            )
            raise
