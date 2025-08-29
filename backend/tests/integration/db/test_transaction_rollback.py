#!/usr/bin/env python3
"""
Integration test for transaction rollback functionality.
Tests that database operations properly rollback on errors within the session lifecycle.
"""
import os

import pytest

from app.data.character_store import CharacterStore
from app.data.encounter_store import EncounterStore
from app.db.connection import get_db_session
from app.models.character import CharacterCreate
from tests.fixtures.generate import default_character


def test_transaction_rollback_on_error():
    """Test that multiple operations rollback completely when an error occurs within the session"""
    url = os.getenv("TEST_DATABASE_URL")

    # Count characters and encounters before test
    with get_db_session(db_url=url) as session:
        character_store = CharacterStore(user_id=1, world_id=1, session=session)
        initial_character_count = len(character_store.get_all_characters())
        encounter_store = EncounterStore(user_id=1, world_id=1, session=session)
        initial_encounter_count = len(encounter_store.get_all_encounters())

    # Attempt transaction that should fail - error happens WITHIN session context
    with pytest.raises(ValueError):
        with get_db_session(db_url=url) as session:
            character_store = CharacterStore(user_id=1, world_id=1, session=session)
            encounter_store = EncounterStore(user_id=1, world_id=1, session=session)

            # Use generator function and model_dump to create character data
            character = default_character()
            character_data = CharacterCreate(**character.model_dump(exclude={"id"}))

            # Create character in session
            character_store.create_character(character_data)

            # At this point character exists in session but not yet committed
            # Now force an error WITHIN the session:
            raise ValueError("Simulated error to test rollback")

    # Verify nothing was committed - counts should be unchanged
    with get_db_session(db_url=url) as session:
        character_store = CharacterStore(user_id=1, world_id=1, session=session)
        final_character_count = len(character_store.get_all_characters())
        encounter_store = EncounterStore(user_id=1, world_id=1, session=session)
        final_encounter_count = len(encounter_store.get_all_encounters())

        assert (
            final_character_count == initial_character_count
        ), "Character should have been rolled back"
        assert (
            final_encounter_count == initial_encounter_count
        ), "Encounter should have been rolled back"
