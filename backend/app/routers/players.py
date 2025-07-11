from fastapi import APIRouter, HTTPException
from typing import List
from app.models.player import Player, PlayerCreate, PlayerUpdate

router = APIRouter(prefix="/api/players", tags=["players"])

# In-memory storage for players (will be replaced with database later)
players_db = [
    {"id": 1, "name": "Aragorn", "description": "A skilled ranger and future king of Gondor"},
    {"id": 2, "name": "Legolas", "description": "An elven archer with keen eyes and swift arrows"},
    {"id": 3, "name": "Gimli", "description": "A dwarven warrior with an axe and a heart of gold"},
    {"id": 4, "name": "Gandalf", "description": "A wise wizard who guides the fellowship"}
]
next_id = 5

@router.get("/", response_model=List[Player])
async def get_players():
    """Get all players"""
    return players_db

@router.get("/{player_id}", response_model=Player)
async def get_player(player_id: int):
    """Get a specific player by ID"""
    player = next((p for p in players_db if p["id"] == player_id), None)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@router.post("/", response_model=Player, status_code=201)
async def create_player(player: PlayerCreate):
    """Create a new player"""
    global next_id
    new_player = {
        "id": next_id,
        "name": player.name,
        "description": player.description
    }
    players_db.append(new_player)
    next_id += 1
    return new_player

@router.put("/{player_id}", response_model=Player)
async def update_player(player_id: int, player_update: PlayerUpdate):
    """Update an existing player"""
    player = next((p for p in players_db if p["id"] == player_id), None)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Update only provided fields
    if player_update.name is not None:
        player["name"] = player_update.name
    if player_update.description is not None:
        player["description"] = player_update.description
    
    return player

@router.delete("/{player_id}", status_code=204)
async def delete_player(player_id: int):
    """Delete a player"""
    global players_db
    player = next((p for p in players_db if p["id"] == player_id), None)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    players_db = [p for p in players_db if p["id"] != player_id]
    return None
