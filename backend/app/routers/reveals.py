from typing import List

from fastapi import APIRouter, HTTPException

from app.data.character_store import CharacterStore
from app.data.reveal_store import RevealStore
from app.models.reveal import Reveal, RevealCreate, RevealUpdate

router = APIRouter(prefix="/api/reveals", tags=["reveals"])


@router.get("", response_model=List[Reveal])
def get_all_reveals():
    """Get all reveals across all characters"""
    return RevealStore().get_all_reveals()


@router.post("", response_model=Reveal)
def create_reveal(reveal_data: RevealCreate):
    """Create a reveal for multiple characters"""
    # Verify all characters exist
    for character_id in reveal_data.character_ids:
        if not CharacterStore().character_exists(character_id):
            raise HTTPException(
                status_code=404, detail=f"Character {character_id} not found"
            )

    return RevealStore().create_reveal(reveal_data)


@router.get("/{reveal_id}", response_model=Reveal)
def get_reveal(reveal_id: int):
    """Get a specific reveal by ID"""
    reveal = RevealStore().get_reveal(reveal_id)
    if not reveal:
        raise HTTPException(status_code=404, detail="Reveal not found")
    return reveal


@router.get("/character/{character_id}", response_model=List[Reveal])
def get_character_reveals(character_id: int):
    """Get all reveals for a character"""
    # Verify character exists
    if not CharacterStore().character_exists(character_id):
        raise HTTPException(status_code=404, detail="Character not found")

    return RevealStore().get_by_character_id(character_id)


@router.put("/{reveal_id}", response_model=Reveal)
def update_reveal(reveal_id: int, reveal_update: RevealUpdate):
    """Update a reveal"""
    # Verify all characters exist if character_ids are being updated
    if reveal_update.character_ids:
        for character_id in reveal_update.character_ids:
            if not CharacterStore().character_exists(character_id):
                raise HTTPException(
                    status_code=404, detail=f"Character {character_id} not found"
                )

    reveal = RevealStore().update_reveal(reveal_id, reveal_update)
    if not reveal:
        raise HTTPException(status_code=404, detail="Reveal not found")
    return reveal


@router.delete("/{reveal_id}")
def delete_reveal(reveal_id: int):
    """Delete a reveal"""
    success = RevealStore().delete_reveal(reveal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reveal not found")
    return {"message": "Reveal deleted successfully"}
