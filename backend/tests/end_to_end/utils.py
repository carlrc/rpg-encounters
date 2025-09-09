#!/usr/bin/env python3
import base64
import json
import uuid

from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner
from sqlalchemy import select

from app.auth.session import SESSION_CONFIG
from app.data.account_store import AccountStore
from app.data.magic_link_store import MagicLinkStore
from app.data.user_store import UserStore
from app.data.world_store import WorldStore
from app.db.models.magic_link import MagicLinkORM
from app.http import DEVICE_NONCE_COOKIE
from app.main import app
from app.models.account import AccountCreate
from app.models.magic_link import MagicLink, MagicLinkCreate
from app.models.user import UserCreate


async def create_test_user_and_account():
    """Create a test user, account, and world for testing"""
    # Create user
    user_store = UserStore()
    user = await user_store.create(UserCreate())

    # Create account with unique email for each test
    unique_email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    account_store = AccountStore(user_id=user.id)
    account = await account_store.create(
        AccountCreate(user_id=user.id, email=unique_email)
    )

    # Create world
    world_store = WorldStore(user_id=user.id)
    world = await world_store.create()

    return user, account, world


def encode_session(
    session_data: dict[str, int], secret_key: str = SESSION_CONFIG.secret_key
) -> str:
    signer = TimestampSigner(secret_key=secret_key)
    raw = base64.b64encode(json.dumps(session_data).encode("utf-8"))
    signed = signer.sign(raw)
    return signed.decode("utf-8")


def decode_session(
    cookie_value: str, secret_key: str = SESSION_CONFIG.secret_key
) -> dict[str, int]:
    signer = TimestampSigner(secret_key=secret_key)
    raw = signer.unsign(cookie_value.encode("utf-8"), max_age=SESSION_CONFIG.max_age)
    return json.loads(base64.b64decode(raw))


async def create_authenticated_client():
    """Create an authenticated TestClient with session and world"""
    client = TestClient(app)
    user, account, world = await create_test_user_and_account()

    # Circumvent /request endpoint such that we have the raw token for use at login (e.g., don't need to wait for email)
    test_token = MagicLinkStore.generate_token()
    test_device_nonce = MagicLinkStore.generate_token()

    # Create magic link directly in database with known token
    magic_link_store = MagicLinkStore()
    magic_link_data = MagicLinkCreate(
        user_id=user.id,
        token_hash=MagicLinkStore.hash_token(test_token),
        device_nonce_hash=MagicLinkStore.hash_token(test_device_nonce),
        expires_at=MagicLinkStore.magic_link_expiry(),
        used=False,
    )
    await magic_link_store.create(magic_link_data)

    # Set device nonce cookie
    client.cookies.set(DEVICE_NONCE_COOKIE, test_device_nonce)

    # Consume magic link to create session
    response = client.get(f"/api/auth?token={test_token}", follow_redirects=False)
    assert response.status_code == 302

    # Get session token from cookies
    session = client.cookies.get(SESSION_CONFIG.session_cookie_name)
    assert session

    decoded_session = decode_session(cookie_value=session)
    assert decoded_session["user_id"]

    return client, user, account, world


async def get_magic_link_by_token_hash_for_testing(token_hash: str) -> MagicLink | None:
    """Get magic link by token hash - FOR TESTING ONLY"""
    magic_link_store = MagicLinkStore()
    async with magic_link_store.get_session() as session:
        result = await session.execute(
            select(MagicLinkORM).where(MagicLinkORM.token_hash == token_hash)
        )
        magic_link = result.scalar_one_or_none()
        return MagicLink.model_validate(magic_link) if magic_link else None


async def get_latest_magic_link_for_user(user_id: int) -> MagicLink | None:
    """Get the most recent magic link for a user - FOR TESTING ONLY"""
    magic_link_store = MagicLinkStore()
    async with magic_link_store.get_session() as session:
        result = await session.execute(
            select(MagicLinkORM)
            .where(MagicLinkORM.user_id == user_id)
            .order_by(MagicLinkORM.created_at.desc())
            .limit(1)
        )
        magic_link = result.scalar_one_or_none()
        return MagicLink.model_validate(magic_link) if magic_link else None
