#!/usr/bin/env python3
from app.data.user_store import UserStore
from app.models.user import UserCreate


def test_user_store():

    new_user_data = UserCreate()
    created_user = UserStore().create_user(new_user_data)
    assert created_user.id is not None
    assert created_user.created_at is not None

    store = UserStore(user_id=created_user.id)

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

    exists_after_delete = UserStore().user_exists(created_user.id)
    assert exists_after_delete is False
