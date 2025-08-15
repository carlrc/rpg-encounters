#!/usr/bin/env python3
import pytest
from dotenv import load_dotenv

from app.data.character_store import CharacterStore
from app.data.memory_store import MemoryStore
from app.db.init_db import create_tables, drop_tables
from app.models.alignment import Alignment
from app.models.character import CharacterCreate
from app.models.class_traits import Class
from app.models.memory import MemoryCreate, MemoryUpdate
from app.models.race import Gender, Race, Size


@pytest.fixture(autouse=True)
def setup_teardown():
    """Setup and teardown for each test"""
    load_dotenv()
    create_tables()
    yield
    drop_tables()


def test_memory_store():
    # Create characters first
    character_store = CharacterStore()

    character1_data = CharacterCreate(
        name="Test Wizard",
        avatar=None,
        race=Race.HIGH_ELF.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.CHAOTIC_GOOD.value,
        gender=Gender.FEMALE.value,
        profession="Court Wizard",
        background="A wise elf who studied magic in the ancient libraries.",
        communication_style="Speaks with measured words and ancient wisdom.",
        motivation="Seeks to preserve ancient magical knowledge.",
        personality="",
        voice="JBFqnCBsd6RMkjVDRZzb",
        race_preferences={Race.HIGH_ELF.value: 2},
        class_preferences={Class.WIZARD.value: 3},
        gender_preferences={Gender.FEMALE.value: 1},
        size_preferences={Size.MEDIUM.value: 1},
    )

    created_character1 = character_store.create_character(character1_data)

    # Now create memory with actual character IDs
    memory_store = MemoryStore()

    new_memory_data = MemoryCreate(
        title="Ancient Battle",
        content="A fierce battle took place at the old bridge where brave warriors fought against dark creatures from the shadow realm.",
        character_ids=[created_character1.id],
    )

    created_memory = memory_store.create_memory(new_memory_data)
    assert created_memory.title == "Ancient Battle"
    assert created_memory.id is not None
    assert created_memory.character_ids == [created_character1.id]

    all_memories = memory_store.get_all_memories()
    assert len(all_memories) >= 1

    retrieved_memory = memory_store.get_memory(created_memory.id)
    assert retrieved_memory is not None
    assert retrieved_memory.title == "Ancient Battle"

    retrieved_memory_alias = memory_store.get_by_id(created_memory.id)
    assert retrieved_memory_alias is not None
    assert retrieved_memory_alias.title == "Ancient Battle"

    character_memories = memory_store.get_by_character_id(created_character1.id)
    assert len(character_memories) >= 1
    assert any(memory.id == created_memory.id for memory in character_memories)

    update_data = MemoryUpdate(
        title="Updated Ancient Battle",
        content="An epic battle took place at the old stone bridge where legendary heroes fought valiantly against the forces of darkness.",
        character_ids=[created_character1.id],
    )
    updated_memory = memory_store.update_memory(created_memory.id, update_data)
    assert updated_memory is not None
    assert updated_memory.title == "Updated Ancient Battle"

    exists = memory_store.memory_exists(created_memory.id)
    assert exists is True

    deleted = memory_store.delete_memory(created_memory.id)
    assert deleted is True

    exists_after_delete = memory_store.memory_exists(created_memory.id)
    assert exists_after_delete is False
