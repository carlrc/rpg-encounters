#!/usr/bin/env python3
import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.data.character_store import CharacterStore
from app.data.encounter_store import EncounterStore
from app.data.player_store import PlayerStore
from app.main import app
from app.models.character import CharacterCreate
from app.models.encounter import EncounterCreate
from app.models.player import PlayerCreate
from app.services import challenge as challenge_service
from app.services import conversation as conversation_service
from app.services.user_token import UserTokenService
from tests.end_to_end.utils import create_authenticated_client
from tests.fixtures.generate import default_character, default_encounter, default_player


async def _fake_save_chunks_to_wav(*_args, **_kwargs) -> str:
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    return path


async def _fake_transcribe_and_moderate(*_args, **_kwargs):
    return "hello", False


async def _fake_check_token_balance(*_args, **_kwargs) -> bool:
    return True


def _patch_audio_and_tokens(monkeypatch):
    monkeypatch.setattr(
        conversation_service, "save_chunks_to_wav", _fake_save_chunks_to_wav
    )
    monkeypatch.setattr(
        conversation_service, "transcribe_and_moderate", _fake_transcribe_and_moderate
    )
    monkeypatch.setattr(
        challenge_service, "save_chunks_to_wav", _fake_save_chunks_to_wav
    )
    monkeypatch.setattr(
        challenge_service, "transcribe_and_moderate", _fake_transcribe_and_moderate
    )
    monkeypatch.setattr(
        UserTokenService, "check_token_balance", _fake_check_token_balance
    )


def _expect_ws_close_1008(connect_ws):
    try:
        with connect_ws() as ws:
            with pytest.raises(WebSocketDisconnect) as exc:
                ws.receive_text()
            assert exc.value.code == 1008
    except WebSocketDisconnect as exc:
        assert exc.code == 1008


async def test_conversation_ws_rejects_player_not_in_encounter(monkeypatch):
    _patch_audio_and_tokens(monkeypatch)

    client, user, _, world = await create_authenticated_client()

    character_store = CharacterStore(user_id=user.id, world_id=world.id)
    player_store = PlayerStore(user_id=user.id, world_id=world.id)
    encounter_store = EncounterStore(user_id=user.id, world_id=world.id)

    character = default_character()
    created_character = await character_store.create(
        CharacterCreate(**character.model_dump(exclude={"id"}))
    )

    player1 = default_player()
    created_player1 = await player_store.create(
        PlayerCreate(**player1.model_dump(exclude={"id"}))
    )

    player2 = default_player(player_id=2)
    created_player2 = await player_store.create(
        PlayerCreate(**player2.model_dump(exclude={"id"}))
    )

    encounter = default_encounter(
        encounter_id=1,
        character_id=created_character.id,
        player_id=created_player1.id,
    )
    created_encounter = await encounter_store.create(
        EncounterCreate(**encounter.model_dump(exclude={"id"}))
    )

    ws_url = (
        f"/api/encounters/{created_encounter.id}/conversation/"
        f"{created_player2.id}/{created_character.id}?world_id={world.id}"
    )

    with client.websocket_connect(ws_url) as ws:
        ws.send_text("END")
        warning = ws.receive_json()
        assert warning["type"] == "warning"

        with pytest.raises(WebSocketDisconnect) as exc:
            ws.receive_json()
        assert exc.value.code == 1008


async def test_challenge_ws_rejects_player_not_in_encounter(monkeypatch):
    _patch_audio_and_tokens(monkeypatch)

    client, user, _, world = await create_authenticated_client()

    character_store = CharacterStore(user_id=user.id, world_id=world.id)
    player_store = PlayerStore(user_id=user.id, world_id=world.id)
    encounter_store = EncounterStore(user_id=user.id, world_id=world.id)

    character = default_character()
    created_character = await character_store.create(
        CharacterCreate(**character.model_dump(exclude={"id"}))
    )

    player1 = default_player()
    created_player1 = await player_store.create(
        PlayerCreate(**player1.model_dump(exclude={"id"}))
    )

    player2 = default_player(player_id=2)
    created_player2 = await player_store.create(
        PlayerCreate(**player2.model_dump(exclude={"id"}))
    )

    encounter = default_encounter(
        encounter_id=1,
        character_id=created_character.id,
        player_id=created_player1.id,
    )
    created_encounter = await encounter_store.create(
        EncounterCreate(**encounter.model_dump(exclude={"id"}))
    )

    ws_url = (
        f"/api/encounters/{created_encounter.id}/challenge/"
        f"{created_player2.id}/{created_character.id}"
        f"?world_id={world.id}&skill=persuasion&d20_roll=10"
    )

    with client.websocket_connect(ws_url) as ws:
        ws.send_text("END")
        warning = ws.receive_json()
        assert warning["type"] == "warning"

        with pytest.raises(WebSocketDisconnect) as exc:
            ws.receive_json()
        assert exc.value.code == 1008


async def test_challenge_ws_rejects_invalid_d20_roll():
    client, _, _, world = await create_authenticated_client()

    ws_url = (
        f"/api/encounters/1/challenge/1/1"
        f"?world_id={world.id}&skill=persuasion&d20_roll=not-a-number"
    )
    _expect_ws_close_1008(lambda: client.websocket_connect(ws_url))


async def test_challenge_ws_rejects_missing_skill():
    client, _, _, world = await create_authenticated_client()

    ws_url = f"/api/encounters/1/challenge/1/1?world_id={world.id}&d20_roll=10"
    _expect_ws_close_1008(lambda: client.websocket_connect(ws_url))


async def test_conversation_ws_rejects_missing_session():
    client = TestClient(app)
    ws_url = "/api/encounters/1/conversation/1/1?world_id=1"

    _expect_ws_close_1008(lambda: client.websocket_connect(ws_url))


async def test_challenge_ws_rejects_missing_session():
    client = TestClient(app)
    ws_url = "/api/encounters/1/challenge/1/1?world_id=1&skill=persuasion&d20_roll=10"

    _expect_ws_close_1008(lambda: client.websocket_connect(ws_url))
