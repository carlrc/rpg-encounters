#!/usr/bin/env python3

from fastapi.testclient import TestClient

from app.clients.redis_client import create_usage_key, get_redis_session
from app.data.account_store import AccountStore
from app.data.user_billing_store import UserBillingStore
from app.data.user_store import UserStore
from app.data.world_store import WorldStore
from app.main import app
from app.models.user_billing import UserBillingUpdate
from app.services.redis import flush_user_token_usage
from app.services.user_token import UserTokenService
from tests.end_to_end.utils import create_authenticated_client


async def test_get_profile_returns_token_summary_for_authenticated_user():
    client, user, _, _ = await create_authenticated_client()

    await UserTokenService().update_token_usage(
        user_id=user.id,
        usage_tokens=40,
    )
    await flush_user_token_usage(user_id=user.id)

    response = client.get("/api/profile")
    assert response.status_code == 200

    payload = response.json()
    assert payload["user_id"] == user.id
    assert payload["last_used_tokens"] == 40
    assert payload["total_used_tokens"] == 40


async def test_get_profile_unauthenticated_returns_401():
    client = TestClient(app)
    response = client.get("/api/profile")
    assert response.status_code == 401


async def test_get_profile_hydrates_cache_when_missing():
    client, user, _, _ = await create_authenticated_client()

    async with get_redis_session() as redis:
        await redis.delete(
            create_usage_key(user_id=user.id)
        )  # pyright: ignore[reportGeneralTypeIssues]

    response = client.get("/api/profile")
    assert response.status_code == 200
    payload = response.json()
    assert payload["user_id"] == user.id
    assert "available_tokens" in payload
    assert "last_used_tokens" in payload
    assert "total_used_tokens" in payload


async def test_get_profile_reads_cache_when_cache_and_db_differ():
    client, user, _, _ = await create_authenticated_client()
    usage_key = create_usage_key(user_id=user.id)

    await UserBillingStore(user_id=user.id).update_by_user_id(
        user_id=user.id,
        user_billing_update=UserBillingUpdate(
            available_tokens=999,
            last_used_tokens=111,
            total_used_tokens=222,
        ),
    )

    async with get_redis_session() as redis:
        await redis.hset(  # pyright: ignore[reportGeneralTypeIssues]
            usage_key,
            mapping={
                "available_tokens": 7,
                "last_used_tokens": 3,
                "total_used_tokens": 19,
                "updated_at_epoch": 2000000000,
                "synced_at_epoch": 1999999900,
            },
        )

    response = client.get("/api/profile")
    assert response.status_code == 200
    payload = response.json()
    assert payload["user_id"] == user.id
    assert payload["available_tokens"] == 7
    assert payload["last_used_tokens"] == 3
    assert payload["total_used_tokens"] == 19


async def test_delete_profile_deletes_user_and_related_records():
    client, user, account, world = await create_authenticated_client()
    usage_key = create_usage_key(user_id=user.id)

    await UserBillingStore(user_id=user.id).get_or_create(user_id=user.id)
    async with get_redis_session() as redis:
        await redis.hset(  # pyright: ignore[reportGeneralTypeIssues]
            usage_key,
            mapping={
                "available_tokens": 10,
                "last_used_tokens": 2,
                "total_used_tokens": 20,
                "updated_at_epoch": 2000000000,
                "synced_at_epoch": 1999999900,
            },
        )

    response = client.delete("/api/profile", headers={"X-World-Id": str(world.id)})
    assert response.status_code == 204

    assert not await UserStore().exists(user.id)
    assert await AccountStore(user_id=None).get_by_id(account.id) is None
    assert await WorldStore(user_id=user.id).get_by_id(world.id) is None
    assert await UserBillingStore(user_id=user.id).get_by_user_id(user.id) is None

    async with get_redis_session() as redis:
        cached = await redis.exists(
            usage_key
        )  # pyright: ignore[reportGeneralTypeIssues]
    assert cached == 0
