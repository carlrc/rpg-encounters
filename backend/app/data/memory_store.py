from typing import Optional, List
from app.models.memory import Memory, MemoryCreate, MemoryUpdate

memories_db = {
    1: Memory(
        id=1,
        title="The Garden Vandal Mystery",
        linked_character_ids=[1, 2, 3, 4],
        visibility_type="always",
        keywords=[],
        player_races=[],
        player_alignments=[],
        memory_text="Someone has been destroying the village gardens at night! Vegetables trampled, flowers uprooted, and prize-winning plants ruined. Nobody knows who's doing it, but the whole village is talking about it.",
        character_limit=500
    ),
    2: Memory(
        id=2,
        title="Suspicious Footprints",
        linked_character_ids=[4],
        visibility_type="keyword",
        keywords=["footprints", "tracks", "evidence", "clues", "investigation"],
        player_races=[],
        player_alignments=[],
        memory_text="Small hobbit-sized footprints were found near the destroyed gardens. Some say they look familiar, but nobody wants to accuse their neighbors without proof.",
        character_limit=500
    ),
    3: Memory(
        id=3,
        title="The Tavern Gossip",
        linked_character_ids=[1],
        visibility_type="keyword",
        keywords=["gossip", "rumors", "tavern", "whispers", "speculation"],
        player_races=[],
        player_alignments=[],
        memory_text="The tavern is buzzing with theories about the garden destroyer. Some suspect jealousy over the annual garden competition, others think it's just mischief. Everyone has an opinion but no real answers.",
        character_limit=500
    ),
    4: Memory(
        id=4,
        title="The Competition Connection",
        linked_character_ids=[2, 4],
        visibility_type="keyword",
        keywords=["competition", "contest", "jealousy", "rivalry", "prize"],
        player_races=[],
        player_alignments=[],
        memory_text="The garden destruction seems to target the best gardens - those that usually win the annual village competition. Could someone be eliminating the competition through sabotage?",
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
