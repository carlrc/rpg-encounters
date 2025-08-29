from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.data.character_store import CharacterStore
from app.data.memory_store import MemoryStore
from app.db.connection import get_db_session
from app.dependencies import get_current_user_world
from app.models.memory import Memory, MemoryCreate, MemoryUpdate

router = APIRouter(prefix="/api/memories", tags=["memories"])


@router.get("", response_model=List[Memory])
def get_all_memories(user_world: tuple[int, int] = Depends(get_current_user_world)):
    """Get all memories across all characters"""
    user_id, world_id = user_world
    return MemoryStore(user_id=user_id, world_id=world_id).get_all_memories()


@router.get("/{memory_id}", response_model=Memory)
def get_memory(
    memory_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Get a specific memory by ID"""
    user_id, world_id = user_world
    memory = MemoryStore(user_id=user_id, world_id=world_id).get_memory(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.post("", response_model=Memory)
def create_memory(
    memory_data: MemoryCreate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Create a memory for multiple characters"""
    user_id, world_id = user_world

    with get_db_session() as session:
        # Verify all characters exist
        character_store = CharacterStore(
            user_id=user_id, world_id=world_id, session=session
        )
        for character_id in memory_data.character_ids:
            if not character_store.character_exists(character_id):
                raise HTTPException(
                    status_code=404, detail=f"Character {character_id} not found"
                )

        return MemoryStore(
            user_id=user_id, world_id=world_id, session=session
        ).create_memory(memory_data)


@router.put("/{memory_id}", response_model=Memory)
def update_memory(
    memory_id: int,
    memory_update: MemoryUpdate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Update a memory"""
    user_id, world_id = user_world

    with get_db_session() as session:
        # Verify all characters exist if character_ids are being updated
        if memory_update.character_ids:
            character_store = CharacterStore(
                user_id=user_id, world_id=world_id, session=session
            )
            for character_id in memory_update.character_ids:
                if not character_store.character_exists(character_id):
                    raise HTTPException(
                        status_code=404, detail=f"Character {character_id} not found"
                    )

        memory = MemoryStore(
            user_id=user_id, world_id=world_id, session=session
        ).update_memory(memory_id, memory_update)
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        return memory


@router.delete("/{memory_id}")
def delete_memory(
    memory_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Delete a memory"""
    user_id, world_id = user_world
    success = MemoryStore(user_id=user_id, world_id=world_id).delete_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"message": "Memory deleted successfully"}
