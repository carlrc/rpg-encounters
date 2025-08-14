from typing import List

from fastapi import APIRouter, HTTPException

from app.data.character_store import CharacterStore
from app.data.memory_store import MemoryStore
from app.models.memory import Memory, MemoryCreate, MemoryUpdate

router = APIRouter(prefix="/api/memories", tags=["memories"])


@router.get("", response_model=List[Memory])
def get_all_memories():
    """Get all memories across all characters"""
    return MemoryStore().get_all_memories()


@router.get("/{memory_id}", response_model=Memory)
def get_memory(memory_id: int):
    """Get a specific memory by ID"""
    memory = MemoryStore().get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.post("", response_model=Memory)
def create_memory(memory_data: MemoryCreate):
    """Create a memory for multiple characters"""
    # Verify all characters exist
    for character_id in memory_data.character_ids:
        if not CharacterStore().character_exists(character_id):
            raise HTTPException(
                status_code=404, detail=f"Character {character_id} not found"
            )

    return MemoryStore().create_memory(memory_data)


@router.put("/{memory_id}", response_model=Memory)
def update_memory(memory_id: int, memory_update: MemoryUpdate):
    """Update a memory"""
    # Verify all characters exist if character_ids are being updated
    if memory_update.character_ids:
        for character_id in memory_update.character_ids:
            if not CharacterStore().character_exists(character_id):
                raise HTTPException(
                    status_code=404, detail=f"Character {character_id} not found"
                )

    memory = MemoryStore().update_memory(memory_id, memory_update)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.delete("/{memory_id}")
def delete_memory(memory_id: int):
    """Delete a memory"""
    success = MemoryStore().delete_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"message": "Memory deleted successfully"}
