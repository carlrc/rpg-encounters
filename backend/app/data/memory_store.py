from typing import Optional, List
from app.models.memory import Memory, MemoryCreate, MemoryUpdate

memories_db = {
    1: Memory(
        id=1,
        title="The One Ring's Corruption",
        linked_character_ids=[1, 3],
        visibility_type="keyword",
        keywords=["ring", "precious", "burden"],
        player_races=[],
        player_alignments=[],
        memory_text="They speak of its terrible power to corrupt even the purest hearts and the need for great caution.",
        character_limit=500
    ),
    2: Memory(
        id=3,
        title="Gondor's Glory",
        linked_character_ids=[2],
        visibility_type="keyword",
        keywords=["gondor", "minas tirith", "white city", "steward"],
        player_races=[],
        player_alignments=[],
        memory_text="This character's eyes light up when Gondor is mentioned. They speak proudly of the White City's strength and the valor of its defenders against the darkness.",
        character_limit=500
    ),
    3: Memory(
        id=4,
        title="Sauron's Growing Shadow",
        linked_character_ids=[1, 2, 3, 4],
        visibility_type="keyword",
        keywords=["sauron", "mordor", "darkness", "enemy", "shadow"],
        player_races=[],
        player_alignments=[],
        memory_text="When the Dark Lord is mentioned, this character becomes solemn and speaks of the growing threat from Mordor and the need for all free peoples to unite.",
        character_limit=500
    ),
    4: Memory(
        id=5,
        title="Rohan's Horse-lords",
        linked_character_ids=[4],
        visibility_type="keyword",
        keywords=["rohan", "horse", "edoras", "rohirrim", "riders"],
        player_races=[],
        player_alignments=[],
        memory_text="This character speaks with pride of the Rohirrim and their swift horses, recounting tales of great cavalry charges and the bond between rider and steed.",
        character_limit=500
    )
}
next_memory_id = 5

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
