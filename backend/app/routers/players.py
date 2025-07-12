from fastapi import APIRouter, HTTPException
from typing import List
from app.models.player import Player, PlayerCreate, PlayerUpdate

router = APIRouter(prefix="/api/players", tags=["players"])

# In-memory storage for players (will be replaced with database later)
players_db = [
    {
        "id": 1, 
        "name": "Aragorn", 
        "appearance": "Tall ranger with weathered features, keen grey eyes, and dark hair",
        "race": "Human",
        "class_name": "Ranger",
        "groups": ["#fellowship", "#rangers-of-the-north"]
    },
    {
        "id": 2, 
        "name": "Legolas", 
        "appearance": "Graceful elf with golden hair, bright blue eyes, and elegant features",
        "race": "Elf",
        "class_name": "Ranger",
        "groups": ["#fellowship", "#woodland-realm"]
    },
    {
        "id": 3, 
        "name": "Gimli", 
        "appearance": "Stout dwarf with braided red beard, chainmail armor, and fierce eyes",
        "race": "Dwarf",
        "class_name": "Fighter",
        "groups": ["#fellowship", "#erebor"]
    },
    {
        "id": 4, 
        "name": "Gandalf", 
        "appearance": "Tall wizard in grey robes with long white beard and piercing eyes",
        "race": "Human",
        "class_name": "Wizard",
        "groups": ["#fellowship", "#istari"]
    }
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
        "appearance": player.appearance,
        "race": player.race,
        "class_name": player.class_name,
        "groups": player.groups
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
    if player_update.appearance is not None:
        player["appearance"] = player_update.appearance
    if player_update.race is not None:
        player["race"] = player_update.race
    if player_update.class_name is not None:
        player["class_name"] = player_update.class_name
    if player_update.groups is not None:
        player["groups"] = player_update.groups
    
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
