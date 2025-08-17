from typing import List

from fastapi import APIRouter, HTTPException

from app.data.player_store import PlayerStore
from app.models.player import Player, PlayerCreate, PlayerUpdate

router = APIRouter(prefix="/api/players", tags=["players"])


@router.get("", response_model=List[Player])
async def get_players():
    """Get all players"""
    return PlayerStore().get_all_players()


@router.get("/{player_id}", response_model=Player)
async def get_player(player_id: int):
    """Get a specific player by ID"""
    player = PlayerStore().get_player_by_id(player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.post("/", response_model=Player, status_code=201)
async def create_player(player: PlayerCreate):
    """Create a new player"""
    return PlayerStore().create_player(player)


@router.put("/{player_id}", response_model=Player)
async def update_player(player_id: int, player_update: PlayerUpdate):
    """Update an existing player"""
    updated_player = PlayerStore().update_player(player_id, player_update)
    if updated_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return updated_player


@router.delete("/{player_id}", status_code=204)
async def delete_player(player_id: int):
    """Delete a player"""
    if not PlayerStore().delete_player(player_id):
        raise HTTPException(status_code=404, detail="Player not found")
    return None
