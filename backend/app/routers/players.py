import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.data.player_store import PlayerStore
from app.dependencies import get_current_user_world
from app.http import ENTITY_NOT_FOUND, INTERNAL_SERVER_ERROR
from app.models.player import Player, PlayerCreate, PlayerUpdate

router = APIRouter(prefix="/api/players", tags=["players"])

logger = logging.getLogger(__name__)


@router.get("", response_model=List[Player])
async def get_players(user_world: tuple[int, int] = Depends(get_current_user_world)):
    """Get all players"""
    user_id, world_id = user_world
    try:
        return await PlayerStore(user_id=user_id, world_id=world_id).get_all_players()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get players for user {user_id}, world {world_id}: {e}")
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.get("/{player_id}", response_model=Player)
async def get_player(
    player_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Get a specific player by ID"""
    user_id, world_id = user_world
    try:
        player = await PlayerStore(user_id=user_id, world_id=world_id).get_player_by_id(
            player_id
        )
        if player is None:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return player
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get player {player_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.post("/", response_model=Player, status_code=201)
async def create_player(
    player: PlayerCreate, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Create a new player"""
    user_id, world_id = user_world
    try:
        return await PlayerStore(user_id=user_id, world_id=world_id).create_player(
            player
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to create player for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.put("/{player_id}", response_model=Player)
async def update_player(
    player_id: int,
    player_update: PlayerUpdate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Update an existing player"""
    user_id, world_id = user_world
    try:
        updated_player = await PlayerStore(
            user_id=user_id, world_id=world_id
        ).update_player(player_id, player_update)
        if updated_player is None:
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return updated_player
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to update player {player_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.delete("/{player_id}", status_code=204)
async def delete_player(
    player_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Delete a player"""
    user_id, world_id = user_world
    try:
        if not await PlayerStore(user_id=user_id, world_id=world_id).delete_player(
            player_id
        ):
            raise HTTPException(status_code=404, detail=ENTITY_NOT_FOUND)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete player {player_id} for user {user_id}, world {world_id}: {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)
