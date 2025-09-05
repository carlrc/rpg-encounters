import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.data.world_store import WorldStore
from app.dependencies import get_current_user_world
from app.http import ENTITY_NOT_FOUND, INTERNAL_SERVER_ERROR
from app.models.world import World

router = APIRouter(prefix="/api/worlds", tags=["worlds"])

logger = logging.getLogger(__name__)


@router.get("", response_model=List[World])
async def get_worlds(user_world: tuple[int, int] = Depends(get_current_user_world)):
    """Get all worlds for the current user"""
    user_id, _ = user_world
    try:
        return await WorldStore(user_id=user_id).get_all()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get worlds for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.get("/{world_id}", response_model=World)
async def get_world(
    world_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Get a specific world by ID"""
    user_id, _ = user_world
    try:
        world = await WorldStore(user_id=user_id).get_by_id(world_id)
        if not world:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return world
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get world {world_id} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.post("", response_model=World, status_code=201)
async def create_world(user_world: tuple[int, int] = Depends(get_current_user_world)):
    """Create a new world for the current user"""
    user_id, _ = user_world
    try:
        return await WorldStore(user_id=user_id).create()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create world for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.delete("/{world_id}", status_code=204)
async def delete_world(
    world_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Delete a world"""
    user_id, _ = user_world
    try:
        success = await WorldStore(user_id=user_id).delete(world_id)
        if not success:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete world {world_id} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)
