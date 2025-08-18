import logging
from typing import List

from app.agents.conversation_agent import ConversationAgent
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.models.character import Character
from app.models.memory import Memory
from app.models.player import Player
from app.services.conversation_manager import ConversationManager

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages persistent ConversationAgent instances to maintain conversation history."""

    def __init__(self):
        self._agents: dict[tuple[int, int], ConversationAgent] = {}

    def get_or_create_agent(
        self,
        player_id: int,
        character_id: int,
        character: Character,
        player: Player,
        char_system_prompt: str,
        scoring_system_prompt: str,
        memories: List[Memory],
    ) -> ConversationAgent:

        key = (player_id, character_id)

        if key not in self._agents:
            logger.info(
                f"Creating new agent for player {player_id} and character {character_id}"
            )
            self._agents[key] = ConversationAgent(
                character=character,
                player=player,
                system_prompt=char_system_prompt,
                memories=memories,
                conversation_manager=ConversationManager(),
                influence_calculator_agent=InfluenceCalculatorAgent(
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
