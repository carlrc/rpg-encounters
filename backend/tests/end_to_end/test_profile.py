#!/usr/bin/env python3

from fastapi.testclient import TestClient

from app.main import app
from app.services.user_token import UserTokenService
from app.services.user_token_flush import flush_user_token_usage
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
    assert payload["updated_at"] is not None


async def test_get_profile_unauthenticated_returns_401():
    client = TestClient(app)
    response = client.get("/api/profile")
    assert response.status_code == 401
