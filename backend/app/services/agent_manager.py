from typing import List
from app.agents.character_agent import CharacterAgent
from app.models.character import Character
from app.models.player import Player
import logging
from app.models.trust import TrustState
from app.services.conversation_manager import ConversationManager
from app.agents.trust_scoring_agent import TrustCalculatorAgent
from app.models.memory import Memory

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages persistent CharacterAgent instances to maintain conversation history."""

    def __init__(self):
        self._agents: dict[tuple[int, int], CharacterAgent] = {}

    def get_or_create_agent(
        self,
        player_id: int,
        character_id: int,
        character: Character,
        player: Player,
        char_system_prompt: str,
        scoring_system_prompt: str,
        memories: List[Memory],
        trust_state: TrustState,
    ) -> CharacterAgent:

        key = (player_id, character_id)

        if key not in self._agents:
            logger.info(
                f"Creating new agent for player {player_id} and character {character_id}"
            )
            self._agents[key] = CharacterAgent(
                character=character,
                player=player,
                system_prompt=char_system_prompt,
                memories=memories,
                trust_state=trust_state,
                conversation_manager=ConversationManager(),
                trust_calculator_agent=TrustCalculatorAgent(
                    system_prompt=scoring_system_prompt,
                    character=character,
                    player=player,
                ),
            )
        else:
            logger.debug(
                f"Reusing existing agent for player {player_id} and character {character_id}"
            )

        return self._agents[key]
