#!/usr/bin/env python3
import os

from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart
from sqlalchemy import create_engine

from app.data.character_store import CharacterStore
from app.data.conversation_store import ConversationStore
from app.data.encounter_store import EncounterStore
from app.data.player_store import PlayerStore
from app.models.alignment import Alignment
from app.models.character import CharacterCreate
from app.models.class_traits import Abilities, Class, Skills
from app.models.conversation import ConversationCreate
from app.models.encounter import EncounterCreate
from app.models.player import PlayerCreate
from app.models.race import Gender, Race, Size


def test_conversation_store():
    url = os.getenv("TEST_DATABASE_URL")
    engine = create_engine(url)

    # Create stores for prerequisite data
    character_store = CharacterStore(user_id=1, world_id=1, engine=engine)
    player_store = PlayerStore(user_id=1, world_id=1, engine=engine)
    encounter_store = EncounterStore(user_id=1, world_id=1, engine=engine)
    conversation_store = ConversationStore(user_id=1, world_id=1, engine=engine)

    # Create test character
    character_data = CharacterCreate(
        name="Test Tavern Keeper",
        avatar=None,
        race=Race.LIGHTFOOT_HALFLING.value,
        size=Size.SMALL.value,
        alignment=Alignment.NEUTRAL_GOOD.value,
        gender=Gender.MALE.value,
        profession="Tavern Keeper",
        background="Friendly tavern keeper who knows all the local gossip.",
        communication_style="Chatty and welcoming, always ready with a story.",
        motivation="To keep customers happy and make money.",
        personality="Appreciates friendly conversation and local gossip sharing.",
        voice="MFZUKuGQUsGJPQjTS4wC",
        race_preferences={Race.LIGHTFOOT_HALFLING.value: 2},
        class_preferences={Class.BARD.value: 3},
        gender_preferences={Gender.FEMALE.value: 1},
        size_preferences={Size.SMALL.value: 1},
    )
    created_character = character_store.create_character(character_data)

    # Create test player
    player_data = PlayerCreate(
        name="Test Bard",
        appearance="A cheerful halfling with curly hair and bright eyes.",
        race=Race.LIGHTFOOT_HALFLING.value,
        class_name=Class.BARD.value,
        size=Size.SMALL.value,
        alignment=Alignment.CHAOTIC_GOOD.value,
        gender=Gender.FEMALE.value,
        abilities={Abilities.CHARISMA.value: 16},
        skills={
            Skills.PERSUASION.value: 7,
            Skills.DECEPTION.value: 3,
            Skills.INTIMIDATION.value: 2,
            Skills.PERFORMANCE.value: 6,
        },
    )
    created_player = player_store.create_player(player_data)

    # Create test encounter
    encounter_data = EncounterCreate(
        name="Test Tavern",
        description="A cozy tavern filled with warm candlelight and cheerful chatter.",
        position_x=200.0,
        position_y=150.0,
        character_ids=[created_character.id],
    )
    created_encounter = encounter_store.create_encounter(encounter_data)

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
    created_conversation = conversation_store.create(new_conversation_data)
    assert len(created_conversation.messages) == 2

    retrieved_conversation = conversation_store.get(
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

    updated_conversation = conversation_store.add_messages(
        player_id=created_player.id,
        character_id=created_character.id,
        encounter_id=created_encounter.id,
        new_messages=new_messages,
    )
    assert updated_conversation is not None
    assert len(updated_conversation.messages) == 4

    exists = conversation_store.conversation_exists(
        player_id=created_player.id,
        character_id=created_character.id,
        encounter_id=created_encounter.id,
    )
    assert exists is True

    deleted = conversation_store.delete_conversation(
        player_id=created_player.id,
        character_id=created_character.id,
        encounter_id=created_encounter.id,
    )
    assert deleted is True

    exists_after_delete = conversation_store.conversation_exists(
        player_id=created_player.id,
        character_id=created_character.id,
        encounter_id=created_encounter.id,
    )
    assert exists_after_delete is False
