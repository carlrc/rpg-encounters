#!/usr/bin/env python3

from app.clients.redis_client import (
    create_usage_key,
    get_redis_session,
)
from app.data.user_billing_store import UserBillingStore
from app.data.user_store import UserStore
from app.db.connection import get_async_db_session
from app.models.user import UserCreate
from app.models.user_billing import UserBillingCreate
from app.services.redis import flush_user_token_usage
from app.services.user_token import UserTokenService


async def test_user_token_service_cache_and_flush_snapshot():
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

    usage_key = create_usage_key(user_id=user.id)
    token_service = UserTokenService()

    try:
        await token_service.overwrite_cache_from_db(user_id=user.id)
        await token_service.update_token_usage(user_id=user.id, usage_tokens=15)

        async with get_redis_session() as redis:
            usage_hash = await redis.hgetall(
                usage_key
            )  # pyright: ignore[reportGeneralTypeIssues]
        assert int(usage_hash["available_tokens"]) == 85
        assert int(usage_hash["last_used_tokens"]) == 15
        assert int(usage_hash["total_used_tokens"]) == 45

        await flush_user_token_usage(user_id=user.id)

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
            await redis.delete(usage_key)  # pyright: ignore[reportGeneralTypeIssues]
