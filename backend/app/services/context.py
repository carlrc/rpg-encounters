import logging
from typing import List

from fastapi import HTTPException
from langfuse import observe
from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.data.account_store import AccountStore
from app.data.character_store import CharacterStore
from app.data.conversation_store import ConversationStore
from app.data.encounter_store import EncounterStore
from app.data.influence_store import InfluenceStore
from app.data.memory_store import MemoryStore
from app.data.player_store import PlayerStore
from app.data.reveal_store import RevealStore
from app.db.connection import get_async_db_session
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
    elevenlabs_token: str | None


# We don't want to have DB records in telemetry
@observe(capture_output=False)
async def get_conversation_context(
    world_id: int,
    player_id: int,
    user_id: int,
    character_id: int,
    encounter_id: int,
    session: AsyncSession | None = None,
) -> ConvoContext:
    """
    Get all conversation-related data for a character using the provided database session.
    Auto-adds character to encounter if not already present.
    """
    try:
        if not session:
            async with get_async_db_session() as session:
                return await get_conversation_context(
                    world_id, player_id, user_id, character_id, encounter_id, session
                )

        # Create store instances with shared session
        character_store = CharacterStore(
            user_id=user_id, world_id=world_id, session=session
        )
        player_store = PlayerStore(user_id=user_id, world_id=world_id, session=session)
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
        account_store = AccountStore(user_id=user_id, session=session)

        # Get character and player data
        character = await character_store.get_by_id(character_id)
        player = await player_store.get_by_id(player_id)
        user_account = await account_store.get_account_by_user_id(user_id=user_id)

        if not character or not player or not user_account:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)

        base_influence = calculate_base_influence(character=character, player=player)

        # Get encounter
        encounter = await encounter_store.get_by_id(encounter_id)
        if not encounter:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)

        # Auto-add character to encounter if not already present (e.g., canvas not saved but character added)
        if character_id not in encounter.character_ids:
            await encounter_store.add_character_to_encounter(encounter_id, character_id)
            # Refresh encounter data after adding character
            encounter = await encounter_store.get_by_id(encounter_id)

        # Get all related data
        reveals = await reveal_store.get_by_character_id(character_id)
        memories = await memory_store.get_by_character_id(character_id)

        # Get or create conversation
        conversation = await conversation_store.get(
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
            conversation = await conversation_store.create(conversation_data)

        # Get or create influence
        influence = await influence_store.get_or_create_influence(
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
            character=character,
            player=player,
            elevenlabs_token=user_account.elevenlabs_token,
        )
    except Exception as e:
        logger.error(f"Failed to get conversation context: {e}")
        raise e
