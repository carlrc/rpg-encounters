from fastapi import APIRouter, HTTPException
from typing import List
from app.models.reveal import Reveal, RevealCreate
from app.data.reveal_store import reveal_store
from app.data.character_store import character_store

router = APIRouter(prefix="/api/reveals", tags=["reveals"])


@router.get("", response_model=List[Reveal])
def get_all_reveals():
    """Get all reveals across all characters"""
    return reveal_store.get_all_reveals()


@router.post("", response_model=Reveal)
def create_reveal(reveal_data: RevealCreate):
    """Create a reveal for multiple characters"""
    # Verify all characters exist
    for character_id in reveal_data.character_ids:
        if not character_store.character_exists(character_id):
            raise HTTPException(
                status_code=404, detail=f"Character {character_id} not found"
            )

    return reveal_store.create_reveal(reveal_data)


@router.get("/{reveal_id}", response_model=Reveal)
def get_reveal(reveal_id: int):
    """Get a specific reveal by ID"""
    reveal = reveal_store.get_reveal(reveal_id)
    if not reveal:
        raise HTTPException(status_code=404, detail="Reveal not found")
    return reveal


@router.get("/character/{character_id}", response_model=List[Reveal])
def get_character_reveals(character_id: int):
    """Get all reveals for a character"""
    # Verify character exists
    if not character_store.character_exists(character_id):
        raise HTTPException(status_code=404, detail="Character not found")

    return reveal_store.get_by_character_id(character_id)


@router.put("/{reveal_id}", response_model=Reveal)
def update_reveal(reveal_id: int, updates: dict):
    """Update a reveal"""
    reveal = reveal_store.update_reveal(reveal_id, updates)
    if not reveal:
        raise HTTPException(status_code=404, detail="Reveal not found")
    return reveal


@router.delete("/{reveal_id}")
def delete_reveal(reveal_id: int):
    """Delete a reveal"""
    success = reveal_store.delete_reveal(reveal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reveal not found")
    return {"message": "Reveal deleted successfully"}
