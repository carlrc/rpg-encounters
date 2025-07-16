from app.ai.character_agent import CharacterAgent
from app.models.character import Character
from app.models.player import Player
import logging

logger = logging.getLogger(__name__)

class AgentManager:
    """Manages persistent CharacterAgent instances to maintain conversation history."""
    
    def __init__(self):
        self._agents: dict[tuple[int, int], CharacterAgent] = {}
    
    def get_or_create_agent(self, player_id: int, character_id: int, 
                           character: Character, player: Player, 
                           system_prompt: str) -> CharacterAgent:

        key = (player_id, character_id)
        
        if key not in self._agents:
            logger.info(f"Creating new agent for player {player_id} and character {character_id}")
            self._agents[key] = CharacterAgent(character, player, system_prompt)
        else:
            logger.debug(f"Reusing existing agent for player {player_id} and character {character_id}")
        
        return self._agents[key]
