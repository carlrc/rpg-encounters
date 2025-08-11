from fastapi import APIRouter, HTTPException
from typing import List
from app.data.memory_store import memory_store
from app.data.character_store import character_store
from app.models.memory import Memory, MemoryCreate

router = APIRouter(prefix="/api/memories", tags=["memories"])


@router.get("", response_model=List[Memory])
def get_all_memories():
    """Get all memories across all characters"""
    return memory_store.get_all_memories()


@router.get("/{memory_id}", response_model=Memory)
def get_memory(memory_id: int):
    """Get a specific memory by ID"""
    memory = memory_store.get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.post("", response_model=Memory)
def create_memory(memory_data: MemoryCreate):
    """Create a memory for multiple characters"""
    # Verify all characters exist
    for character_id in memory_data.character_ids:
        if not character_store.character_exists(character_id):
            raise HTTPException(
                status_code=404, detail=f"Character {character_id} not found"
            )

    return memory_store.create_memory(memory_data)


@router.put("/{memory_id}", response_model=Memory)
def update_memory(memory_id: int, updates: dict):
    """Update a memory"""
    memory = memory_store.update_memory(memory_id, updates)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.delete("/{memory_id}")
def delete_memory(memory_id: int):
    """Delete a memory"""
    success = memory_store.delete_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"message": "Memory deleted successfully"}
