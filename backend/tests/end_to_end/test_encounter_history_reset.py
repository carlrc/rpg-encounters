#!/usr/bin/env python3
from app.data.character_store import CharacterStore
from app.data.conversation_store import ConversationStore
from app.data.encounter_store import EncounterStore
from app.data.influence_store import InfluenceStore
from app.data.player_store import PlayerStore
from app.models.character import CharacterCreate
from app.models.conversation import ConversationCreate
from app.models.encounter import EncounterCreate
from app.models.influence import Influence
from app.models.player import PlayerCreate
from app.services.influence_calculator import calculate_base_influence
from tests.end_to_end.utils import create_authenticated_client
from tests.fixtures.generate import default_character, default_encounter, default_player


async def test_delete_encounter_conversation_history():
    client, user, _, world = await create_authenticated_client()

    character_store = CharacterStore(user_id=user.id, world_id=world.id)
    player_store = PlayerStore(user_id=user.id, world_id=world.id)
    encounter_store = EncounterStore(user_id=user.id, world_id=world.id)
    conversation_store = ConversationStore(user_id=user.id, world_id=world.id)
    influence_store = InfluenceStore(user_id=user.id, world_id=world.id)

    character = default_character()
    character_data = CharacterCreate(**character.model_dump(exclude={"id"}))
    created_character = await character_store.create(character_data)

    player = default_player()
    player_data = PlayerCreate(**player.model_dump(exclude={"id"}))
    created_player = await player_store.create(player_data)

    encounter = default_encounter(
        encounter_id=1, character_id=created_character.id, player_id=created_player.id
    )
    encounter_data = EncounterCreate(**encounter.model_dump(exclude={"id"}))
    created_encounter = await encounter_store.create(encounter_data)

    base_influence = calculate_base_influence(
        character=created_character, player=created_player
    )
    await influence_store.get_or_create_influence(
        created_character.id, created_player.id, base_influence
    )
    await influence_store.update(
        Influence(
            character_id=created_character.id,
            player_id=created_player.id,
            base=base_influence,
            earned=3,
        )
    )

    conversation_create = ConversationCreate(
        player_id=created_player.id,
        character_id=created_character.id,
        encounter_id=created_encounter.id,
        messages=[],
    )
    await conversation_store.create(conversation_create)

    delete_response = client.delete(
        f"/api/encounters/{created_encounter.id}/conversation/{created_player.id}/{created_character.id}",
        headers={"X-World-Id": str(world.id)},
    )
    assert delete_response.status_code == 204

    deleted_conversation = await conversation_store.get(
        player_id=created_player.id,
        character_id=created_character.id,
        encounter_id=created_encounter.id,
    )
    assert deleted_conversation is None

    deleted_influence = await influence_store.get_influence(
        created_character.id, created_player.id
    )
    assert deleted_influence is None

    refreshed_response = client.get(
        f"/api/encounters/{created_encounter.id}/conversation/{created_player.id}/{created_character.id}",
        headers={"X-World-Id": str(world.id)},
    )
    assert refreshed_response.status_code == 200
    refreshed_payload = refreshed_response.json()
    assert refreshed_payload["influence"] == base_influence
