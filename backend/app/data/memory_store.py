from typing import List
from app.models.memory import Memory, MemoryCreate
from tests.fixtures.memories import memories_db, next_memory_id


class MemoryStore:
    def __init__(self):
        self.memories = memories_db
        self.next_id = next_memory_id

    def get_all_memories(self) -> List[Memory]:
        """Get all memories across all characters"""
        return list(self.memories.values())

    def get_by_character_id(self, character_id: int) -> List[Memory]:
        """Get all memories for a character"""
        return [
            memory
            for memory in self.memories.values()
            if character_id in memory.character_ids
        ]

    def get_memory(self, memory_id: int) -> Memory | None:
        """Get a specific memory by ID"""
        return self.memories.get(memory_id)

    def get_by_id(self, memory_id: int) -> Memory | None:
        """Get a specific memory by ID (alias for get_memory)"""
        return self.memories.get(memory_id)

    def create_memory(self, memory_data: MemoryCreate) -> Memory:
        """Create a new memory"""
        memory_dict = memory_data.model_dump()
        memory_dict["id"] = self.next_id

        memory = Memory(**memory_dict)
        self.memories[self.next_id] = memory
        self.next_id += 1

        return memory

    def update_memory(self, memory_id: int, updates: dict) -> Memory | None:
        """Update an existing memory"""
        if memory_id not in self.memories:
            return None

        existing_memory = self.memories[memory_id]
        update_data = existing_memory.model_dump()
        update_data.update(updates)

        updated_memory = Memory(**update_data)
        self.memories[memory_id] = updated_memory
        return updated_memory

    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory"""
        if memory_id not in self.memories:
            return False
        del self.memories[memory_id]
        return True


# Create singleton instance
memory_store = MemoryStore()
