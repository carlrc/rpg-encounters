#!/usr/bin/env python3

from datetime import datetime, timedelta, timezone

import pytest

from app.data.account_store import AccountStore
from app.data.magic_link_store import (
    DeviceMismatchError,
    MagicLinkStore,
    TokenAlreadyUsedError,
    TokenExpiredError,
    TokenNotFoundError,
)
from app.data.user_store import UserStore
from app.db.connection import get_async_db_session
from app.models.account import AccountCreate
from app.models.magic_link import MagicLinkCreate
from app.models.user import UserCreate
from app.utils import get_or_throw


async def test_magic_link_create_and_retrieve():
    """Test creating a magic link and verifying its properties"""
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        # Create user
        user_store = UserStore(session=session)
        user = await user_store.create(UserCreate())

        # Create account
        account_store = AccountStore(user_id=user.id, session=session)
        await account_store.create(
            AccountCreate(user_id=user.id, email="test@example.com")
        )

        # Create magic link
        magic_link_store = MagicLinkStore(session=session)
        device_nonce = MagicLinkStore.generate_token()
        raw_token = MagicLinkStore.generate_token()

        magic_link_data = MagicLinkCreate(
            user_id=user.id,
            token_hash=MagicLinkStore.hash_token(raw_token),
            device_nonce_hash=MagicLinkStore.hash_token(device_nonce),
            expires_at=MagicLinkStore.magic_link_expiry(),
            used=False,
        )

        magic_link = await magic_link_store.create(magic_link_data)

        # Verify link properties
        assert magic_link.user_id == user.id
        assert magic_link.token_hash == MagicLinkStore.hash_token(raw_token)
        assert magic_link.device_nonce_hash == MagicLinkStore.hash_token(device_nonce)
        assert magic_link.used is False
        assert magic_link.expires_at > datetime.now(timezone.utc)
        assert magic_link.id is not None
        assert magic_link.created_at is not None


async def test_magic_link_consume_success():
    """Test successfully consuming a magic link"""
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        # Create user and account
        user_store = UserStore(session=session)
        user = await user_store.create(UserCreate())

        account_store = AccountStore(user_id=user.id, session=session)
        await account_store.create(
            AccountCreate(user_id=user.id, email="test@example.com")
        )

        # Create magic link
        magic_link_store = MagicLinkStore(session=session)
        device_nonce = MagicLinkStore.generate_token()
        raw_token = MagicLinkStore.generate_token()

        magic_link_data = MagicLinkCreate(
            user_id=user.id,
            token_hash=MagicLinkStore.hash_token(raw_token),
            device_nonce_hash=MagicLinkStore.hash_token(device_nonce),
            expires_at=MagicLinkStore.magic_link_expiry(),
            used=False,
        )

        created_link = await magic_link_store.create(magic_link_data)

        # Consume the magic link
        consumed_link = await magic_link_store.consume(
            token_hash=MagicLinkStore.hash_token(raw_token),
            device_nonce_hash=MagicLinkStore.hash_token(device_nonce),
        )

        # Verify consumption
        assert consumed_link.id == created_link.id
        assert consumed_link.user_id == user.id
        assert consumed_link.used is True
        assert consumed_link.used_at is not None
        assert consumed_link.used_at > created_link.created_at


async def test_magic_link_consume_wrong_device():
    """Test consuming with wrong device nonce"""
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        # Create user and account
        user_store = UserStore(session=session)
        user = await user_store.create(UserCreate())

        account_store = AccountStore(user_id=user.id, session=session)
        await account_store.create(
            AccountCreate(user_id=user.id, email="test@example.com")
        )

        # Create magic link
        magic_link_store = MagicLinkStore(session=session)
        device_nonce = MagicLinkStore.generate_token()
        raw_token = MagicLinkStore.generate_token()

        magic_link_data = MagicLinkCreate(
            user_id=user.id,
            token_hash=MagicLinkStore.hash_token(raw_token),
            device_nonce_hash=MagicLinkStore.hash_token(device_nonce),
            expires_at=MagicLinkStore.magic_link_expiry(),
            used=False,
        )

        await magic_link_store.create(magic_link_data)

        # Try to consume with wrong device nonce
        wrong_device_nonce = MagicLinkStore.generate_token()
        with pytest.raises(DeviceMismatchError):
            await magic_link_store.consume(
                token_hash=MagicLinkStore.hash_token(raw_token),
                device_nonce_hash=MagicLinkStore.hash_token(wrong_device_nonce),
            )


async def test_magic_link_consume_expired():
    """Test consuming an expired magic link"""
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        # Create user and account
        user_store = UserStore(session=session)
        user = await user_store.create(UserCreate())

        account_store = AccountStore(user_id=user.id, session=session)
        await account_store.create(
            AccountCreate(user_id=user.id, email="test@example.com")
        )

        # Create expired magic link
        magic_link_store = MagicLinkStore(session=session)
        device_nonce = MagicLinkStore.generate_token()
        raw_token = MagicLinkStore.generate_token()

        expired_time = datetime.now(timezone.utc) - timedelta(hours=1)
        magic_link_data = MagicLinkCreate(
            user_id=user.id,
            token_hash=MagicLinkStore.hash_token(raw_token),
            device_nonce_hash=MagicLinkStore.hash_token(device_nonce),
            expires_at=expired_time,
            used=False,
        )

        await magic_link_store.create(magic_link_data)

        # Try to consume expired link
        with pytest.raises(TokenExpiredError):
            await magic_link_store.consume(
                token_hash=MagicLinkStore.hash_token(raw_token),
                device_nonce_hash=MagicLinkStore.hash_token(device_nonce),
            )


async def test_magic_link_consume_already_used():
    """Test consuming an already used magic link"""
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        # Create user and account
        user_store = UserStore(session=session)
        user = await user_store.create(UserCreate())

        account_store = AccountStore(user_id=user.id, session=session)
        await account_store.create(
            AccountCreate(user_id=user.id, email="test@example.com")
        )

        # Create magic link
        magic_link_store = MagicLinkStore(session=session)
        device_nonce = MagicLinkStore.generate_token()
        raw_token = MagicLinkStore.generate_token()

        magic_link_data = MagicLinkCreate(
            user_id=user.id,
            token_hash=MagicLinkStore.hash_token(raw_token),
            device_nonce_hash=MagicLinkStore.hash_token(device_nonce),
            expires_at=MagicLinkStore.magic_link_expiry(),
            used=False,
        )

        await magic_link_store.create(magic_link_data)

        # Consume the link once
        await magic_link_store.consume(
            token_hash=MagicLinkStore.hash_token(raw_token),
            device_nonce_hash=MagicLinkStore.hash_token(device_nonce),
        )

        # Try to consume again
        with pytest.raises(TokenAlreadyUsedError):
            await magic_link_store.consume(
                token_hash=MagicLinkStore.hash_token(raw_token),
                device_nonce_hash=MagicLinkStore.hash_token(device_nonce),
            )


async def test_magic_link_consume_not_found():
    """Test consuming with non-existent token"""
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        magic_link_store = MagicLinkStore(session=session)

        # Try to consume non-existent token
        fake_token = MagicLinkStore.generate_token()
        fake_device_nonce = MagicLinkStore.generate_token()

        with pytest.raises(TokenNotFoundError):
            await magic_link_store.consume(
                token_hash=MagicLinkStore.hash_token(fake_token),
                device_nonce_hash=MagicLinkStore.hash_token(fake_device_nonce),
            )


async def test_multiple_magic_links_per_user():
    """Test creating multiple magic links for the same user"""
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        # Create user and account
        user_store = UserStore(session=session)
        user = await user_store.create(UserCreate())

        account_store = AccountStore(user_id=user.id, session=session)
        await account_store.create(
            AccountCreate(user_id=user.id, email="test@example.com")
        )

        # Create multiple magic links
        magic_link_store = MagicLinkStore(session=session)
        links = []

        for _ in range(3):
            device_nonce = MagicLinkStore.generate_token()
            raw_token = MagicLinkStore.generate_token()

            magic_link_data = MagicLinkCreate(
                user_id=user.id,
                token_hash=MagicLinkStore.hash_token(raw_token),
                device_nonce_hash=MagicLinkStore.hash_token(device_nonce),
                expires_at=MagicLinkStore.magic_link_expiry(),
                used=False,
            )

            link = await magic_link_store.create(magic_link_data)
            links.append((link, raw_token, device_nonce))

        # Verify all links exist and are independent
        assert len(links) == 3
        for link, raw_token, device_nonce in links:
            assert link.user_id == user.id
            assert link.used is False

        # Consume one link
        first_link, first_token, first_device = links[0]
        consumed = await magic_link_store.consume(
            token_hash=MagicLinkStore.hash_token(first_token),
            device_nonce_hash=MagicLinkStore.hash_token(first_device),
        )

        assert consumed.id == first_link.id
        assert consumed.used is True

        # Verify other links are still unused
        second_link, second_token, second_device = links[1]
        still_valid = await magic_link_store.consume(
            token_hash=MagicLinkStore.hash_token(second_token),
            device_nonce_hash=MagicLinkStore.hash_token(second_device),
        )

        assert still_valid.id == second_link.id
        assert still_valid.used is True
