import logging
from typing import List
from dotenv import load_dotenv
from pydantic_ai import Agent, NativeOutput, UnexpectedModelBehavior
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.agent import AgentRunResult
from app.agents.agent_output import ChallengeAgentOutput
from app.http import create_retrying_client
from app.models.character import Character
from app.models.memory import Memory
from app.models.player import Player
from app.services.conversation_manager import ConversationManager
from app.agents.base_agent import BaseAgent
from backend.app.models.reveal import Reveal

logger = logging.getLogger(__name__)


class ChallengeAgent(BaseAgent):
    def __init__(
        self,
        character: Character,
        player: Player,
        system_prompt: str,
        memories: List[Memory],
        conversation_manager: ConversationManager,
    ):
        super().__init__(character=character, player=player, memories=memories)
        load_dotenv()
        self.convo_manager = conversation_manager

        agent = Agent(
            OpenAIModel(
                model_name="gpt-4o",
                provider=OpenAIProvider(http_client=create_retrying_client()),
            ),
            # Moving character.to_prompt() to instructions caused instability in output validation
            system_prompt=system_prompt + "\n" + self.character.to_prompt(),
            instructions=self._build_base_instruction(),
            history_processors=[self._keep_recent_messages],
            output_type=NativeOutput(ChallengeAgentOutput),
        )
        self.run_result: AgentRunResult[ChallengeAgentOutput] = None

        # Set instance variable after decorators defined
        self.agent = agent

    async def chat(self, player_transcript: str, reveals: list[Reveal]) -> str:
        try:
            self.run_result = await self.agent.run(
                user_prompt=player_transcript,
                deps=reveals,
                message_history=self.convo_manager.get_history(),
            )
        except UnexpectedModelBehavior as e:
            logger.error(f"Agent failure. {e.message}")
            raise
        except Exception as e:
            logger.error(f"Response generation failed. {e}")
            raise
