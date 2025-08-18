#!/usr/bin/env python3
import os

from sqlalchemy import create_engine

from app.data.user_store import UserStore
from app.models.user import UserCreate


def test_user_store():
    url = os.getenv("TEST_DATABASE_URL")
    engine = create_engine(url)
    new_user_data = UserCreate()
    created_user = UserStore(engine=engine).create_user(new_user_data)
    assert created_user.id is not None
    assert created_user.created_at is not None

    store = UserStore(user_id=created_user.id, engine=engine)

    all_users = store.get_all_users()
    assert len(all_users) >= 1

    retrieved_user = store.get_user_by_id(created_user.id)
    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.created_at == created_user.created_at

    exists = store.user_exists(created_user.id)
    assert exists is True

    deleted = store.delete_user()
    assert deleted is True

    exists_after_delete = UserStore(engine=engine).user_exists(created_user.id)
    assert exists_after_delete is False
