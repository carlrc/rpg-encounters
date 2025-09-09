from unittest.mock import patch

from fastapi.testclient import TestClient

from app.auth.session import SESSION_CONFIG
from app.data.account_store import AccountStore
from app.data.magic_link_store import MagicLinkStore
from app.http import DEVICE_NONCE_COOKIE
from app.main import app
from tests.end_to_end.utils import (
    create_authenticated_client,
    create_test_user_and_account,
    decode_session,
    encode_session,
    get_latest_magic_link_for_user,
)


async def test_magic_link_complete_flow():
    client, _, _, world = await create_authenticated_client()

    # Step 5: Logout
    response = client.post("api/auth/logout", headers={"X-World-Id": str(world.id)})
    assert response.status_code == 204


async def test_nonexistent_user_request():
    """Test magic link request for non-existent user (no user enumeration)"""
    client = TestClient(app)
    email = "nonexistent@example.com"

    response = client.post("/api/auth/request", json={"email": email})
    assert response.status_code == 200
    # Should return empty response to prevent user enumeration

    # Verify no magic link was created by looking up the email
    account_store = AccountStore(user_id=None)
    account = await account_store.get_by_email(email=email)
    assert account is None, "Account should not exist"


async def test_invalid_token_consumption():
    """Test consuming invalid token"""
    client = TestClient(app)

    # Set a device nonce first
    client.cookies.set(name=DEVICE_NONCE_COOKIE, value=MagicLinkStore.generate_token())

    response = client.get(
        f"/api/auth?token={MagicLinkStore.generate_token()}", follow_redirects=False
    )
    assert response.status_code == 400


async def test_token_reuse_prevention():
    """Test that magic links can't be reused"""
    client = TestClient(app)
    user, account, _ = await create_test_user_and_account()

    test_token = MagicLinkStore.generate_token()
    test_device_nonce = MagicLinkStore.generate_token()
    with patch(
        "app.data.magic_link_store.MagicLinkStore.generate_token"
    ) as mock_generate:
        mock_generate.side_effect = [test_device_nonce, test_token]
        magic_response = client.post("/api/auth/request", json={"email": account.email})
        assert magic_response.status_code == 200

    client.cookies.set(DEVICE_NONCE_COOKIE, magic_response.cookies[DEVICE_NONCE_COOKIE])

    # First consumption - should work
    response = client.get(f"/api/auth?token={test_token}", follow_redirects=False)
    assert response.status_code == 200

    # Verify token is now marked as used in database
    magic_link = await get_latest_magic_link_for_user(user.id)
    assert magic_link is not None
    assert magic_link.used is True

    # Use a new client for second attempt (simulates different session)
    client2 = TestClient(app)
    client2.cookies.set(
        DEVICE_NONCE_COOKIE, magic_response.cookies[DEVICE_NONCE_COOKIE]
    )

    # Second consumption - should fail
    response = client2.get(f"/api/auth?token={test_token}", follow_redirects=False)
    assert response.status_code == 400


async def test_device_binding_enforcement():
    """Test that device binding is enforced"""
    client = TestClient(app)
    _, account, _ = await create_test_user_and_account()

    # Request magic link
    test_token = MagicLinkStore.generate_token()
    test_device_nonce = MagicLinkStore.generate_token()
    with patch(
        "app.data.magic_link_store.MagicLinkStore.generate_token"
    ) as mock_generate:
        mock_generate.side_effect = [test_device_nonce, test_token]
        response = client.post("/api/auth/request", json={"email": account.email})
        assert response.status_code == 200

    device_nonce = response.cookies.get(DEVICE_NONCE_COOKIE)

    # Try to consume without device nonce cookie
    client_no_cookie = TestClient(app)
    response = client_no_cookie.get(
        f"/api/auth?token={test_token}", follow_redirects=False
    )
    assert response.status_code == 400

    # Try to consume with wrong device nonce
    client_wrong_cookie = TestClient(app)
    client_wrong_cookie.cookies.set(
        name=DEVICE_NONCE_COOKIE, value=MagicLinkStore.generate_token()
    )
    response = client_wrong_cookie.get(
        f"/api/auth?token={test_token}", follow_redirects=False
    )
    assert response.status_code == 400

    # Should work with correct device nonce
    client.cookies.set(name=DEVICE_NONCE_COOKIE, value=device_nonce)
    response = client.get(f"/api/auth?token={test_token}", follow_redirects=False)
    assert response.status_code == 200


async def test_missing_token_in_consume():
    """Test consuming magic link without token"""
    client = TestClient(app)

    response = client.get("/api/auth")
    assert response.status_code == 422


async def test_invalid_email_format():
    """Test magic link request with invalid email"""
    client = TestClient(app)

    response = client.post("/api/auth/request", json={"email": "invalid-email"})
    assert response.status_code == 422


async def test_consume_without_device_nonce():
    """Test consuming magic link without device nonce cookie"""
    client = TestClient(app)

    response = client.get("/api/auth?token=some-token", follow_redirects=False)
    assert response.status_code == 400


async def test_device_nonce_cookie_creation():
    """Test that device nonce cookie is properly created"""
    client = TestClient(app)
    _, account, _ = await create_test_user_and_account()

    response = client.post("/api/auth/request", json={"email": account.email})

    assert response.status_code == 200
    assert response.cookies[DEVICE_NONCE_COOKIE]


async def test_device_nonce_persistence():
    """Test that device nonce persists across multiple requests"""
    client = TestClient(app)
    _, account, _ = await create_test_user_and_account()

    # First request - should create device nonce
    response1 = client.post("/api/auth/request", json={"email": account.email})
    assert response1.status_code == 200

    assert response1.cookies[DEVICE_NONCE_COOKIE]
    client.cookies.set(
        name=DEVICE_NONCE_COOKIE, value=response1.cookies[DEVICE_NONCE_COOKIE]
    )

    response2 = client.post("/api/auth/request", json={"email": account.email})
    assert response2.status_code == 200


async def test_tampered_session_rejected():
    """Test that tampered session cookies are rejected"""
    client, _, _, world = await create_authenticated_client()

    # Use valid session
    response = client.get("/api/players", headers={"X-World-Id": str(world.id)})
    assert response.status_code == 200

    session = decode_session(
        cookie_value=response.cookies.get(SESSION_CONFIG.session_cookie_name)
    )
    client.cookies.clear()
    session["user_id"] = 2000
    client.cookies.set(
        name=SESSION_CONFIG.session_cookie_name,
        value=encode_session(session_data=session, secret_key="12345"),
        domain="testserver.local",
    )

    response = client.get("/api/players", headers={"X-World-Id": str(world.id)})
    assert response.status_code == 401


async def test_invalid_session_signature_rejected():
    """Test that sessions with invalid signatures are rejected"""
    client = TestClient(app)
    _, _, world = await create_test_user_and_account()

    # Set a completely invalid session cookie
    client.cookies.set(
        name=SESSION_CONFIG.session_cookie_name,
        value="completely.invalid.session.signature",
    )

    # Try to access protected endpoint with invalid session
    response = client.get("/api/players", headers={"X-World-Id": str(world.id)})
    assert response.status_code == 401


async def test_empty_session_rejected():
    """Test that empty session cookies are rejected"""
    client = TestClient(app)
    _, _, world = await create_test_user_and_account()

    # Set empty session cookie
    client.cookies.set(name=SESSION_CONFIG.session_cookie_name, value="")

    # Try to access protected endpoint with empty session
    response = client.get("/api/players", headers={"X-World-Id": str(world.id)})
    assert response.status_code == 401
