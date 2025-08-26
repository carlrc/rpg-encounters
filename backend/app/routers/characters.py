from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.agents.communication_style_agent import CommunicationStyleAgent
from app.agents.personality_agent import PersonalityAgent
from app.agents.prompts.import_prompts import import_system_prompt
from app.data.character_store import CharacterStore
from app.dependencies import get_current_user_world
from app.models.character import (
    Character,
    CharacterCreate,
    CharacterUpdate,
    CommunicationStyle,
)

router = APIRouter(prefix="/api/characters", tags=["characters"])


@router.get("", response_model=List[Character])
async def get_characters(user_world: tuple[int, int] = Depends(get_current_user_world)):
    """Get all characters"""
    user_id, world_id = user_world
    return CharacterStore(user_id=user_id, world_id=world_id).get_all_characters()


@router.get("/{character_id}", response_model=Character)
async def get_character(
    character_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Get a specific character by ID"""
    user_id, world_id = user_world
    character = CharacterStore(user_id=user_id, world_id=world_id).get_character_by_id(
        character_id
    )
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.post("", response_model=Character, status_code=201)
async def create_character(
    character_data: CharacterCreate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Create a new character with AI-generated personality"""
    user_id, world_id = user_world

    custom_style = (
        character_data.communication_style_type == CommunicationStyle.CUSTOM.value
    )
    if not custom_style:
        communication_style_agent = CommunicationStyleAgent(
            system_prompt=import_system_prompt("communication_style_agent")
        )

        communication_style = await communication_style_agent.generate(character_data)
        character_data.communication_style = communication_style.style_summary
        character_data.communication_style_examples = communication_style.examples

    # For CUSTOM communication style, only generate personality and leave custom communication style
    character_data.personality = await PersonalityAgent().generate(character_data)

    # Create character with generated summaries
    character = CharacterCreate(**character_data.model_dump())

    return CharacterStore(user_id=user_id, world_id=world_id).create_character(
        character
    )


@router.put("/{character_id}", response_model=Character)
async def update_character(
    character_id: int,
    character_update: CharacterUpdate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Update an existing character"""
    user_id, world_id = user_world
    character = CharacterStore(user_id=user_id, world_id=world_id).update_character(
        character_id, character_update
    )
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.delete("/{character_id}", status_code=204)
async def delete_character(
    character_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Delete a character"""
    user_id, world_id = user_world
    success = CharacterStore(user_id=user_id, world_id=world_id).delete_character(
        character_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Character not found")
    return None
