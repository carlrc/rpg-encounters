import asyncio
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.agents.communication_style_agent import (
    COMMUNICATION_STYLE_PROFILES,
    CommunicationStyleAgent,
)
from app.agents.personality_agent import PersonalityAgent
from app.agents.prompts.import_prompts import render_prompt
from app.data.character_store import CharacterStore
from app.db.limits import CHARACTER_COMMUNICATION_LIMIT
from app.dependencies import get_current_user_world
from app.http import ENTITY_NOT_FOUND, INTERNAL_SERVER_ERROR
from app.models.character import (
    Character,
    CharacterCreate,
    CharacterUpdate,
    CommunicationStyle,
)

router = APIRouter(prefix="/api/characters", tags=["characters"])

logger = logging.getLogger(__name__)


def _generate_communication_style_task(character):
    """Generate communication style task if not custom style type."""

    if character.communication_style_type == CommunicationStyle.CUSTOM.value:
        return None

    system_prompt = render_prompt(
        "communication_style_agent",
        {
            "character": character,
            "style_profile": COMMUNICATION_STYLE_PROFILES[
                character.communication_style_type
            ],
            "max_response_length": CHARACTER_COMMUNICATION_LIMIT,
        },
    )
    return CommunicationStyleAgent(system_prompt=system_prompt).generate(character)


@router.get("", response_model=List[Character])
async def get_characters(
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Get all characters"""
    user_id, world_id = user_world
    try:
        return await CharacterStore(
            user_id=user_id, world_id=world_id
        ).get_all_characters()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get characters for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.get("/{character_id}", response_model=Character)
async def get_character(
    character_id: int,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Get a specific character by ID"""
    user_id, world_id = user_world
    try:
        character = await CharacterStore(
            user_id=user_id, world_id=world_id
        ).get_character_by_id(character_id)
        if not character:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return character
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get character {character_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.post("", response_model=Character, status_code=201)
async def create_character(
    character_data: CharacterCreate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Create a new character with AI-generated personality"""
    user_id, world_id = user_world
    try:
        communication_task = _generate_communication_style_task(character_data)
        if communication_task:
            communication_style = await communication_task
            character_data.communication_style = communication_style.style_summary
            character_data.communication_style_examples = communication_style.examples

        # For CUSTOM communication style, only generate personality and leave custom communication style
        character_data.personality = await PersonalityAgent().generate(character_data)

        # Create character with generated summaries
        character = CharacterCreate(**character_data.model_dump())

        return await CharacterStore(
            user_id=user_id, world_id=world_id
        ).create_character(character)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to create character for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.put("/{character_id}", response_model=Character)
async def update_character(
    character_id: int,
    character_update: CharacterUpdate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Update an existing character"""
    user_id, world_id = user_world
    try:
        character_store = CharacterStore(user_id=user_id, world_id=world_id)
        # Because generating content with LLMs is expensive, ensure the character exists first
        character = await character_store.get_character_by_id(character_id=character_id)
        if not character:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)

        # Only regenerate personality if background or motivation changed
        personality_task = None
        if character_update.background or character_update.motivation:
            # Merge existing character with updates for AI generation
            merged_data = character.model_dump()
            merged_data.update(character_update.model_dump(exclude_unset=True))
            merged_character = CharacterUpdate(**merged_data)
            personality_task = PersonalityAgent().generate(merged_character)

        communication_task = None
        if (
            character_update.communication_style_type
            or character_update.communication_style
        ):
            communication_task = _generate_communication_style_task(merged_character)

        # Run tasks concurrently with defaults for consistent unpacking
        async def null_task():
            return None

        personality_task = personality_task or null_task()
        communication_task = communication_task or null_task()

        personality, communication_style = await asyncio.gather(
            personality_task, communication_task
        )

        if personality is not None:
            character_update.personality = personality

        if communication_style is not None:
            character_update.communication_style = communication_style.style_summary
            character_update.communication_style_examples = communication_style.examples

        return await character_store.update_character(character_id, character_update)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update character {character_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.delete("/{character_id}", status_code=204)
async def delete_character(
    character_id: int,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Delete a character"""
    user_id, world_id = user_world
    try:
        success = await CharacterStore(
            user_id=user_id, world_id=world_id
        ).delete_character(character_id)
        if not success:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete character {character_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)
