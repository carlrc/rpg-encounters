from fastapi import APIRouter, HTTPException
from typing import List
from app.models.trust import TrustProfile, TrustProfileCreate, TrustNugget, TrustNuggetCreate
from app.data.trust_store import trust_profile_store, nugget_store
from app.data.character_store import character_store

router = APIRouter(prefix="/api/trust", tags=["trust"])

# Trust Profile endpoints
@router.post("/profiles", response_model=TrustProfile)
def create_trust_profile(profile_data: TrustProfileCreate):
    """Create a trust profile for a character"""
    # Verify character exists
    if not character_store.character_exists(profile_data.character_id):
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Check if profile already exists
    existing_profile = trust_profile_store.get_by_character_id(profile_data.character_id)
    if existing_profile:
        raise HTTPException(status_code=400, detail="Trust profile already exists for this character")
    
    return trust_profile_store.create_trust_profile(profile_data)

@router.get("/profiles/{character_id}", response_model=TrustProfile)
def get_trust_profile(character_id: int):
    """Get trust profile for a character"""
    profile = trust_profile_store.get_by_character_id(character_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Trust profile not found")
    return profile

@router.put("/profiles/{character_id}", response_model=TrustProfile)
def update_trust_profile(character_id: int, updates: dict):
    """Update trust profile for a character"""
    profile = trust_profile_store.update_trust_profile(character_id, updates)
    if not profile:
        raise HTTPException(status_code=404, detail="Trust profile not found")
    return profile

@router.delete("/profiles/{character_id}")
def delete_trust_profile(character_id: int):
    """Delete trust profile for a character"""
    success = trust_profile_store.delete_trust_profile(character_id)
    if not success:
        raise HTTPException(status_code=404, detail="Trust profile not found")
    return {"message": "Trust profile deleted successfully"}

# Nugget endpoints
@router.get("/nuggets", response_model=List[TrustNugget])
def get_all_nuggets():
    """Get all nuggets across all characters"""
    return nugget_store.get_all_nuggets()

@router.post("/nuggets", response_model=TrustNugget)
def create_nugget(nugget_data: TrustNuggetCreate):
    """Create a trust nugget for multiple characters"""
    # Verify all characters exist
    for character_id in nugget_data.character_ids:
        if not character_store.character_exists(character_id):
            raise HTTPException(status_code=404, detail=f"Character {character_id} not found")
    
    return nugget_store.create_nugget(nugget_data)

@router.get("/nuggets/{nugget_id}", response_model=TrustNugget)
def get_nugget(nugget_id: int):
    """Get a specific nugget by ID"""
    nugget = nugget_store.get_nugget(nugget_id)
    if not nugget:
        raise HTTPException(status_code=404, detail="Nugget not found")
    return nugget

@router.get("/nuggets/character/{character_id}", response_model=List[TrustNugget])
def get_character_nuggets(character_id: int):
    """Get all nuggets for a character"""
    # Verify character exists
    if not character_store.character_exists(character_id):
        raise HTTPException(status_code=404, detail="Character not found")
    
    return nugget_store.get_by_character_id(character_id)

@router.put("/nuggets/{nugget_id}", response_model=TrustNugget)
def update_nugget(nugget_id: int, updates: dict):
    """Update a nugget"""
    nugget = nugget_store.update_nugget(nugget_id, updates)
    if not nugget:
        raise HTTPException(status_code=404, detail="Nugget not found")
    return nugget

@router.delete("/nuggets/{nugget_id}")
def delete_nugget(nugget_id: int):
    """Delete a nugget"""
    success = nugget_store.delete_nugget(nugget_id)
    if not success:
        raise HTTPException(status_code=404, detail="Nugget not found")
    return {"message": "Nugget deleted successfully"}
