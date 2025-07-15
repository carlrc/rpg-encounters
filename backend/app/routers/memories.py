from fastapi import APIRouter, HTTPException
from typing import List
from app.models.memory import Memory, MemoryCreate, MemoryUpdate
from app.data.memory_store import memory_store

router = APIRouter(prefix="/api/memories", tags=["memories"])

@router.get("/", response_model=List[Memory])
async def get_memories():
    """Get all memories"""
    return memory_store.get_all_memories()

@router.get("/{memory_id}", response_model=Memory)
async def get_memory(memory_id: int):
    """Get a specific memory by ID"""
    memory = memory_store.get_memory_by_id(memory_id)
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

@router.post("/", response_model=Memory)
async def create_memory(memory: MemoryCreate):
    """Create a new memory"""
    return memory_store.create_memory(memory)

@router.put("/{memory_id}", response_model=Memory)
async def update_memory(memory_id: int, memory_update: MemoryUpdate):
    """Update an existing memory"""
    updated_memory = memory_store.update_memory(memory_id, memory_update)
    if updated_memory is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return updated_memory

@router.delete("/{memory_id}")
async def delete_memory(memory_id: int):
    """Delete a memory"""
    if not memory_store.delete_memory(memory_id):
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"message": "Memory deleted successfully"}
