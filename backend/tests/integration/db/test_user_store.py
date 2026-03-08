#!/usr/bin/env python3

from app.data.user_store import UserStore
from app.db.connection import get_async_db_session
from app.models.user import UserCreate
from app.utils import get_or_throw


async def test_user_store():
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        new_user_data = UserCreate()
        created_user = await UserStore(session=session).create(new_user_data)
        assert created_user.id is not None
        assert created_user.created_at is not None

        store = UserStore(user_id=created_user.id, session=session)

        all_users = await store.get_all()
        assert len(all_users) >= 1

        retrieved_user = await store.get_by_id(created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.created_at == created_user.created_at

        exists = await store.exists(created_user.id)
        assert exists is True

        deleted = await store.delete()
        assert deleted is True

        exists_after_delete = await UserStore(session=session).exists(created_user.id)
        assert exists_after_delete is False
