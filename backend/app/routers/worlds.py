from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.data.world_store import WorldStore
from app.dependencies import get_current_user_world
from app.models.world import World

router = APIRouter(prefix="/api/worlds", tags=["worlds"])


@router.get("", response_model=List[World])
async def get_worlds(user_world: tuple[int, int] = Depends(get_current_user_world)):
    """Get all worlds for the current user"""
    user_id, _ = user_world
    return WorldStore(user_id=user_id).get_all_worlds()


@router.get("/{world_id}", response_model=World)
async def get_world(
    world_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Get a specific world by ID"""
    user_id, _ = user_world
    world = WorldStore(user_id=user_id).get_world_by_id(world_id)
    if not world:
        raise HTTPException(status_code=404, detail="Not found")
    return world


@router.post("", response_model=World, status_code=201)
async def create_world(user_world: tuple[int, int] = Depends(get_current_user_world)):
    """Create a new world for the current user"""
    user_id, _ = user_world
    return WorldStore(user_id=user_id).create_world()


@router.delete("/{world_id}", status_code=204)
async def delete_world(
    world_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Delete a world"""
    user_id, _ = user_world
    success = WorldStore(user_id=user_id).delete_world(world_id)
    if not success:
        raise HTTPException(status_code=404, detail="Not found")
    return None
