from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.memory import Memory, MemoryCreate, MemoryUpdate

router = APIRouter(prefix="/api/memories", tags=["memories"])

# In-memory storage for now (replace with database later)
memories_db = {
    1: Memory(
        id=1,
        title="Tavern Regular",
        linked_character_ids=[1],
        visibility_type="always",
        keywords=[],
        player_races=[],
        player_alignments=[],
        player_tags=[],
        memory_text="This character is a regular at the local tavern and knows all the gossip in town. They're friendly to adventurers who buy them a drink.",
        character_limit=500
    ),
    2: Memory(
        id=2,
        title="Distrusts Elves",
        linked_character_ids=[1],
        visibility_type="player_race",
        keywords=[],
        player_races=["Elf"],
        player_alignments=[],
        player_tags=[],
        memory_text="This character has had bad experiences with elves in the past and is initially suspicious of elf characters. They may be less helpful or charge higher prices.",
        character_limit=500
    ),
    3: Memory(
        id=3,
        title="Recognizes Noble Bearing",
        linked_character_ids=[2],
        visibility_type="tags",
        keywords=[],
        player_races=[],
        player_alignments=[],
        player_tags=["noble", "aristocrat", "wealthy"],
        memory_text="This character can spot nobility from a mile away and will treat noble-born characters with extra respect and deference.",
        character_limit=500
    ),
    4: Memory(
        id=4,
        title="Dragon Knowledge",
        linked_character_ids=[1, 2],
        visibility_type="keyword",
        keywords=["dragon", "wyrm", "ancient", "treasure"],
        player_races=[],
        player_alignments=[],
        player_tags=[],
        memory_text="When dragons are mentioned, this character becomes visibly nervous and will share warnings about an ancient red dragon that supposedly lairs in the nearby mountains.",
        character_limit=500
    )
}
next_memory_id = 5

@router.get("/", response_model=List[Memory])
async def get_memories():
    """Get all memories"""
    return list(memories_db.values())

@router.get("/{memory_id}", response_model=Memory)
async def get_memory(memory_id: int):
    """Get a specific memory by ID"""
    if memory_id not in memories_db:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memories_db[memory_id]

@router.post("/", response_model=Memory)
async def create_memory(memory: MemoryCreate):
    """Create a new memory"""
    global next_memory_id
    
    memory_dict = memory.model_dump()
    memory_dict["id"] = next_memory_id
    
    new_memory = Memory(**memory_dict)
    memories_db[next_memory_id] = new_memory
    next_memory_id += 1
    
    return new_memory

@router.put("/{memory_id}", response_model=Memory)
async def update_memory(memory_id: int, memory_update: MemoryUpdate):
    """Update an existing memory"""
    if memory_id not in memories_db:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    existing_memory = memories_db[memory_id]
    update_data = memory_update.model_dump(exclude_unset=True)
    
    # Update the existing memory with new data
    updated_data = existing_memory.model_dump()
    updated_data.update(update_data)
    
    updated_memory = Memory(**updated_data)
    memories_db[memory_id] = updated_memory
    
    return updated_memory

@router.delete("/{memory_id}")
async def delete_memory(memory_id: int):
    """Delete a memory"""
    if memory_id not in memories_db:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    del memories_db[memory_id]
    return {"message": "Memory deleted successfully"}
