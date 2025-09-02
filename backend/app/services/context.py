import asyncio
import functools
import logging
from typing import List

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage

from app.data.character_store import CharacterStore
from app.data.conversation_store import ConversationStore
from app.data.encounter_store import EncounterStore
from app.data.influence_store import InfluenceStore
from app.data.memory_store import MemoryStore
from app.data.player_store import PlayerStore
from app.data.reveal_store import RevealStore
from app.db.connection import get_db_session
from app.http import ENTITY_NOT_FOUND
from app.models.character import Character
from app.models.conversation import ConversationCreate
from app.models.encounter import Encounter
from app.models.influence import Influence
from app.models.memory import Memory
from app.models.player import Player
from app.models.reveal import Reveal
from app.services.influence_calculator import calculate_base_influence

logger = logging.getLogger(__name__)


class ConvoContext(BaseModel):
    encounter: Encounter
    influence: Influence
    reveals: List[Reveal]
    memories: List[Memory]
    character: Character
    player: Player
    messages: List[ModelMessage] | None


async def get_conversation_context_async(
    world_id: int,
    player_id: int,
    user_id: int,
    character_id: int,
    encounter_id: int,
) -> ConvoContext:
    """Async version that runs sync function in executor thread"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        functools.partial(
            get_conversation_context,
            world_id=world_id,
            player_id=player_id,
            user_id=user_id,
            character_id=character_id,
            encounter_id=encounter_id,
        ),
    )


def get_conversation_context(
    world_id: int,
    player_id: int,
    user_id: int,
    character_id: int,
    encounter_id: int,
) -> ConvoContext:
    """
    Get all conversation-related data for a character using the provided database session.
    Auto-adds character to encounter if not already present.
    """
    try:
        with get_db_session() as session:
            # Create store instances with shared session
            character = CharacterStore(
                world_id=world_id, user_id=user_id, session=session
            ).get_character_by_id(character_id=character_id)
            player = PlayerStore(
                world_id=world_id, user_id=user_id, session=session
            ).get_player_by_id(player_id=player_id)

            if not character or not player:
                raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)

            base_influence = calculate_base_influence(
                character=character, player=player
            )
            encounter_store = EncounterStore(
                user_id=user_id, world_id=world_id, session=session
            )
            reveal_store = RevealStore(
                user_id=user_id, world_id=world_id, session=session
            )
            memory_store = MemoryStore(
                user_id=user_id, world_id=world_id, session=session
            )
            conversation_store = ConversationStore(
                user_id=user_id, world_id=world_id, session=session
            )
            influence_store = InfluenceStore(
                user_id=user_id, world_id=world_id, session=session
            )

            # Get encounter
            encounter = encounter_store.get_encounter_by_id(encounter_id=encounter_id)
            if not encounter:
                raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)

            # Auto-add character to encounter if not already present
            if character_id not in encounter.character_ids:
                encounter_store.add_character_to_encounter(
                    encounter_id=encounter_id, character_id=character_id
                )
                # Refresh encounter data after adding character
                encounter = encounter_store.get_encounter_by_id(
                    encounter_id=encounter_id
                )

            # Get all related data using shared session
            reveals = reveal_store.get_by_character_id(character_id=character_id)
            memories = memory_store.get_by_character_id(character_id=character_id)

            # Get or create conversation
            conversation = conversation_store.get(
                player_id=player_id,
                character_id=character_id,
                encounter_id=encounter_id,
            )
            if not conversation:
                conversation_data = ConversationCreate(
                    player_id=player_id,
                    character_id=character_id,
                    encounter_id=encounter_id,
                    messages=[],
                )
                conversation = conversation_store.create(
                    conversation_data=conversation_data
                )

            # Get or create influence
            influence = influence_store.get_or_create(
                character_id=character_id, player_id=player_id, base=base_influence
            )

            # Extract messages
            messages = conversation.messages if conversation else None

            return ConvoContext(
                encounter=encounter,
                influence=influence,
                reveals=reveals,
                memories=memories,
                messages=messages,
                character=character,
                player=player,
            )
    except Exception as e:
        logger.error(f"Failed to get conversation context: {e}")
        raise e
