import logging
from typing import List

from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage
from sqlalchemy.orm import Session

from app.data.conversation_store import ConversationStore
from app.data.encounter_store import EncounterStore
from app.data.influence_store import InfluenceStore
from app.data.memory_store import MemoryStore
from app.data.reveal_store import RevealStore
from app.models.conversation import ConversationCreate
from app.models.encounter import Encounter
from app.models.influence import Influence
from app.models.memory import Memory
from app.models.reveal import Reveal

logger = logging.getLogger(__name__)


class ConvoContext(BaseModel):
    encounter: Encounter
    influence: Influence
    reveals: List[Reveal]
    memories: List[Memory]
    messages: List[ModelMessage] | None


def get_conversation_context(
    world_id: int,
    player_id: int,
    user_id: int,
    character_id: int,
    encounter_id: int,
    base_influence: int,
    session: Session,
) -> ConvoContext:
    """
    Get all conversation-related data for a character using the provided database session.
    Auto-adds character to encounter if not already present.
    """
    try:
        # Create store instances with shared session
        encounter_store = EncounterStore(
            user_id=user_id, world_id=world_id, session=session
        )
        reveal_store = RevealStore(user_id=user_id, world_id=world_id, session=session)
        memory_store = MemoryStore(user_id=user_id, world_id=world_id, session=session)
        conversation_store = ConversationStore(
            user_id=user_id, world_id=world_id, session=session
        )
        influence_store = InfluenceStore(
            user_id=user_id, world_id=world_id, session=session
        )

        # Get encounter
        encounter = encounter_store.get_encounter_by_id(encounter_id)
        if not encounter:
            raise ValueError(f"Encounter {encounter_id} not found")

        # Auto-add character to encounter if not already present
        if character_id not in encounter.character_ids:
            encounter_store.add_character_to_encounter(encounter_id, character_id)
            # Refresh encounter data after adding character
            encounter = encounter_store.get_encounter_by_id(encounter_id)

        # Get all related data using shared session
        reveals = reveal_store.get_by_character_id(character_id)
        memories = memory_store.get_by_character_id(character_id)

        # Get or create conversation
        conversation = conversation_store.get(player_id, character_id, encounter_id)
        if not conversation:
            conversation_data = ConversationCreate(
                player_id=player_id,
                character_id=character_id,
                encounter_id=encounter_id,
                messages=[],
            )
            conversation = conversation_store.create(conversation_data)

        # Get or create influence
        influence = influence_store.get_or_create(
            character_id, player_id, base_influence
        )

        # Extract messages
        messages = conversation.messages if conversation else None

        return ConvoContext(
            encounter=encounter,
            influence=influence,
            reveals=reveals,
            memories=memories,
            messages=messages,
        )
    except Exception as e:
        logger.error(f"Failed to get conversation context: {e}")
        raise e
