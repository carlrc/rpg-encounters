#!/usr/bin/env python3

from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart

from app.data.character_store import CharacterStore
from app.data.conversation_store import ConversationStore
from app.data.encounter_store import EncounterStore
from app.data.player_store import PlayerStore
from app.db.connection import get_async_db_session
from app.models.character import CharacterCreate
from app.models.conversation import ConversationCreate
from app.models.encounter import EncounterCreate
from app.models.player import PlayerCreate
from app.utils import get_or_throw
from tests.fixtures.generate import default_character, default_encounter, default_player


async def test_conversation_store():
    url = get_or_throw("TEST_DATABASE_URL")
    async with get_async_db_session(url) as session:
        # Create stores for prerequisite data
        character_store = CharacterStore(user_id=1, world_id=1, session=session)
        player_store = PlayerStore(user_id=1, world_id=1, session=session)
        encounter_store = EncounterStore(user_id=1, world_id=1, session=session)
        conversation_store = ConversationStore(user_id=1, world_id=1, session=session)

        # Use generate functions
        character = default_character()
        character_data = CharacterCreate(**character.model_dump(exclude={"id"}))
        created_character = await character_store.create(character_data)

        player = default_player()
        player_data = PlayerCreate(**player.model_dump(exclude={"id"}))
        created_player = await player_store.create(player_data)

        encounter = default_encounter()
        encounter_data = EncounterCreate(**encounter.model_dump(exclude={"id"}))
        encounter_data.character_ids = [created_character.id]
        encounter_data.player_ids = [created_player.id]
        created_encounter = await encounter_store.create(encounter_data)

        user_message = ModelRequest.user_text_prompt(
            "Hello, do you have any rooms available?"
        )
        initial_messages = [
            user_message,
            ModelResponse(
                parts=[
                    TextPart(
                        content="Welcome to our tavern! Yes, we have a lovely room available."
                    )
                ]
            ),
        ]

        new_conversation_data = ConversationCreate(
            player_id=created_player.id,
            character_id=created_character.id,
            encounter_id=created_encounter.id,
            messages=initial_messages,
        )
        created_conversation = await conversation_store.create(new_conversation_data)
        assert len(created_conversation.messages) == 2

        retrieved_conversation = await conversation_store.get(
            player_id=created_player.id,
            character_id=created_character.id,
            encounter_id=created_encounter.id,
        )
        assert retrieved_conversation is not None

        user_message = ModelRequest.user_text_prompt("What's the price for the room?")
        new_messages = [
            user_message,
            ModelResponse(
                parts=[
                    TextPart(
                        content="The room is 2 gold pieces per night, including breakfast."
                    )
                ]
            ),
        ]

        updated_conversation = await conversation_store.add_messages(
            player_id=created_player.id,
            character_id=created_character.id,
            encounter_id=created_encounter.id,
            new_messages=new_messages,
        )
        assert updated_conversation is not None
        assert len(updated_conversation.messages) == 4

        exists = await conversation_store.exists(
            player_id=created_player.id,
            character_id=created_character.id,
            encounter_id=created_encounter.id,
        )
        assert exists is True

        deleted = await conversation_store.delete(
            player_id=created_player.id,
            character_id=created_character.id,
            encounter_id=created_encounter.id,
        )
        assert deleted is True

        exists_after_delete = await conversation_store.exists(
            player_id=created_player.id,
            character_id=created_character.id,
            encounter_id=created_encounter.id,
        )
        assert exists_after_delete is False
