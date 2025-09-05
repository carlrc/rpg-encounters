#!/usr/bin/env python3
import os

from app.data.character_store import CharacterStore
from app.data.memory_store import MemoryStore
from app.db.connection import get_async_db_session
from app.models.character import CharacterCreate
from app.models.memory import MemoryCreate, MemoryUpdate
from tests.fixtures.generate import default_character


async def test_memory_store():
    url = os.getenv("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        character_store = CharacterStore(user_id=1, world_id=1, session=session)

        # Use generate function
        character = default_character()
        character1_data = CharacterCreate(**character.model_dump(exclude={"id"}))

        created_character1 = await character_store.create(character1_data)

        # Now create memory with actual character IDs
        memory_store = MemoryStore(user_id=1, world_id=1, session=session)

        new_memory_data = MemoryCreate(
            title="Ancient Battle",
            content="A fierce battle took place at the old bridge where brave warriors fought against dark creatures from the shadow realm.",
            character_ids=[created_character1.id],
        )

        created_memory = await memory_store.create(new_memory_data)
        assert created_memory.title == "Ancient Battle"
        assert created_memory.id is not None
        assert created_memory.character_ids == [created_character1.id]

        all_memories = await memory_store.get_all()
        assert len(all_memories) >= 1

        retrieved_memory = await memory_store.get_by_id(created_memory.id)
        assert retrieved_memory is not None
        assert retrieved_memory.title == "Ancient Battle"

        retrieved_memory_alias = await memory_store.get_by_id(created_memory.id)
        assert retrieved_memory_alias is not None
        assert retrieved_memory_alias.title == "Ancient Battle"

        character_memories = await memory_store.get_by_character_id(
            created_character1.id
        )
        assert len(character_memories) >= 1
        assert any(memory.id == created_memory.id for memory in character_memories)

        update_data = MemoryUpdate(
            title="Updated Ancient Battle",
            content="An epic battle took place at the old stone bridge where legendary heroes fought valiantly against the forces of darkness.",
            character_ids=[created_character1.id],
        )
        updated_memory = await memory_store.update(created_memory.id, update_data)
        assert updated_memory is not None
        assert updated_memory.title == "Updated Ancient Battle"

        exists = await memory_store.exists(created_memory.id)
        assert exists is True

        deleted = await memory_store.delete(created_memory.id)
        assert deleted is True

        exists_after_delete = await memory_store.exists(created_memory.id)
        assert exists_after_delete is False
