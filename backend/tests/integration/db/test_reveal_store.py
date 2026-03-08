#!/usr/bin/env python3

from app.data.character_store import CharacterStore
from app.data.reveal_store import RevealStore
from app.db.connection import get_async_db_session
from app.models.character import CharacterCreate
from app.models.reveal import RevealCreate, RevealUpdate
from app.utils import get_or_throw
from tests.fixtures.generate import default_character


async def test_reveal_store():
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        character_store = CharacterStore(user_id=1, world_id=1, session=session)

        # Use generate function
        character = default_character()
        character1_data = CharacterCreate(**character.model_dump(exclude={"id"}))

        created_character1 = await character_store.create(character1_data)

        # Now create reveal with actual character IDs
        reveal_store = RevealStore(user_id=1, world_id=1, session=session)

        new_reveal_data = RevealCreate(
            title="Hidden Treasure",
            character_ids=[created_character1.id],
            level_1_content="There's something valuable hidden in the old ruins.",
            level_2_content="A chest of gold coins is buried beneath the altar.",
            level_3_content="The chest contains 500 gold pieces and a magical amulet of protection.",
            standard_threshold=0,
            privileged_threshold=15,
            exclusive_threshold=20,
        )

        created_reveal = await reveal_store.create(new_reveal_data)
        assert created_reveal.title == new_reveal_data.title
        assert created_reveal.id is not None
        assert created_reveal.character_ids == [created_character1.id]
        assert created_reveal.level_1_content == new_reveal_data.level_1_content
        assert created_reveal.level_2_content == new_reveal_data.level_2_content
        assert created_reveal.level_3_content == new_reveal_data.level_3_content
        assert created_reveal.standard_threshold == new_reveal_data.standard_threshold
        assert (
            created_reveal.privileged_threshold == new_reveal_data.privileged_threshold
        )
        assert created_reveal.exclusive_threshold == new_reveal_data.exclusive_threshold

        all_reveals = await reveal_store.get_all()
        assert len(all_reveals) == 1

        retrieved_reveal = await reveal_store.get_by_id(created_reveal.id)
        assert retrieved_reveal is not None

        retrieved_reveal_alias = await reveal_store.get_by_id(created_reveal.id)
        assert retrieved_reveal_alias is not None

        character_reveals = await reveal_store.get_by_character_id(
            created_character1.id
        )
        assert len(character_reveals) == 1

        update_data = RevealUpdate(
            title="Updated Hidden Treasure",
            standard_threshold=5,
            privileged_threshold=10,
            exclusive_threshold=15,
        )
        updated_reveal = await reveal_store.update(created_reveal.id, update_data)
        assert updated_reveal is not None
        assert updated_reveal.standard_threshold == update_data.standard_threshold
        assert updated_reveal.privileged_threshold == update_data.privileged_threshold
        assert updated_reveal.exclusive_threshold == update_data.exclusive_threshold

        exists = await reveal_store.exists(created_reveal.id)
        assert exists is True

        deleted = await reveal_store.delete(created_reveal.id)
        assert deleted is True

        exists_after_delete = await reveal_store.exists(created_reveal.id)
        assert exists_after_delete is False
