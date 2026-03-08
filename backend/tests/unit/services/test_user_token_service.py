from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.clients.redis_client import create_usage_key
from app.services.user_token import UserTokenService


def make_usage_hash(available_tokens: int) -> dict[str, str]:
    return {
        "available_tokens": str(available_tokens),
        "last_used_tokens": "12",
        "total_used_tokens": "240",
        "updated_at_epoch": "1730000000",
        "synced_at_epoch": "1729999940",
    }


def build_redis_session(usage_hash: dict[str, str]):
    redis = SimpleNamespace(
        hget=AsyncMock(side_effect=lambda _usage_key, field: usage_hash.get(field)),
        hgetall=AsyncMock(return_value=dict(usage_hash)),
        expire=AsyncMock(return_value=True),
    )

    @asynccontextmanager
    async def session():
        yield redis

    return session, redis


@pytest.mark.asyncio
async def test_check_token_balance_true_when_available_tokens_above_zero(monkeypatch):
    usage_key = create_usage_key(user_id=77)
    usage_hash = make_usage_hash(available_tokens=30)
    service = UserTokenService()
    redis_session, redis = build_redis_session(usage_hash=usage_hash)
    hydrate_mock = AsyncMock()
    service._hydrate_from_db_if_missing = hydrate_mock

    # monkeypatch temporarily replaces module attributes during this test only.
    monkeypatch.setattr("app.services.user_token.IGNORE_BILLING_BALANCE_CHECK", False)
    monkeypatch.setattr("app.services.user_token.get_redis_session", redis_session)

    result = await service.check_token_balance(user_id=77)

    assert result is True
    hydrate_mock.assert_awaited_once_with(redis=redis, user_id=77)
    redis.hgetall.assert_awaited_once_with(usage_key)


@pytest.mark.asyncio
async def test_check_token_balance_false_when_available_tokens_is_zero(monkeypatch):
    usage_hash = make_usage_hash(available_tokens=0)
    service = UserTokenService()
    redis_session, redis = build_redis_session(usage_hash=usage_hash)
    hydrate_mock = AsyncMock()
    service._hydrate_from_db_if_missing = hydrate_mock

    # monkeypatch temporarily replaces module attributes during this test only.
    monkeypatch.setattr("app.services.user_token.IGNORE_BILLING_BALANCE_CHECK", False)
    monkeypatch.setattr("app.services.user_token.get_redis_session", redis_session)

    result = await service.check_token_balance(user_id=77)

    assert result is False
    hydrate_mock.assert_awaited_once_with(redis=redis, user_id=77)
