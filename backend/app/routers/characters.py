from fastapi import APIRouter, HTTPException
from typing import List
from app.models.character import Character, CharacterCreate, CharacterUpdate, CharacterRace, CharacterSize, CharacterAlignment

router = APIRouter(prefix="/api/characters", tags=["characters"])

# In-memory storage for characters (will be replaced with database later)
characters_db = [
    {
        "id": 1,
        "name": "Elara Moonwhisper",
        "avatar": None,
        "race": CharacterRace.ELF.value,
        "size": CharacterSize.MEDIUM.value,
        "alignment": CharacterAlignment.NEUTRAL_GOOD.value,
        "profession": "Merchant",
        "background": "A traveling merchant who has seen many lands and peoples. She values knowledge and fair trade above all else. Her family runs a network of trading posts across the realm.",
        "communication_style": "Speaks softly with measured words, often pausing to consider responses carefully.",
        "tags": ["#merchant", "#traveler", "#knowledge-seeker"]
    },
    {
        "id": 2,
        "name": "Thorin Ironforge",
        "avatar": None,
        "race": CharacterRace.DWARF.value,
        "size": CharacterSize.MEDIUM.value,
        "alignment": CharacterAlignment.LAWFUL_GOOD.value,
        "profession": "Guard",
        "background": "A veteran city guard who has protected the gates for over twenty years. Known for his unwavering sense of duty and his ability to spot trouble from a mile away.",
        "communication_style": "Direct and gruff, but fair. Uses few words but makes them count.",
        "tags": ["#guard", "#veteran", "#duty-bound"]
    },
    {
        "id": 3,
        "name": "Zara the Wise",
        "avatar": None,
        "race": CharacterRace.HUMAN.value,
        "size": CharacterSize.MEDIUM.value,
        "alignment": CharacterAlignment.TRUE_NEUTRAL.value,
        "profession": "Mage",
        "background": "An accomplished wizard who runs the local magic academy. She has dedicated her life to the study of arcane arts and teaching the next generation of spellcasters.",
        "communication_style": "Scholarly and precise, often references ancient texts and magical theory.",
        "tags": ["#mage", "#teacher", "#scholar"]
    },
    {
        "id": 4,
        "name": "Lord Aldric Blackwood",
        "avatar": None,
        "race": CharacterRace.HUMAN.value,
        "size": CharacterSize.MEDIUM.value,
        "alignment": CharacterAlignment.LAWFUL_NEUTRAL.value,
        "profession": "Noble",
        "background": "A minor lord who oversees a small but prosperous region. He is known for his political acumen and his ability to navigate court intrigue with skill.",
        "communication_style": "Formal and diplomatic, chooses words carefully to avoid offense.",
        "tags": ["#noble", "#politician", "#courtly"]
    }
]
next_id = 5

@router.get("/", response_model=List[Character])
async def get_characters():
    """Get all characters"""
    return characters_db

@router.get("/{character_id}", response_model=Character)
async def get_character(character_id: int):
    """Get a specific character by ID"""
    character = next((c for c in characters_db if c["id"] == character_id), None)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

@router.post("/", response_model=Character, status_code=201)
async def create_character(character: CharacterCreate):
    """Create a new character"""
    global next_id
    new_character = {
        "id": next_id,
        "name": character.name,
        "avatar": character.avatar,
        "race": character.race,
        "size": character.size,
        "alignment": character.alignment,
        "profession": character.profession,
        "background": character.background,
        "communication_style": character.communication_style,
        "tags": character.tags
    }
    characters_db.append(new_character)
    next_id += 1
    return new_character

@router.put("/{character_id}", response_model=Character)
async def update_character(character_id: int, character_update: CharacterUpdate):
    """Update an existing character"""
    character = next((c for c in characters_db if c["id"] == character_id), None)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Update only provided fields
    if character_update.name is not None:
        character["name"] = character_update.name
    if character_update.avatar is not None:
        character["avatar"] = character_update.avatar
    if character_update.race is not None:
        character["race"] = character_update.race
    if character_update.size is not None:
        character["size"] = character_update.size
    if character_update.alignment is not None:
        character["alignment"] = character_update.alignment
    if character_update.profession is not None:
        character["profession"] = character_update.profession
    if character_update.background is not None:
        character["background"] = character_update.background
    if character_update.communication_style is not None:
        character["communication_style"] = character_update.communication_style
    if character_update.tags is not None:
        character["tags"] = character_update.tags
    
    return character

@router.delete("/{character_id}", status_code=204)
async def delete_character(character_id: int):
    """Delete a character"""
    global characters_db
    character = next((c for c in characters_db if c["id"] == character_id), None)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    characters_db = [c for c in characters_db if c["id"] != character_id]
    return None
