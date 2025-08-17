from typing import List

from fastapi import APIRouter, HTTPException

from app.agents.personality_agent import PersonalityGenerator
from app.data.character_store import CharacterStore
from app.models.character import Character, CharacterCreate, CharacterUpdate

router = APIRouter(prefix="/api/characters", tags=["characters"])


@router.get("", response_model=List[Character])
async def get_characters():
    """Get all characters"""
    return CharacterStore().get_all_characters()


@router.get("/{character_id}", response_model=Character)
async def get_character(character_id: int):
    """Get a specific character by ID"""
    character = CharacterStore().get_character_by_id(character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.post("/", response_model=Character, status_code=201)
async def create_character(character_data: CharacterCreate):
    """Create a new character with AI-generated personality"""
    # Generate personality profile
    personality = await PersonalityGenerator.generate_personality(character_data)

    # Create new CharacterCreate object with generated personality
    character_with_personality = CharacterCreate(
        **character_data.model_dump(), personality=personality
    )

    return CharacterStore().create_character(character_with_personality)


@router.put("/{character_id}", response_model=Character)
async def update_character(character_id: int, character_update: CharacterUpdate):
    """Update an existing character"""
    character = CharacterStore().update_character(character_id, character_update)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character


@router.delete("/{character_id}", status_code=204)
async def delete_character(character_id: int):
    """Delete a character"""
    success = CharacterStore().delete_character(character_id)
    if not success:
        raise HTTPException(status_code=404, detail="Character not found")
    return None
