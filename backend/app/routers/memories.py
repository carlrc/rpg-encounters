import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.data.character_store import CharacterStore
from app.data.memory_store import MemoryStore
from app.db.connection import get_db_session
from app.dependencies import get_current_user_world
from app.http import ENTITY_NOT_FOUND, INTERNAL_SERVER_ERROR
from app.models.memory import Memory, MemoryCreate, MemoryUpdate

router = APIRouter(prefix="/api/memories", tags=["memories"])

logger = logging.getLogger(__name__)


@router.get("", response_model=List[Memory])
def get_all_memories(user_world: tuple[int, int] = Depends(get_current_user_world)):
    """Get all memories across all characters"""
    user_id, world_id = user_world
    try:
        return MemoryStore(user_id=user_id, world_id=world_id).get_all_memories()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get memories for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.get("/{memory_id}", response_model=Memory)
def get_memory(
    memory_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Get a specific memory by ID"""
    user_id, world_id = user_world
    try:
        memory = MemoryStore(user_id=user_id, world_id=world_id).get_memory(memory_id)
        if not memory:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return memory
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get memory {memory_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.post("", response_model=Memory)
def create_memory(
    memory_data: MemoryCreate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Create a memory for multiple characters"""
    user_id, world_id = user_world
    try:
        with get_db_session() as session:
            # Verify all characters exist
            character_store = CharacterStore(
                user_id=user_id, world_id=world_id, session=session
            )
            for character_id in memory_data.character_ids:
                if not character_store.character_exists(character_id):
                    raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)

            return MemoryStore(
                user_id=user_id, world_id=world_id, session=session
            ).create_memory(memory_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to create memory for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.put("/{memory_id}", response_model=Memory)
def update_memory(
    memory_id: int,
    memory_update: MemoryUpdate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Update a memory"""
    user_id, world_id = user_world
    try:
        with get_db_session() as session:
            # Verify all characters exist if character_ids are being updated
            if memory_update.character_ids:
                character_store = CharacterStore(
                    user_id=user_id, world_id=world_id, session=session
                )
                for character_id in memory_update.character_ids:
                    if not character_store.character_exists(character_id):
                        raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)

            memory = MemoryStore(
                user_id=user_id, world_id=world_id, session=session
            ).update_memory(memory_id, memory_update)
            if not memory:
                raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
            return memory
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update memory {memory_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.delete("/{memory_id}")
def delete_memory(
    memory_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Delete a memory"""
    user_id, world_id = user_world
    try:
        success = MemoryStore(user_id=user_id, world_id=world_id).delete_memory(
            memory_id
        )
        if not success:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return {"message": "Memory deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete memory {memory_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)
