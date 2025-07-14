from typing import Optional, List
from ..models.memory import Memory, MemoryCreate, MemoryUpdate

memories_db = {
    1: Memory(
        id=1,
        title="Tavern Regular",
        linked_character_ids=[1],
        visibility_type="always",
        keywords=[],
        player_races=[],
        player_alignments=[],
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
        memory_text="This character has had bad experiences with elves in the past and is initially suspicious of elf characters. They may be less helpful or charge higher prices.",
        character_limit=500
    ),
    3: Memory(
        id=3,
        title="Recognizes Noble Bearing",
        linked_character_ids=[2],
        visibility_type="always",
        keywords=[],
        player_races=[],
        player_alignments=[],
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
        memory_text="When dragons are mentioned, this character becomes visibly nervous and will share warnings about an ancient red dragon that supposedly lairs in the nearby mountains.",
        character_limit=500
    ),
    5: Memory(
        id=5,
        title="Wary of Evil Intent",
        linked_character_ids=[2],
        visibility_type="player_alignment",
        keywords=[],
        player_races=[],
        player_alignments=["Lawful Evil", "Neutral Evil", "Chaotic Evil"],
        memory_text="This character has a keen sense for malevolent intentions and becomes noticeably uncomfortable around evil-aligned individuals. They may refuse service or demand payment upfront.",
        character_limit=500
    )
}
next_memory_id = 6

class MemoryStore:
    def __init__(self):
        self.memories = memories_db
        self.next_id = next_memory_id

    def get_all_memories(self) -> List[Memory]:
        """Get all memories"""
        return list(self.memories.values())

    def get_memory_by_id(self, memory_id: int) -> Optional[Memory]:
        """Get a specific memory by ID"""
        return self.memories.get(memory_id)

    def create_memory(self, memory_data: MemoryCreate) -> Memory:
        """Create a new memory"""
        memory_dict = memory_data.model_dump()
        memory_dict["id"] = self.next_id
        
        new_memory = Memory(**memory_dict)
        self.memories[self.next_id] = new_memory
        self.next_id += 1
        
        return new_memory

    def update_memory(self, memory_id: int, memory_update: MemoryUpdate) -> Optional[Memory]:
        """Update an existing memory"""
        if memory_id not in self.memories:
            return None
        
        existing_memory = self.memories[memory_id]
        update_data = memory_update.model_dump(exclude_unset=True)
        
        # Update the existing memory with new data
        updated_data = existing_memory.model_dump()
        updated_data.update(update_data)
        
        updated_memory = Memory(**updated_data)
        self.memories[memory_id] = updated_memory
        
        return updated_memory

    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory"""
        if memory_id not in self.memories:
            return False
        
        del self.memories[memory_id]
        return True

    def memory_exists(self, memory_id: int) -> bool:
        """Check if a memory exists"""
        return memory_id in self.memories


# Create a singleton instance
memory_store = MemoryStore()
