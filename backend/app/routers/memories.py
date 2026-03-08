import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.session import UserSession
from app.data.character_store import CharacterStore
from app.data.memory_store import MemoryStore
from app.db.connection import get_async_db_routes_session
from app.dependencies import validate_current_user_world
from app.http import ENTITY_NOT_FOUND, INTERNAL_SERVER_ERROR
from app.models.memory import Memory, MemoryCreate, MemoryUpdate

router = APIRouter(prefix="/api/memories", tags=["memories"])

logger = logging.getLogger(__name__)


@router.get("", response_model=List[Memory])
async def get_all_memories(
    session: UserSession = Depends(validate_current_user_world),
):
    """Get all memories across all characters"""
    user_id, world_id = session.user_id, session.world_id
    try:
        return await MemoryStore(user_id=user_id, world_id=world_id).get_all()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get memories for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )


@router.get("/{memory_id}", response_model=Memory)
async def get_memory(
    memory_id: int, session: UserSession = Depends(validate_current_user_world)
):
    """Get a specific memory by ID"""
    user_id, world_id = session.user_id, session.world_id
    try:
        memory = await MemoryStore(user_id=user_id, world_id=world_id).get_by_id(
            memory_id
        )
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=ENTITY_NOT_FOUND
            )
        return memory
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get memory {memory_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )


@router.post("", response_model=Memory)
async def create_memory(
    memory_data: MemoryCreate,
    session: UserSession = Depends(validate_current_user_world),
    db_session: AsyncSession = Depends(get_async_db_routes_session),
):
    """Create a memory for multiple characters"""
    user_id, world_id = session.user_id, session.world_id
    try:
        # Verify all characters exist
        character_store = CharacterStore(
            user_id=user_id, world_id=world_id, session=db_session
        )
        for character_id in memory_data.character_ids:
            if not await character_store.exists(character_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=ENTITY_NOT_FOUND
                )

        return await MemoryStore(
            user_id=user_id, world_id=world_id, session=db_session
        ).create(memory_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to create memory for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )


@router.put("/{memory_id}", response_model=Memory)
async def update_memory(
    memory_id: int,
    memory_update: MemoryUpdate,
    session: UserSession = Depends(validate_current_user_world),
    db_session: AsyncSession = Depends(get_async_db_routes_session),
):
    """Update a memory"""
    user_id, world_id = session.user_id, session.world_id
    try:
        # Verify all characters exist if character_ids are being updated
        if memory_update.character_ids:
            character_store = CharacterStore(
                user_id=user_id, world_id=world_id, session=db_session
            )
            for character_id in memory_update.character_ids:
                if not await character_store.exists(character_id):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail=ENTITY_NOT_FOUND
                    )

        memory = await MemoryStore(
            user_id=user_id, world_id=world_id, session=db_session
        ).update(memory_id, memory_update)
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=ENTITY_NOT_FOUND
            )
        return memory
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update memory {memory_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: int, session: UserSession = Depends(validate_current_user_world)
):
    """Delete a memory"""
    user_id, world_id = session.user_id, session.world_id
    try:
        success = await MemoryStore(user_id=user_id, world_id=world_id).delete(
            memory_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=ENTITY_NOT_FOUND
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete memory {memory_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )
