#!/usr/bin/env python3

from fastapi.testclient import TestClient

from app.main import app
from app.services.user_billing import UserBillingService
from app.services.user_billing_flush import flush_user_usage
from tests.end_to_end.utils import create_authenticated_client


async def test_get_user_billing_summary_returns_owner_summary():
    client, user, _, _ = await create_authenticated_client()

    await UserBillingService().update_token_usage(
        user_id=user.id,
        usage_tokens=40,
    )
    await flush_user_usage(user_id=user.id)

    response = client.get(f"/api/billing/users/{user.id}")
    assert response.status_code == 200

    payload = response.json()
    assert payload["user_id"] == user.id
    assert payload["last_used_tokens"] == 40
    assert payload["total_used_tokens"] == 40
    assert payload["updated_at"] is not None


async def test_get_user_billing_unauthenticated_returns_401():
    client = TestClient(app)
    response = client.get("/api/billing/users/1")
    assert response.status_code == 401


async def test_get_user_billing_for_other_user_returns_403():
    owner_client, owner_user, _, _ = await create_authenticated_client()
    _, other_user, _, _ = await create_authenticated_client()

    response = owner_client.get(f"/api/billing/users/{other_user.id}")
    assert response.status_code == 403
    assert owner_user.id != other_user.id
