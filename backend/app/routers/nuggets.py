from fastapi import APIRouter, HTTPException
from typing import List
from app.models.nugget import Truth, TruthCreate
from app.data.nugget_store import truth_store
from app.data.character_store import character_store

router = APIRouter(prefix="/api/truths", tags=["truths"])


@router.get("", response_model=List[Truth])
def get_all_truths():
    """Get all truths across all characters"""
    return truth_store.get_all_truths()


@router.post("", response_model=Truth)
def create_truth(truth_data: TruthCreate):
    """Create a truth for multiple characters"""
    # Verify all characters exist
    for character_id in truth_data.character_ids:
        if not character_store.character_exists(character_id):
            raise HTTPException(
                status_code=404, detail=f"Character {character_id} not found"
            )

    return truth_store.create_truth(truth_data)


@router.get("/{truth_id}", response_model=Truth)
def get_truth(truth_id: int):
    """Get a specific truth by ID"""
    truth = truth_store.get_truth(truth_id)
    if not truth:
        raise HTTPException(status_code=404, detail="Truth not found")
    return truth


@router.get("/character/{character_id}", response_model=List[Truth])
def get_character_truths(character_id: int):
    """Get all truths for a character"""
    # Verify character exists
    if not character_store.character_exists(character_id):
        raise HTTPException(status_code=404, detail="Character not found")

    return truth_store.get_by_character_id(character_id)


@router.put("/{truth_id}", response_model=Truth)
def update_truth(truth_id: int, updates: dict):
    """Update a truth"""
    truth = truth_store.update_truth(truth_id, updates)
    if not truth:
        raise HTTPException(status_code=404, detail="Truth not found")
    return truth


@router.delete("/{truth_id}")
def delete_truth(truth_id: int):
    """Delete a truth"""
    success = truth_store.delete_truth(truth_id)
    if not success:
        raise HTTPException(status_code=404, detail="Truth not found")
    return {"message": "Truth deleted successfully"}
