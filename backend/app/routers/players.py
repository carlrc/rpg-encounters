from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.data.player_store import PlayerStore
from app.dependencies import get_current_user_world
from app.models.player import Player, PlayerCreate, PlayerUpdate

router = APIRouter(prefix="/api/players", tags=["players"])


@router.get("", response_model=List[Player])
async def get_players(user_world: tuple[int, int] = Depends(get_current_user_world)):
    """Get all players"""
    user_id, world_id = user_world
    return PlayerStore(user_id=user_id, world_id=world_id).get_all_players()


@router.get("/{player_id}", response_model=Player)
async def get_player(
    player_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Get a specific player by ID"""
    user_id, world_id = user_world
    player = PlayerStore(user_id=user_id, world_id=world_id).get_player_by_id(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.post("/", response_model=Player, status_code=201)
async def create_player(
    player: PlayerCreate, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Create a new player"""
    user_id, world_id = user_world
    return PlayerStore(user_id=user_id, world_id=world_id).create_player(player)


@router.put("/{player_id}", response_model=Player)
async def update_player(
    player_id: int,
    player_update: PlayerUpdate,
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Update an existing player"""
    user_id, world_id = user_world
    updated_player = PlayerStore(user_id=user_id, world_id=world_id).update_player(
        player_id, player_update
    )
    if updated_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return updated_player


@router.delete("/{player_id}", status_code=204)
async def delete_player(
    player_id: int, user_world: tuple[int, int] = Depends(get_current_user_world)
):
    """Delete a player"""
    user_id, world_id = user_world
    if not PlayerStore(user_id=user_id, world_id=world_id).delete_player(player_id):
        raise HTTPException(status_code=404, detail="Player not found")
    return None
