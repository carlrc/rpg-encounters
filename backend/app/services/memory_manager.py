from backend.app.models.memory import Memory
from backend.app.models.player import Player
from ..data.memory_store import memory_store
from ..data.player_store import player_store

class MemoryManager:
    def __init__(self):
        self.active_memories = []

    def get_memories(self, characterId: int, playerId: int) -> list[str]:
        # Get the player data
        player = player_store.get_player_by_id(playerId)

        all_memories = memory_store.get_all_memories()
        linked_memories = list(filter(lambda memory: characterId in memory.linked_character_ids, all_memories))
        active_memory_ids = {memory.id for memory in self.active_memories}
        inactive_memories = list(filter(lambda memory: memory.id not in active_memory_ids, linked_memories))
        relevant_memories = self._get_relevant_memories(inactive_memories, player)

        return [memory.memory_text for memory in relevant_memories]

    def _get_relevant_memories(self, memories: list[Memory], player: Player) -> list[Memory]:
        relevant_memories: list[Memory] = []
        for memory in memories:
            if memory.visibility_type == "always":
                relevant_memories.append(memory)
            if memory.visibility_type == "player_race":
                if player.race in memory.player_races:
                    relevant_memories.append(memory)
            if memory.visibility_type == "player_alignment":
                if player.alignment in memory.player_alignments:
                    relevant_memories.append(memory)
            if memory.visibility_type == "keyword":
                if self._has_keywords("", memory):
                    relevant_memories.append(memory)
        
        return relevant_memories
    
    def _has_keywords(self, transcript: str, memory: Memory) -> bool:
        """
        Check if any keywords from the memory are present in the transcript
        using a two-pointer approach that searches from both ends.
        """
        if not memory.keywords or not transcript:
            return False
        
        # Split transcript into words and convert to lowercase for case-insensitive matching
        words = transcript.lower().split()
        if not words:
            return False
        
        # Convert keywords to lowercase and remove dashes for comparison
        keywords_lower = [keyword.lower().replace('-', '') for keyword in memory.keywords]
        
        # Two-pointer approach: start from both ends
        left = 0
        right = len(words) - 1
        
        while left <= right:
            # Check word at left pointer
            if words[left] in keywords_lower:
                return True
            
            # Check word at right pointer (avoid checking same word twice when left == right)
            if left != right and words[right] in keywords_lower:
                return True
            
            # Move pointers inward
            left += 1
            right -= 1
        
        return False
