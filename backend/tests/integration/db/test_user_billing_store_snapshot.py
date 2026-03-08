#!/usr/bin/env python3

from app.data.user_billing_store import UserBillingStore
from app.data.user_store import UserStore
from app.db.connection import get_async_db_session
from app.models.user import UserCreate
from app.models.user_billing import UserBillingCreate, UserBillingUpdate
from app.utils import get_or_throw


async def test_apply_token_usage_snapshot_persists_token_fields():
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        user = await UserStore(session=session).create(UserCreate())
        store = UserBillingStore(user_id=user.id, session=session)
        await store.create(
            UserBillingCreate(
                user_id=user.id,
                available_tokens=100,
                last_used_tokens=0,
                total_used_tokens=10,
            )
        )

        updated = await store.apply_token_usage_snapshot(
            user_id=user.id,
            token_usage_update=UserBillingUpdate(
                available_tokens=82,
                last_used_tokens=18,
                total_used_tokens=28,
            ),
        )

        assert updated.available_tokens == 82
        assert updated.last_used_tokens == 18
        assert updated.total_used_tokens == 28
