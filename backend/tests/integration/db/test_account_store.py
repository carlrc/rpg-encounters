#!/usr/bin/env python3

from app.data.account_store import AccountStore
from app.data.user_store import UserStore
from app.db.connection import get_async_db_session
from app.models.account import AccountCreate, AccountUpdate
from app.models.user import UserCreate
from app.utils import get_or_throw


async def test_account_store():
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        # Create a user first
        user_data = UserCreate()
        created_user = await UserStore(session=session).create(user_data)

        # Create account with user relationship
        account_store = AccountStore(user_id=created_user.id, session=session)
        new_account_data = AccountCreate(
            user_id=created_user.id,
            email="test@example.com",
            token="test-token-123",
            elevenlabs_token="elevenlabs-token-456",
        )

        created_account = await account_store.create(new_account_data)
        assert created_account.id is not None
        assert created_account.user_id == created_user.id
        assert created_account.email == "test@example.com"
        assert created_account.elevenlabs_token == "elevenlabs-token-456"
        assert created_account.created_at is not None

        # Test get by id
        retrieved_account = await account_store.get_by_id(created_account.id)
        assert retrieved_account is not None
        assert retrieved_account.id == created_account.id
        assert retrieved_account.user_id == created_user.id
        assert retrieved_account.email == "test@example.com"

        # Test get by user id (one-to-one relationship)
        account_by_user = await account_store.get_account_by_user_id(created_user.id)
        assert account_by_user is not None
        assert account_by_user.id == created_account.id
        assert account_by_user.user_id == created_user.id

        # Test get all accounts
        all_accounts = await account_store.get_all()
        assert len(all_accounts) >= 1
        assert any(account.id == created_account.id for account in all_accounts)

        # Test update account
        update_data = AccountUpdate(email="updated@example.com")
        updated_account = await account_store.update(created_account.id, update_data)
        assert updated_account is not None
        assert updated_account.email == "updated@example.com"
        assert updated_account.elevenlabs_token == "elevenlabs-token-456"  # unchanged

        # Test account exists
        exists = await account_store.exists(created_account.id)
        assert exists is True

        # Test delete account
        deleted = await account_store.delete(created_account.id)
        assert deleted is True

        # Test account no longer exists
        exists_after_delete = await account_store.exists(created_account.id)
        assert exists_after_delete is False

        # Cleanup user
        await UserStore(user_id=created_user.id, session=session).delete()
