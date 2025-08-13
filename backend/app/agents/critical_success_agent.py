import logging
from typing import List

from dotenv import load_dotenv
from pydantic_ai import Agent, NativeOutput
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.agents.agent_output import ChallengeAgentOutput
from app.agents.base_agent import BaseAgent
from app.http import create_retrying_client
from app.models.character import Character
from app.models.memory import Memory
from app.models.player import Player

logger = logging.getLogger(__name__)


class CriticalSuccessAgent(BaseAgent):
    def __init__(
        self,
        character: Character,
        player: Player,
        system_prompt: str,
        memories: List[Memory],
        reveals: List[str],
    ):
        super().__init__(character=character, player=player, memories=memories)
        load_dotenv()
        self.reveals = reveals
        self.agent = Agent(
            OpenAIModel(
                model_name="gpt-4o",
                provider=OpenAIProvider(http_client=create_retrying_client()),
            ),
            instructions=system_prompt
            + "\n"
            + self.character.to_prompt()
            + "\n"
            + self._add_reveals()
            + "\n"
            + self._build_base_instruction(),
            history_processors=[self._keep_recent_messages],
            output_type=NativeOutput(ChallengeAgentOutput),
        )
        self.run_result: AgentRunResult[ChallengeAgentOutput] = None

    async def chat(self, player_transcript: str) -> str:
        try:
            history = self.run_result.all_messages() if self.run_result else None
            self.run_result = await self.agent.run(
                user_prompt=player_transcript,
                message_history=history,
            )
            return self.run_result.output.response
        except Exception as e:
            logger.error(f"Critical success agent error. {e}")
            raise

    def _add_reveals(self) -> str:
        reveal_context = """
        # Reveals
        The following information should be used in your response.
        """

        if self.reveals:
            for reveal in self.reveals:
                reveal_context += f"""
            - {reveal}
            """

        return reveal_context
