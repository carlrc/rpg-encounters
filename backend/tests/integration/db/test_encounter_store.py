#!/usr/bin/env python3
import pytest
from dotenv import load_dotenv

from app.data.character_store import CharacterStore
from app.data.encounter_store import EncounterStore
from app.db.init_db import create_tables, drop_tables
from app.models.alignment import Alignment
from app.models.character import CharacterCreate
from app.models.class_traits import Class
from app.models.encounter import EncounterCreate, EncounterUpdate
from app.models.race import Gender, Race, Size


@pytest.fixture(autouse=True)
def my_fixture():
    load_dotenv()
    create_tables(use_test_db=True)  # Explicitly use test database
    yield
    drop_tables(use_test_db=True)  # Explicitly use test database


def test_encounter_store():
    character_store = CharacterStore()

    # Create test characters first
    character1_data = CharacterCreate(
        name="Test Innkeeper",
        avatar=None,
        race=Race.HUMAN.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.NEUTRAL_GOOD.value,
        gender=Gender.MALE.value,
        profession="Innkeeper",
        background="A friendly innkeeper who knows all the local gossip.",
        communication_style="Warm and welcoming, always ready with a story.",
        motivation="Wants to keep his tavern as the heart of the community.",
        personality="",
        voice="JBFqnCBsd6RMkjVDRZzb",
        race_preferences={Race.HUMAN.value: 1},
        class_preferences={Class.COMMONER.value: 2},
        gender_preferences={Gender.MALE.value: 1},
        size_preferences={Size.MEDIUM.value: 1},
    )

    character2_data = CharacterCreate(
        name="Test Guard",
        avatar=None,
        race=Race.HUMAN.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.LAWFUL_GOOD.value,
        gender=Gender.FEMALE.value,
        profession="Town Guard",
        background="A dedicated guard who protects the town.",
        communication_style="Direct and authoritative.",
        motivation="Maintains law and order in the community.",
        personality="",
        voice="JBFqnCBsd6RMkjVDRZzb",
        race_preferences={Race.HUMAN.value: 1},
        class_preferences={Class.FIGHTER.value: 3},
        gender_preferences={Gender.FEMALE.value: 1},
        size_preferences={Size.MEDIUM.value: 1},
    )

    created_character1 = character_store.create_character(character1_data)
    created_character2 = character_store.create_character(character2_data)

    # Now test encounter store
    encounter_store = EncounterStore()

    # Test create encounter with characters
    new_encounter_data = EncounterCreate(
        name="The Prancing Pony Tavern",
        description="A cozy tavern filled with warm candlelight and cheerful chatter.",
        position_x=200.0,
        position_y=150.0,
        character_ids=[created_character1.id, created_character2.id],
    )

    created_encounter = encounter_store.create_encounter(new_encounter_data)
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
    all_encounters = encounter_store.get_all_encounters()
    assert len(all_encounters) == 1
    assert all_encounters[0].id == created_encounter.id

    # Test get encounter by id
    retrieved_encounter = encounter_store.get_encounter_by_id(created_encounter.id)
    assert retrieved_encounter is not None
    assert retrieved_encounter.name == created_encounter.name
    assert set(retrieved_encounter.character_ids) == {
        created_character1.id,
        created_character2.id,
    }

    # Test get non-existent encounter
    non_existent = encounter_store.get_encounter_by_id(99999)
    assert non_existent is None

    # Test create encounter without characters
    encounter_no_chars = EncounterCreate(
        name="Empty Forest Path",
        description="A quiet path through the woods.",
        position_x=500.0,
        position_y=300.0,
        character_ids=None,
    )

    created_no_chars = encounter_store.create_encounter(encounter_no_chars)
    assert created_no_chars.character_ids == []

    # Test update encounter
    update_data = EncounterUpdate(
        name="Updated Tavern Name",
        description="An updated description of the tavern.",
        position_x=250.0,
        position_y=175.0,
        character_ids=[created_character1.id],  # Remove one character
    )

    updated_encounter = encounter_store.update_encounter(
        created_encounter.id, update_data
    )
    assert updated_encounter is not None
    assert updated_encounter.name == update_data.name
    assert updated_encounter.description == update_data.description
    assert updated_encounter.position_x == update_data.position_x
    assert updated_encounter.position_y == update_data.position_y
    assert updated_encounter.character_ids == [created_character1.id]

    # Test update non-existent encounter
    update_non_existent = encounter_store.update_encounter(99999, update_data)
    assert update_non_existent is None

    # Test partial update (only some fields)
    partial_update = EncounterUpdate(
        name="Partially Updated Name",
    )
    partial_updated = encounter_store.update_encounter(
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
    deleted = encounter_store.delete_encounter(created_encounter.id)
    assert deleted is True

    # Verify deletion
    deleted_encounter = encounter_store.get_encounter_by_id(created_encounter.id)
    assert deleted_encounter is None

    # Test delete non-existent encounter
    deleted_again = encounter_store.delete_encounter(created_encounter.id)
    assert deleted_again is False

    # Verify remaining encounters
    remaining_encounters = encounter_store.get_all_encounters()
    assert (
        len(remaining_encounters) == 1
    )  # Only the one without characters should remain
