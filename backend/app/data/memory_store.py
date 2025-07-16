from typing import Optional, List
from app.models.memory import Memory, MemoryCreate, MemoryUpdate
from tests.fixtures.memories import memories_db, next_memory_id

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
