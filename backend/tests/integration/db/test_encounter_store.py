#!/usr/bin/env python3
import os

from app.data.character_store import CharacterStore
from app.data.encounter_store import EncounterStore
from app.db.connection import get_async_db_session
from app.models.character import CharacterCreate
from app.models.encounter import EncounterCreate, EncounterUpdate
from tests.fixtures.generate import default_character, default_encounter


async def test_encounter_store():
    url = os.getenv("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        encounter_store = EncounterStore(user_id=1, world_id=1, session=session)
        character_store = CharacterStore(user_id=1, world_id=1, session=session)

        # Create test characters using generate functions
        character1 = default_character(character_id=1)
        character1_data = CharacterCreate(**character1.model_dump(exclude={"id"}))
        created_character1 = await character_store.create_character(character1_data)

        character2 = default_character(character_id=2)
        character2_data = CharacterCreate(**character2.model_dump(exclude={"id"}))
        created_character2 = await character_store.create_character(character2_data)

        # Test create encounter with characters using generate function
        encounter = default_encounter(
            encounter_id=1, character_id=created_character1.id
        )
        new_encounter_data = EncounterCreate(
            name=encounter.name,
            description=encounter.description,
            position_x=encounter.position_x,
            position_y=encounter.position_y,
            character_ids=[created_character1.id, created_character2.id],
        )

        created_encounter = await encounter_store.create_encounter(new_encounter_data)
        assert created_encounter.name == new_encounter_data.name
        assert created_encounter.id is not None
        assert created_encounter.description == new_encounter_data.description
        assert created_encounter.position_x == new_encounter_data.position_x
        assert created_encounter.position_y == new_encounter_data.position_y
        assert set(created_encounter.character_ids) == {
            created_character1.id,
            created_character2.id,
        }

        # Test get all encounters
        all_encounters = await encounter_store.get_all_encounters()
        assert len(all_encounters) == 1
        assert all_encounters[0].id == created_encounter.id

        # Test get encounter by id
        retrieved_encounter = await encounter_store.get_encounter_by_id(
            created_encounter.id
        )
        assert retrieved_encounter is not None
        assert retrieved_encounter.name == created_encounter.name
        assert set(retrieved_encounter.character_ids) == {
            created_character1.id,
            created_character2.id,
        }

        # Test get non-existent encounter
        non_existent = await encounter_store.get_encounter_by_id(99999)
        assert non_existent is None

        # Test create encounter without characters
        encounter_no_chars = EncounterCreate(
            name="Empty Forest Path",
            description="A quiet path through the woods.",
            position_x=500.0,
            position_y=300.0,
            character_ids=None,
        )

        created_no_chars = await encounter_store.create_encounter(encounter_no_chars)
        assert created_no_chars.character_ids == []

        # Test update encounter
        update_data = EncounterUpdate(
            name="Updated Tavern Name",
            description="An updated description of the tavern.",
            position_x=250.0,
            position_y=175.0,
            character_ids=[created_character1.id],  # Remove one character
        )

        updated_encounter = await encounter_store.update_encounter(
            created_encounter.id, update_data
        )
        assert updated_encounter is not None
        assert updated_encounter.name == update_data.name
        assert updated_encounter.description == update_data.description
        assert updated_encounter.position_x == update_data.position_x
        assert updated_encounter.position_y == update_data.position_y
        assert updated_encounter.character_ids == [created_character1.id]

        # Test update non-existent encounter
        update_non_existent = await encounter_store.update_encounter(99999, update_data)
        assert update_non_existent is None

        # Test partial update (only some fields)
        partial_update = EncounterUpdate(
            name="Partially Updated Name",
        )
        partial_updated = await encounter_store.update_encounter(
            created_encounter.id, partial_update
        )
        assert partial_updated is not None
        assert partial_updated.name == partial_update.name
        assert (
            partial_updated.description == update_data.description
        )  # Should keep previous value
        assert (
            partial_updated.position_x == update_data.position_x
        )  # Should keep previous value

        # Test delete encounter
        deleted = await encounter_store.delete_encounter(created_encounter.id)
        assert deleted is True

        # Verify deletion
        deleted_encounter = await encounter_store.get_encounter_by_id(
            created_encounter.id
        )
        assert deleted_encounter is None

        # Test delete non-existent encounter
        deleted_again = await encounter_store.delete_encounter(created_encounter.id)
        assert deleted_again is False

        # Verify remaining encounters
        remaining_encounters = await encounter_store.get_all_encounters()
        assert (
            len(remaining_encounters) == 1
        )  # Only the one without characters should remain
