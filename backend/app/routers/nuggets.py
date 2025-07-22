from fastapi import APIRouter, HTTPException
from typing import List
from app.models.nugget import TrustNugget, TrustNuggetCreate
from app.data.nugget_store import nugget_store
from app.data.character_store import character_store

router = APIRouter(prefix="/api/nuggets", tags=["nuggets"])


@router.get("", response_model=List[TrustNugget])
def get_all_nuggets():
    """Get all nuggets across all characters"""
    return nugget_store.get_all_nuggets()


@router.post("", response_model=TrustNugget)
def create_nugget(nugget_data: TrustNuggetCreate):
    """Create a trust nugget for multiple characters"""
    # Verify all characters exist
    for character_id in nugget_data.character_ids:
        if not character_store.character_exists(character_id):
            raise HTTPException(
                status_code=404, detail=f"Character {character_id} not found"
            )

    return nugget_store.create_nugget(nugget_data)


@router.get("/{nugget_id}", response_model=TrustNugget)
def get_nugget(nugget_id: int):
    """Get a specific nugget by ID"""
    nugget = nugget_store.get_nugget(nugget_id)
    if not nugget:
        raise HTTPException(status_code=404, detail="Nugget not found")
    return nugget


@router.get("/character/{character_id}", response_model=List[TrustNugget])
def get_character_nuggets(character_id: int):
    """Get all nuggets for a character"""
    # Verify character exists
    if not character_store.character_exists(character_id):
        raise HTTPException(status_code=404, detail="Character not found")

    return nugget_store.get_by_character_id(character_id)


@router.put("/{nugget_id}", response_model=TrustNugget)
def update_nugget(nugget_id: int, updates: dict):
    """Update a nugget"""
    nugget = nugget_store.update_nugget(nugget_id, updates)
    if not nugget:
        raise HTTPException(status_code=404, detail="Nugget not found")
    return nugget


@router.delete("/{nugget_id}")
def delete_nugget(nugget_id: int):
    """Delete a nugget"""
    success = nugget_store.delete_nugget(nugget_id)
    if not success:
        raise HTTPException(status_code=404, detail="Nugget not found")
    return {"message": "Nugget deleted successfully"}
