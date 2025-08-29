#!/usr/bin/env python3
import os

from app.data.character_store import CharacterStore
from app.db.connection import get_db_session
from app.models.character import CharacterCreate, CharacterUpdate
from tests.fixtures.generate import default_character


def test_character_store():
    url = os.getenv("TEST_DATABASE_URL")
    with get_db_session(url) as session:
        store = CharacterStore(user_id=1, world_id=1, session=session)

        # Use generate function for character creation
        character = default_character()
        new_character_data = CharacterCreate(**character.model_dump(exclude={"id"}))

        created_character = store.create_character(new_character_data)
        assert created_character.name == character.name

        all_characters = store.get_all_characters()
        assert len(all_characters) >= 1

        retrieved_character = store.get_character_by_id(created_character.id)
        assert retrieved_character is not None

        update_data = CharacterUpdate(
            name="Updated " + character.name,
            profession="Archmage",
        )
        updated_character = store.update_character(created_character.id, update_data)
        assert updated_character is not None
        assert updated_character.name == "Updated " + character.name
        assert updated_character.profession == "Archmage"

        exists = store.character_exists(created_character.id)
        assert exists is True

        deleted = store.delete_character(created_character.id)
        assert deleted is True

        exists_after_delete = store.character_exists(created_character.id)
        assert exists_after_delete is False
