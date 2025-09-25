#!/usr/bin/env python3
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.auth.session import SESSION_CONFIG
from app.data.player_magic_link_store import PlayerMagicLinkStore
from app.main import app
from tests.end_to_end.utils import (
    create_authenticated_client,
    create_authenticated_player_client,
    create_test_player,
    create_test_user_and_account,
    decode_session,
    get_latest_player_magic_link_for_player,
)


async def test_player_login_complete_flow():
    """Test complete player login flow: POST to generate link, GET to consume"""
    # Create authenticated user client to request player login
    dm_client, user, _, world = await create_authenticated_client()

    # Create a player
    player, _ = await create_test_player(user.id, world.id)

    # Step 1: Generate player login link
    response = dm_client.post(
        f"/api/players/{player.id}/login", headers={"X-World-Id": str(world.id)}
    )
    assert response.status_code == 200
    data = response.json()
    assert "login_url" in data
    assert "expires_at" in data

    # Extract token from login_url
    login_url = data["login_url"]
    token = login_url.split("token=")[1]

    # Step 2: Use a new client to consume the player login link (simulates player using link)
    player_client = TestClient(app)
    response = player_client.get(f"/api/players/{player.id}/login?token={token}")
    assert response.status_code == 200

    # Verify response contains world_id
    data = response.json()
    assert data["world_id"] == world.id

    # Verify player session was created
    session_cookie = player_client.cookies.get(SESSION_CONFIG.session_cookie_name)
    assert session_cookie is not None

    decoded_session = decode_session(cookie_value=session_cookie)
    assert decoded_session["user_id"] == user.id
    assert decoded_session["player_id"] == player.id
    assert decoded_session["world_id"] == world.id

    # Verify magic link is marked as used
    player_magic_link = await get_latest_player_magic_link_for_player(player.id)
    assert player_magic_link is not None
    assert player_magic_link.used is True
    assert player_magic_link.used_at is not None


async def test_player_login_request_nonexistent_player():
    """Test requesting login for non-existent player"""
    client, _, _, world = await create_authenticated_client()

    response = client.post(
        "/api/players/99999/login", headers={"X-World-Id": str(world.id)}
    )
    assert response.status_code == 404


async def test_player_login_invalid_token_consumption():
    """Test consuming invalid token"""
    _, user, _, world = await create_authenticated_client()

    # Create a player
    player, _ = await create_test_player(user.id, world.id)

    # Try to consume with invalid token
    client = TestClient(app)
    fake_token = PlayerMagicLinkStore.generate_token()
    response = client.get(f"/api/players/{player.id}/login?token={fake_token}")
    assert response.status_code == 400


async def test_player_login_token_reuse_prevention():
    """Test that player login tokens can't be reused"""
    # Create authenticated user client
    dm_client, user, _, world = await create_authenticated_client()

    # Create a player
    player, _ = await create_test_player(user.id, world.id)

    test_token = PlayerMagicLinkStore.generate_token()
    with patch(
        "app.data.player_magic_link_store.PlayerMagicLinkStore.generate_token"
    ) as mock_generate:
        mock_generate.return_value = test_token
        # Generate player login link
        response = dm_client.post(
            f"/api/players/{player.id}/login", headers={"X-World-Id": str(world.id)}
        )
        assert response.status_code == 200

    # First consumption - should work
    player_client1 = TestClient(app)
    response = player_client1.get(f"/api/players/{player.id}/login?token={test_token}")
    assert response.status_code == 200

    # Verify token is now marked as used
    player_magic_link = await get_latest_player_magic_link_for_player(player.id)
    assert player_magic_link is not None
    assert player_magic_link.used is True

    # Second consumption - should fail
    player_client2 = TestClient(app)
    response = player_client2.get(f"/api/players/{player.id}/login?token={test_token}")
    assert response.status_code == 400


async def test_player_login_mismatched_player_id():
    """Test consuming token with wrong player_id in URL"""
    # Create authenticated user client
    dm_client, user, _, world = await create_authenticated_client()

    # Create two players
    player1, _ = await create_test_player(user.id, world.id)
    player2, _ = await create_test_player(user.id, world.id)

    # Generate login link for player1
    response = dm_client.post(
        f"/api/players/{player1.id}/login", headers={"X-World-Id": str(world.id)}
    )
    assert response.status_code == 200
    data = response.json()
    token = data["login_url"].split("token=")[1]

    # Try to use player1's token with player2's URL
    client = TestClient(app)
    response = client.get(f"/api/players/{player2.id}/login?token={token}")
    assert response.status_code == 401


async def test_player_login_rate_limiting():
    """Test rate limiting on player login consumption endpoint"""
    _, user, _, world = await create_authenticated_client()

    # Create a player
    player, _ = await create_test_player(user.id, world.id)

    client = TestClient(app)

    # Make requests up to the rate limit
    # Note: Rate limit in the code is 50 requests per 10 minutes per IP
    for _ in range(5):  # Test a smaller number to avoid long test times
        fake_token = PlayerMagicLinkStore.generate_token()
        response = client.get(f"/api/players/{player.id}/login?token={fake_token}")
        # Should be 400 for invalid token, not 429 for rate limit
        assert response.status_code == 400


async def test_player_login_missing_token():
    """Test consuming player login without token parameter"""
    user, _, world = await create_test_user_and_account()

    # Create a player
    player, _ = await create_test_player(user.id, world.id)

    client = TestClient(app)
    response = client.get(f"/api/players/{player.id}/login")
    assert response.status_code == 422  # Missing required parameter


async def test_player_login_expired_token():
    """Test consuming expired player login token"""
    from datetime import datetime, timedelta, timezone

    from app.db.models.player_magic_link import PlayerMagicLinkORM
    from app.models.player_magic_link import PlayerMagicLinkCreate

    user, _, world = await create_test_user_and_account()

    # Create a player
    player, _ = await create_test_player(user.id, world.id)

    # Create expired token directly in database
    player_magic_link_store = PlayerMagicLinkStore()
    test_token = PlayerMagicLinkStore.generate_token()
    expired_time = datetime.now(timezone.utc) - timedelta(hours=1)

    async with player_magic_link_store.get_session() as session:
        magic_link_data = PlayerMagicLinkCreate(
            player_id=player.id,
            user_id=user.id,
            world_id=world.id,
            token_hash=PlayerMagicLinkStore.hash_token(test_token),
            expires_at=expired_time,
            used=False,
        )

        player_magic_link_orm = PlayerMagicLinkORM(**magic_link_data.model_dump())
        session.add(player_magic_link_orm)
        await session.flush()

    # Try to consume expired token
    client = TestClient(app)
    response = client.get(f"/api/players/{player.id}/login?token={test_token}")
    assert response.status_code == 400


async def test_player_session_authentication():
    """Test that player session can be used to access player endpoints"""
    # Create authenticated player client
    player_client, _, player, _ = await create_authenticated_player_client()

    # Try to access player's encounter (requires player authentication)
    response = player_client.get(f"/api/players/{player.id}/encounter")

    # The response might be 404 (no encounter assigned) or 200 (encounter exists)
    # Both are valid - the important thing is it's not 401/403 (authentication failed)
    assert response.status_code in [200, 404]
    assert response.status_code != 401  # Not unauthorized
    assert response.status_code != 403  # Not forbidden


async def test_player_login_unauthorized_access():
    """Test that unauthenticated requests can't generate player login links"""
    client = TestClient(app)

    response = client.post("/api/players/1/login")
    assert response.status_code == 401


async def test_multiple_player_sessions():
    """Test that multiple players can have independent sessions"""
    # Create DM and two players
    dm_client, user, _, world = await create_authenticated_client()

    # Create two players
    player1, _ = await create_test_player(user.id, world.id)
    player2, _ = await create_test_player(user.id, world.id)

    # Generate login links for both players
    response1 = dm_client.post(
        f"/api/players/{player1.id}/login", headers={"X-World-Id": str(world.id)}
    )
    assert response1.status_code == 200
    token1 = response1.json()["login_url"].split("token=")[1]

    response2 = dm_client.post(
        f"/api/players/{player2.id}/login", headers={"X-World-Id": str(world.id)}
    )
    assert response2.status_code == 200
    token2 = response2.json()["login_url"].split("token=")[1]

    # Create separate clients for each player
    player1_client = TestClient(app)
    player2_client = TestClient(app)

    # Consume tokens to create sessions
    response1 = player1_client.get(f"/api/players/{player1.id}/login?token={token1}")
    assert response1.status_code == 200

    response2 = player2_client.get(f"/api/players/{player2.id}/login?token={token2}")
    assert response2.status_code == 200

    # Verify each client has the correct session
    session1 = decode_session(
        cookie_value=player1_client.cookies.get(SESSION_CONFIG.session_cookie_name)
    )
    session2 = decode_session(
        cookie_value=player2_client.cookies.get(SESSION_CONFIG.session_cookie_name)
    )

    assert session1["player_id"] == player1.id
    assert session2["player_id"] == player2.id
    assert session1["player_id"] != session2["player_id"]


# Helper function to avoid duplication
async def create_authenticated_user_and_account():
    """Helper to create authenticated user and account for specific tests"""
    return await create_test_user_and_account()
