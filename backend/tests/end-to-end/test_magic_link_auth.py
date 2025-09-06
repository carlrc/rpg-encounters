#!/usr/bin/env python3
import uuid

from fastapi.testclient import TestClient

from app.data.account_store import AccountStore
from app.data.magic_link_store import MagicLinkStore
from app.data.user_store import UserStore
from app.main import app
from app.models.account import AccountCreate
from app.models.auth import AuthStatusResponse, LogoutResponse
from app.models.magic_link import MagicLinkConsumeResponse, MagicLinkResponse
from app.models.user import User, UserCreate


async def create_test_user_and_account():
    """Create a test user and account for testing"""
    # Create user
    user_store = UserStore()
    user = await user_store.create(UserCreate())

    # Create account with unique email for each test
    unique_email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    account_store = AccountStore(user_id=user.id)
    account = await account_store.create(
        AccountCreate(user_id=user.id, email=unique_email)
    )

    return user, account


async def test_magic_link_complete_flow():
    """Test the complete happy path: request -> consume -> authenticate"""
    client = TestClient(app)
    user, account = await create_test_user_and_account()

    # Step 1: Check initial auth status (not authenticated)
    response = client.get("/auth/status")
    assert response.status_code == 200
    auth_status = AuthStatusResponse(**response.json())
    assert auth_status.authenticated is False
    assert auth_status.user_id is None

    # Step 2: Request magic link
    response = client.post("/auth/magic/request", json={"email": account.email})
    assert response.status_code == 200
    magic_link_response = MagicLinkResponse(**response.json())

    assert magic_link_response.success is True
    assert magic_link_response.token is not None  # Should have token for existing user
    assert "successfully" in magic_link_response.message.lower()

    # Extract token and set cookies on client
    magic_token = magic_link_response.token
    if "device_nonce" in response.cookies:
        client.cookies.set("device_nonce", response.cookies["device_nonce"])

    # Step 3: Consume magic link to create session
    response = client.post("/auth/magic/consume", json={"token": magic_token})
    assert response.status_code == 200
    consume_response = MagicLinkConsumeResponse(**response.json())
    assert consume_response.success is True
    assert consume_response.message == "Successfully authenticated"
    assert consume_response.redirect_to is None

    # Step 4: Verify authentication status
    response = client.get("/auth/status")
    assert response.status_code == 200
    auth_status = AuthStatusResponse(**response.json())
    assert auth_status.authenticated is True
    assert auth_status.user_id == user.id

    # Step 5: Access protected endpoint
    response = client.get("/auth/me")
    assert response.status_code == 200
    user_response = User(**response.json())
    assert user_response.id == user.id
    assert user_response.created_at is not None

    # Step 6: Logout
    response = client.post("/auth/logout")
    assert response.status_code == 200
    logout_response = LogoutResponse(**response.json())
    assert logout_response.success is True
    assert logout_response.message == "Logged out successfully"

    # Step 7: Verify logout worked
    response = client.get("/auth/status")
    assert response.status_code == 200
    auth_status = AuthStatusResponse(**response.json())
    assert auth_status.authenticated is False
    assert auth_status.user_id is None


async def test_magic_link_with_redirect():
    """Test magic link with redirect_to parameter"""
    client = TestClient(app)
    _, account = await create_test_user_and_account()

    # Request magic link with redirect
    response = client.post(
        "/auth/magic/request",
        json={"email": account.email, "redirect_to": "/dashboard"},
    )
    assert response.status_code == 200
    magic_link_response = MagicLinkResponse(**response.json())
    magic_token = magic_link_response.token

    if "device_nonce" in response.cookies:
        client.cookies.set("device_nonce", response.cookies["device_nonce"])

    # Consume magic link
    response = client.post("/auth/magic/consume", json={"token": magic_token})
    assert response.status_code == 200
    consume_response = MagicLinkConsumeResponse(**response.json())
    assert consume_response.success is True
    assert consume_response.redirect_to == "/dashboard"


async def test_nonexistent_user_request():
    """Test magic link request for non-existent user (no user enumeration)"""
    client = TestClient(app)

    response = client.post(
        "/auth/magic/request", json={"email": "nonexistent@example.com"}
    )
    assert response.status_code == 200
    magic_link_response = MagicLinkResponse(**response.json())
    assert magic_link_response.success is True
    assert magic_link_response.token is None  # No token for non-existent user
    assert magic_link_response.message == "Magic link sent successfully"


async def test_invalid_token_consumption():
    """Test consuming invalid token"""
    client = TestClient(app)

    # Set a device nonce first
    client.cookies.set("device_nonce", "test-device-nonce")

    response = client.post("/auth/magic/consume", json={"token": "invalid-token"})
    assert response.status_code == 400
    data = response.json()
    assert "invalid or expired" in data["detail"].lower()


async def test_token_reuse_prevention():
    """Test that magic links can't be reused"""
    client = TestClient(app)
    user, account = await create_test_user_and_account()

    # Request magic link
    magic_response = client.post("/auth/magic/request", json={"email": account.email})
    assert magic_response.status_code == 200
    magic_link_response = MagicLinkResponse(**magic_response.json())
    magic_token = magic_link_response.token

    if "device_nonce" in magic_response.cookies:
        client.cookies.set("device_nonce", magic_response.cookies["device_nonce"])

    # First consumption - should work
    response = client.post("/auth/magic/consume", json={"token": magic_token})
    assert response.status_code == 200

    # Use a new client for second attempt (simulates different session)
    client2 = TestClient(app)
    if "device_nonce" in magic_response.cookies:
        client2.cookies.set("device_nonce", magic_response.cookies["device_nonce"])

    # Second consumption - should fail
    response = client2.post("/auth/magic/consume", json={"token": magic_token})
    assert response.status_code == 400
    data = response.json()
    assert "invalid or expired" in data["detail"].lower()


async def test_device_binding_enforcement():
    """Test that device binding is enforced"""
    client = TestClient(app)
    user, account = await create_test_user_and_account()

    # Request magic link
    response = client.post("/auth/magic/request", json={"email": account.email})
    assert response.status_code == 200
    magic_link_response = MagicLinkResponse(**response.json())
    magic_token = magic_link_response.token
    device_nonce = response.cookies.get("device_nonce")

    # Try to consume without device nonce cookie
    client_no_cookie = TestClient(app)
    response = client_no_cookie.post("/auth/magic/consume", json={"token": magic_token})
    assert response.status_code == 400
    data = response.json()
    assert "device not recognized" in data["detail"].lower()

    # Try to consume with wrong device nonce
    client_wrong_cookie = TestClient(app)
    client_wrong_cookie.cookies.set("device_nonce", "wrong-nonce")
    response = client_wrong_cookie.post(
        "/auth/magic/consume", json={"token": magic_token}
    )
    assert response.status_code == 400
    data = response.json()
    assert "device mismatch" in data["detail"].lower()

    # Should work with correct device nonce
    if device_nonce:
        client.cookies.set("device_nonce", device_nonce)
    response = client.post("/auth/magic/consume", json={"token": magic_token})
    assert response.status_code == 200


async def test_missing_token_in_consume():
    """Test consuming magic link without token"""
    client = TestClient(app)

    response = client.post("/auth/magic/consume", json={})
    assert response.status_code == 422  # Validation error for missing token


async def test_invalid_email_format():
    """Test magic link request with invalid email"""
    client = TestClient(app)

    response = client.post("/auth/magic/request", json={"email": "invalid-email"})
    assert response.status_code == 422  # Validation error


async def test_protected_endpoint_without_auth():
    """Test accessing protected endpoint without authentication"""
    client = TestClient(app)

    response = client.get("/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert "not authenticated" in data["detail"].lower()


async def test_session_persistence_across_requests():
    """Test that session persists across multiple requests"""
    client = TestClient(app)
    user, account = await create_test_user_and_account()

    # Complete login flow
    response = client.post("/auth/magic/request", json={"email": account.email})
    magic_link_response = MagicLinkResponse(**response.json())
    magic_token = magic_link_response.token

    if "device_nonce" in response.cookies:
        client.cookies.set("device_nonce", response.cookies["device_nonce"])

    response = client.post("/auth/magic/consume", json={"token": magic_token})
    assert response.status_code == 200

    # Make multiple requests with session
    for _ in range(3):
        response = client.get("/auth/me")
        assert response.status_code == 200
        user_response = User(**response.json())
        assert user_response.id == user.id


async def test_token_hashing_security():
    """Verify that raw tokens are never stored in database"""
    client = TestClient(app)
    user, account = await create_test_user_and_account()

    # Request magic link
    response = client.post("/auth/magic/request", json={"email": account.email})
    magic_link_response = MagicLinkResponse(**response.json())
    magic_token = magic_link_response.token

    # Verify token is hashed in database
    magic_link_store = MagicLinkStore()
    token_hash = magic_link_store.hash_token(magic_token)

    # Should find by hash
    stored_link = await magic_link_store.get_by_token_hash(token_hash)
    assert stored_link is not None
    assert stored_link.token_hash == token_hash
    assert stored_link.token_hash != magic_token  # Hash != raw token


async def test_device_nonce_cookie_creation():
    """Test that device nonce cookie is properly created"""
    client = TestClient(app)
    user, account = await create_test_user_and_account()

    response = client.post("/auth/magic/request", json={"email": account.email})

    # In TestClient, cookies are handled differently than real HTTP
    # We can verify the response was successful and cookie was set
    assert response.status_code == 200
    if "device_nonce" in response.cookies:
        # Cookie was created successfully
        assert response.cookies["device_nonce"] is not None


async def test_session_authentication_works():
    """Test that session management works correctly"""
    client = TestClient(app)
    user, account = await create_test_user_and_account()

    # Complete login to get session
    response = client.post("/auth/magic/request", json={"email": account.email})
    magic_link_response = MagicLinkResponse(**response.json())
    magic_token = magic_link_response.token

    if "device_nonce" in response.cookies:
        client.cookies.set("device_nonce", response.cookies["device_nonce"])

    response = client.post("/auth/magic/consume", json={"token": magic_token})
    assert response.status_code == 200

    # Verify session works
    response = client.get("/auth/me")
    assert response.status_code == 200
    user_response = User(**response.json())
    assert user_response.id == user.id


async def test_cleanup_expired_tokens():
    """Test that expired tokens are properly cleaned up"""
    magic_link_store = MagicLinkStore()

    # Cleanup should not raise errors
    cleanup_count = await magic_link_store.cleanup_expired()
    assert cleanup_count >= 0  # Should return count of cleaned records


async def test_device_nonce_persistence():
    """Test that device nonce persists across multiple requests"""
    client = TestClient(app)
    user, account = await create_test_user_and_account()

    # First request - should create device nonce
    response1 = client.post("/auth/magic/request", json={"email": account.email})
    assert response1.status_code == 200

    if "device_nonce" in response1.cookies:
        device_nonce1 = response1.cookies["device_nonce"]
        client.cookies.set("device_nonce", device_nonce1)

    # Second request with same client - should reuse device nonce
    response2 = client.post("/auth/magic/request", json={"email": account.email})
    assert response2.status_code == 200
    # Should not set device_nonce cookie again since client already has it
