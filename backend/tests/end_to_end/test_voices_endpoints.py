#!/usr/bin/env python3

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.end_to_end.utils import create_authenticated_client


async def test_voices_requires_authentication():
    client = TestClient(app)

    response = client.get("/api/voices/tts_providers")
    assert response.status_code == 401


async def test_voices_requires_world_header_for_authenticated_user():
    client, _, _, _ = await create_authenticated_client()

    response = client.get("/api/voices/tts_providers")
    assert response.status_code == 400


async def test_get_tts_providers_happy_path():
    client, _, _, world = await create_authenticated_client()

    response = client.get(
        "/api/voices/tts_providers", headers={"X-World-Id": str(world.id)}
    )
    assert response.status_code == 200
    providers = response.json()
    assert isinstance(providers, list)
    assert len(providers) > 0


async def test_search_voices_happy_path_with_configured_provider():
    client, _, _, world = await create_authenticated_client()

    providers_response = client.get(
        "/api/voices/tts_providers", headers={"X-World-Id": str(world.id)}
    )
    assert providers_response.status_code == 200
    providers = providers_response.json()
    assert len(providers) > 0
    provider = providers[0]

    response = client.get(
        f"/api/voices/search?search_term=en&tts_provider={provider}",
        headers={"X-World-Id": str(world.id)},
    )
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload.get("voices"), list)
    assert "has_more" in payload
    assert "total_count" in payload
    if payload["voices"]:
        voice = payload["voices"][0]
        assert "voice_id" in voice
        assert "name" in voice


async def test_get_voice_sample_happy_path_with_configured_provider():
    client, _, _, world = await create_authenticated_client()

    providers_response = client.get(
        "/api/voices/tts_providers", headers={"X-World-Id": str(world.id)}
    )
    assert providers_response.status_code == 200
    providers = providers_response.json()
    assert len(providers) > 0
    provider = providers[0]

    search_response = client.get(
        f"/api/voices/search?search_term=en&tts_provider={provider}",
        headers={"X-World-Id": str(world.id)},
    )
    assert search_response.status_code == 200
    voices = search_response.json().get("voices", [])
    if not voices:
        pytest.skip("No voices returned by configured provider")
    voice_id = voices[0]["voice_id"]

    response = client.get(
        f"/api/voices/{voice_id}/sample?tts_provider={provider}",
        headers={"X-World-Id": str(world.id)},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/mpeg")
    assert (
        f"attachment; filename=voice_sample_{voice_id}.mp3"
        in response.headers["content-disposition"]
    )
    assert len(response.content) > 0


async def test_search_voices_invalid_provider_returns_500():
    client, _, _, world = await create_authenticated_client()

    response = client.get(
        "/api/voices/search?search_term=en&tts_provider=unsupported-provider",
        headers={"X-World-Id": str(world.id)},
    )
    assert response.status_code == 500


async def test_get_voice_sample_invalid_provider_returns_500():
    client, _, _, world = await create_authenticated_client()

    response = client.get(
        "/api/voices/voice-1/sample?tts_provider=unsupported-provider",
        headers={"X-World-Id": str(world.id)},
    )
    assert response.status_code == 500
