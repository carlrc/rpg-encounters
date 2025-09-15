import logging
from typing import List, Union

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

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
from app.moderation.check import moderate_character

router = APIRouter(prefix="/api/characters", tags=["characters"])

logger = logging.getLogger(__name__)


async def _generate_personality_background(
    character_id: int,
    character_data: Union[CharacterCreate, CharacterUpdate],
    user_id: int,
    world_id: int,
) -> None:
    """Generate personality in background and update character"""
    try:
        # Generate personality
        personality = await PersonalityAgent().generate(character_data)

        # Update character with generated personality
        character_store = CharacterStore(user_id=user_id, world_id=world_id)
        update_data = CharacterUpdate(personality=personality)

        await character_store.update(character_id, update_data)

        logger.info(f"Created personality for user {user_id} in background task...")
    except Exception as e:
        logger.error(
            f"Background personality generation task for user {user_id} error: {e}"
        )
        raise


async def _generate_communication_style_background(
    character_id: int,
    character_data: Union[CharacterCreate, CharacterUpdate],
    user_id: int,
    world_id: int,
) -> None:
    """Generate communication style in background and update character"""
    try:
        if character_data.communication_style_type == CommunicationStyle.CUSTOM.value:
            return

        system_prompt = render_prompt(
            "communication_style_agent",
            {
                "character": character_data,
                "style_profile": COMMUNICATION_STYLE_PROFILES[
                    character_data.communication_style_type
                ],
                "max_response_length": CHARACTER_COMMUNICATION_LIMIT,
            },
        )

        communication_style = await CommunicationStyleAgent(
            system_prompt=system_prompt
        ).generate()

        update_data = CharacterUpdate(
            communication_style=communication_style.style_summary,
            communication_style_examples=communication_style.examples,
        )

        await CharacterStore(user_id=user_id, world_id=world_id).update(
            character_id, update_data
        )

        logger.info(
            f"Created communication style for user {user_id} in background task..."
        )
    except Exception as e:
        logger.error(
            f"Background communication style generation task for user {user_id} error: {e}"
        )
        raise


@router.get("", response_model=List[Character])
async def get_characters(
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Get all characters"""
    user_id, world_id = user_world
    try:
        return await CharacterStore(user_id=user_id, world_id=world_id).get_all()
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
        character = await CharacterStore(user_id=user_id, world_id=world_id).get_by_id(
            character_id
        )
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
    background_tasks: BackgroundTasks,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Create a new character and generate AI content in background"""
    user_id, world_id = user_world
    try:
        # Moderate character fields
        character_data = await moderate_character(
            user_id=user_id, character_data=character_data
        )

        # Create character immediately without AI-generated content
        # personality field defaults to empty string
        character = await CharacterStore(user_id=user_id, world_id=world_id).create(
            character_data
        )

        # TODO: If moderated we would want to skip incurring this computation cost
        # Add background tasks for AI generation
        background_tasks.add_task(
            _generate_personality_background,
            character_id=character.id,
            character_data=character_data,
            user_id=user_id,
            world_id=world_id,
        )

        background_tasks.add_task(
            _generate_communication_style_background,
            character_id=character.id,
            character_data=character_data,
            user_id=user_id,
            world_id=world_id,
        )

        logger.debug(
            f"Created character for user {user_id} and queued background AI generation..."
        )
        return character

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
    background_tasks: BackgroundTasks,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Update an existing character and regenerate AI content in background if needed"""
    user_id, world_id = user_world
    try:
        character_store = CharacterStore(user_id=user_id, world_id=world_id)
        # Ensure the character exists first
        character = await character_store.get_by_id(character_id=character_id)
        if not character:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)

        # Moderate character fields
        character_update = await moderate_character(
            user_id=user_id, character_data=character_update
        )

        # Update character immediately (without AI regeneration)
        updated_character = await character_store.update(character_id, character_update)

        # Add background tasks only if fields that affect AI generation changed
        needs_personality_regen = (
            character_update.background or character_update.motivation
        )
        needs_communication_regen = (
            character_update.communication_style_type
            or character_update.communication_style
        )

        if needs_personality_regen:
            # Merge existing character with updates for AI generation
            merged_data = character.model_dump()
            merged_data.update(character_update.model_dump(exclude_unset=True))
            merged_character = CharacterUpdate(**merged_data)

            background_tasks.add_task(
                _generate_personality_background,
                character_id,
                merged_character,
                user_id,
                world_id,
            )

        if needs_communication_regen:
            # Merge existing character with updates for AI generation
            merged_data = character.model_dump()
            merged_data.update(character_update.model_dump(exclude_unset=True))
            merged_character = CharacterUpdate(**merged_data)

            background_tasks.add_task(
                _generate_communication_style_background,
                character_id,
                merged_character,
                user_id,
                world_id,
            )

        return updated_character

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
        success = await CharacterStore(user_id=user_id, world_id=world_id).delete(
            character_id
        )
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
