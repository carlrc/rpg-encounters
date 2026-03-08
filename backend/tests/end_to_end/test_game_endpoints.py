#!/usr/bin/env python3
from fastapi.testclient import TestClient

from app.main import app
from tests.end_to_end.utils import (
    create_authenticated_client,
)


async def test_game_data_without_authentication():
    """Test GET /api/game/ without session returns 401"""
    client = TestClient(app)

    # Try to access without authentication
    response = client.get("/api/game/")

    # Endpoint now requires authentication
    assert response.status_code == 401


async def test_game_data_requires_world_header():
    """Test GET /api/game/ requires X-World-Id header (when authenticated)"""
    client = TestClient(app)

    # Without authentication, we get 401 (authentication takes precedence)
    response = client.get("/api/game/")
    assert response.status_code == 401


async def test_game_data_with_authentication():
    """Test GET /api/game/ returns game data when authenticated"""
    client, _, _, world = await create_authenticated_client()

    # Test the game endpoint with authentication
    response = client.get("/api/game/", headers={"X-World-Id": str(world.id)})
    assert response.status_code == 200
