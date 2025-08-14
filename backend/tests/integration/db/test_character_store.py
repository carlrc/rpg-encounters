#!/usr/bin/env python3
from dotenv import load_dotenv

from app.data.character_store import CharacterStore
from app.db.init_db import create_tables, drop_tables
from app.models.alignment import Alignment
from app.models.character import CharacterCreate, CharacterUpdate
from app.models.class_traits import Class
from app.models.race import Gender, Race, Size


def test_character_store():
    load_dotenv()

    create_tables()

    store = CharacterStore()

    new_character_data = CharacterCreate(
        name="Test Wizard",
        avatar=None,
        race=Race.HIGH_ELF.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.CHAOTIC_GOOD.value,
        gender=Gender.FEMALE.value,
        profession="Court Wizard",
        background="A wise elf who studied magic in the ancient libraries of her homeland.",
        communication_style="Speaks with measured words and ancient wisdom, often referencing old texts and magical theory.",
        motivation="Seeks to preserve ancient magical knowledge and protect the realm from dark forces.",
        personality="",
        voice="JBFqnCBsd6RMkjVDRZzb",
        race_preferences={Race.HIGH_ELF.value: 2, Race.HUMAN.value: 1},
        class_preferences={Class.WIZARD.value: 3, Class.SORCERER.value: 1},
        gender_preferences={Gender.FEMALE.value: 1},
        size_preferences={Size.MEDIUM.value: 1},
    )

    created_character = store.create_character(new_character_data)
    assert created_character.name == "Test Wizard"

    all_characters = store.get_all_characters()
    assert len(all_characters) >= 1

    retrieved_character = store.get_character_by_id(created_character.id)
    assert retrieved_character is not None

    update_data = CharacterUpdate(
        name="Updated Test Wizard",
        profession="Archmage",
        background="An experienced elf who has mastered the arcane arts and now leads the magical council.",
    )
    updated_character = store.update_character(created_character.id, update_data)
    assert updated_character is not None
    assert updated_character.name == "Updated Test Wizard"
    assert updated_character.profession == "Archmage"

    exists = store.character_exists(created_character.id)
    assert exists is True

    deleted = store.delete_character(created_character.id)
    assert deleted is True

    exists_after_delete = store.character_exists(created_character.id)
    assert exists_after_delete is False

    drop_tables()
