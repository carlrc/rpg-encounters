#!/usr/bin/env python3

import time

from app.clients.redis_client import create_usage_key, get_redis_session
from app.data.user_billing_store import UserBillingStore
from app.data.user_store import UserStore
from app.db.connection import get_async_db_session
from app.models.user import UserCreate
from app.models.user_billing import UserBillingCreate
from app.services.redis import (
    USAGE_FLUSH_INTERVAL_SECONDS,
    _sync_pending_token_usage,
)
from app.services.user_token import UserTokenService


async def test_token_usage_sync_poller_flushes_due_usage():
    async with get_async_db_session() as session:
        user = await UserStore(session=session).create(UserCreate())
        billing_store = UserBillingStore(user_id=user.id, session=session)
        await billing_store.create(
            UserBillingCreate(
                user_id=user.id,
                available_tokens=100,
                last_used_tokens=5,
                total_used_tokens=30,
            )
        )

    token_service = UserTokenService()
    usage_key = create_usage_key(user_id=user.id)

    try:
        async with get_redis_session() as redis:
            async for key in redis.scan_iter(match="billing:user:*"):
                await redis.delete(key)  # pyright: ignore[reportGeneralTypeIssues]

        await token_service.overwrite_cache_from_db(user_id=user.id)
        await token_service.update_token_usage(user_id=user.id, usage_tokens=15)

        stale_synced_at = int(time.time()) - USAGE_FLUSH_INTERVAL_SECONDS - 1
        async with get_redis_session() as redis:
            await redis.hset(  # pyright: ignore[reportGeneralTypeIssues]
                usage_key,
                mapping={"synced_at_epoch": stale_synced_at},
            )

        await _sync_pending_token_usage()

        async with get_async_db_session() as session:
            updated = await UserBillingStore(
                user_id=user.id, session=session
            ).get_by_user_id(user.id)
            assert updated is not None
            assert updated.available_tokens == 85
            assert updated.last_used_tokens == 15
            assert updated.total_used_tokens == 45
    finally:
        async with get_redis_session() as redis:
            async for key in redis.scan_iter(match="billing:user:*"):
                await redis.delete(key)  # pyright: ignore[reportGeneralTypeIssues]
