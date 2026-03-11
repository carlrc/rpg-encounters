#!/usr/bin/env python3

from app.data.character_store import CharacterStore
from app.data.encounter_store import EncounterStore
from app.data.player_store import PlayerStore
from app.models.character import CharacterCreate
from app.models.encounter import EncounterCreate, EncounterUpdate
from app.models.player import PlayerCreate
from tests.end_to_end.utils import create_authenticated_client
from tests.fixtures.generate import default_character, default_encounter, default_player


async def test_create_encounter_rejects_cross_tenant_ids():
    client, user_a, _, world_a = await create_authenticated_client()
    _, user_b, _, world_b = await create_authenticated_client()

    character_store_b = CharacterStore(user_id=user_b.id, world_id=world_b.id)
    player_store_b = PlayerStore(user_id=user_b.id, world_id=world_b.id)

    character_b = default_character()
    player_b = default_player()

    created_character_b = await character_store_b.create(
        CharacterCreate(**character_b.model_dump(exclude={"id"}))
    )
    created_player_b = await player_store_b.create(
        PlayerCreate(**player_b.model_dump(exclude={"id"}))
    )

    encounter = default_encounter(
        encounter_id=1,
        character_id=created_character_b.id,
        player_id=created_player_b.id,
    )
    encounter_create = EncounterCreate(**encounter.model_dump(exclude={"id"}))

    response = client.post(
        "/api/encounters",
        json=encounter_create.model_dump(),
        headers={"X-World-Id": str(world_a.id)},
    )
    assert response.status_code == 404

    encounter_store_a = EncounterStore(user_id=user_a.id, world_id=world_a.id)
    encounters = await encounter_store_a.get_all()
    assert encounters == []


async def test_update_encounter_rejects_cross_tenant_ids():
    client, user_a, _, world_a = await create_authenticated_client()
    _, user_b, _, world_b = await create_authenticated_client()

    character_store_a = CharacterStore(user_id=user_a.id, world_id=world_a.id)
    player_store_a = PlayerStore(user_id=user_a.id, world_id=world_a.id)
    encounter_store_a = EncounterStore(user_id=user_a.id, world_id=world_a.id)

    character_a = default_character()
    player_a = default_player()

    created_character_a = await character_store_a.create(
        CharacterCreate(**character_a.model_dump(exclude={"id"}))
    )
    created_player_a = await player_store_a.create(
        PlayerCreate(**player_a.model_dump(exclude={"id"}))
    )

    encounter = default_encounter(
        encounter_id=1,
        character_id=created_character_a.id,
        player_id=created_player_a.id,
    )
    created_encounter = await encounter_store_a.create(
        EncounterCreate(**encounter.model_dump(exclude={"id"}))
    )
    assert created_encounter

    character_store_b = CharacterStore(user_id=user_b.id, world_id=world_b.id)
    player_store_b = PlayerStore(user_id=user_b.id, world_id=world_b.id)

    created_character_b = await character_store_b.create(
        CharacterCreate(**default_character().model_dump(exclude={"id"}))
    )
    created_player_b = await player_store_b.create(
        PlayerCreate(**default_player().model_dump(exclude={"id"}))
    )

    update_payload = EncounterUpdate(
        character_ids=[created_character_b.id],
        player_ids=[created_player_b.id],
    )

    response = client.put(
        f"/api/encounters/{created_encounter.id}",
        json=update_payload.model_dump(exclude_unset=True),
        headers={"X-World-Id": str(world_a.id)},
    )
    assert response.status_code == 404

    refreshed = await encounter_store_a.get_by_id(created_encounter.id)
    assert refreshed is not None
    assert refreshed.character_ids == [created_character_a.id]
    assert refreshed.player_ids == [created_player_a.id]


async def test_create_and_update_encounter_accepts_in_scope_ids():
    client, user, _, world = await create_authenticated_client()

    character_store = CharacterStore(user_id=user.id, world_id=world.id)
    player_store = PlayerStore(user_id=user.id, world_id=world.id)
    encounter_store = EncounterStore(user_id=user.id, world_id=world.id)

    character = default_character()
    player = default_player()

    created_character = await character_store.create(
        CharacterCreate(**character.model_dump(exclude={"id"}))
    )
    created_player = await player_store.create(
        PlayerCreate(**player.model_dump(exclude={"id"}))
    )

    encounter = default_encounter(
        encounter_id=1,
        character_id=created_character.id,
        player_id=created_player.id,
    )
    encounter_create = EncounterCreate(**encounter.model_dump(exclude={"id"}))

    create_response = client.post(
        "/api/encounters",
        json=encounter_create.model_dump(),
        headers={"X-World-Id": str(world.id)},
    )
    assert create_response.status_code == 200
    created = create_response.json()
    assert created["character_ids"] == [created_character.id]
    assert created["player_ids"] == [created_player.id]

    update_payload = EncounterUpdate(
        character_ids=[created_character.id],
        player_ids=[created_player.id],
    )
    update_response = client.put(
        f"/api/encounters/{created['id']}",
        json=update_payload.model_dump(exclude_unset=True),
        headers={"X-World-Id": str(world.id)},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["character_ids"] == [created_character.id]
    assert updated["player_ids"] == [created_player.id]

    stored = await encounter_store.get_by_id(created["id"])
    assert stored is not None
    assert stored.character_ids == [created_character.id]
    assert stored.player_ids == [created_player.id]
