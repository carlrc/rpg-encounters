#!/usr/bin/env python3

from app.data.character_store import CharacterStore
from app.models.canvas import CanvasSaveRequest
from app.models.character import CharacterCreate
from app.models.encounter import EncounterWithId
from app.models.encounter_connection import ConnectionUpdate
from tests.end_to_end.utils import create_authenticated_client
from tests.fixtures.generate import (
    default_character,
    default_connection,
    default_encounter,
)


async def test_canvas_save_and_load_with_connection_roundtrip():
    client, user, _, world = await create_authenticated_client()

    character_store = CharacterStore(user_id=user.id, world_id=world.id)
    created_character = await character_store.create(
        CharacterCreate(**default_character().model_dump(exclude={"id"}))
    )
    assert created_character is not None

    encounter_seed = default_encounter(
        encounter_id=-1, character_id=created_character.id
    )

    encounter_one = EncounterWithId.model_validate(encounter_seed.model_dump())
    encounter_two = encounter_one.model_copy(update={"id": -2})
    save_payload = CanvasSaveRequest(
        new_encounters=[encounter_one, encounter_two],
        new_connections=[
            # Canvas save accepts temporary encounter IDs for new nodes and remaps them to persisted IDs.
            default_connection(source_encounter_id=-1, target_encounter_id=-2)
        ],
    )

    save_response = client.post(
        "/api/canvas",
        json=save_payload.model_dump(),
        headers={"X-World-Id": str(world.id)},
    )
    assert save_response.status_code == 200

    saved = save_response.json()
    assert len(saved["encounters"]) == 2
    assert len(saved["connections"]) == 1

    connection = saved["connections"][0]
    source_id = connection["source_encounter_id"]
    target_id = connection["target_encounter_id"]

    load_response = client.get("/api/canvas", headers={"X-World-Id": str(world.id)})
    assert load_response.status_code == 200

    loaded = load_response.json()
    loaded_encounter_ids = {encounter["id"] for encounter in loaded["encounters"]}
    assert source_id in loaded_encounter_ids
    assert target_id in loaded_encounter_ids

    matching = [
        c
        for c in loaded["connections"]
        if c["source_encounter_id"] == source_id
        and c["target_encounter_id"] == target_id
    ]
    # Ensure the saved edge survives a full save->load cycle after temp encounter IDs are mapped.
    assert len(matching) == 1


async def test_canvas_save_rejects_missing_connection_source_target():
    client, _, _, world = await create_authenticated_client()

    missing_source_payload = CanvasSaveRequest(
        new_connections=[
            default_connection(source_encounter_id=999999, target_encounter_id=999998)
        ]
    )

    missing_source_response = client.post(
        "/api/canvas",
        json=missing_source_payload.model_dump(),
        headers={"X-World-Id": str(world.id)},
    )
    assert missing_source_response.status_code == 404


async def test_canvas_save_rejects_existing_connection_update_missing_ids():
    client, _, _, world = await create_authenticated_client()

    payload = CanvasSaveRequest(
        existing_connections=[
            ConnectionUpdate(
                id=123,
                source_handle="right",
                target_handle="left",
                edge_type="straight",
                stroke_color="#007bff",
                stroke_width=3,
            )
        ]
    )

    response = client.post(
        "/api/canvas",
        json=payload.model_dump(),
        headers={"X-World-Id": str(world.id)},
    )
    assert response.status_code == 400


async def test_get_encounter_connections_unknown_encounter_returns_404():
    client, _, _, world = await create_authenticated_client()

    response = client.get(
        "/api/encounters/999999/connections",
        headers={"X-World-Id": str(world.id)},
    )
    assert response.status_code == 404
