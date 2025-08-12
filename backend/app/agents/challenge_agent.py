import logging
from typing import List
from dotenv import load_dotenv
from pydantic_ai import Agent, NativeOutput
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.agent import AgentRunResult
from app.agents.agent_output import ChallengeAgentOutput
from app.http import create_retrying_client
from app.models.character import Character
from app.models.memory import Memory
from app.models.player import Player
from app.agents.base_agent import BaseAgent
from app.services.ability_challenge import D20Outcomes

logger = logging.getLogger(__name__)


class ChallengeAgent(BaseAgent):
    def __init__(
        self,
        character: Character,
        player: Player,
        system_prompt: str,
        memories: List[Memory],
        reveals: List[str],
        d20_value: int,
    ):
        super().__init__(character=character, player=player, memories=memories)
        load_dotenv()
        self.reveals = reveals
        self.d20_value = d20_value
        self.agent = Agent(
            OpenAIModel(
                model_name="gpt-4o",
                provider=OpenAIProvider(http_client=create_retrying_client()),
            ),
            # Moving character.to_prompt() to instructions caused instability in output validation
            system_prompt=system_prompt + "\n" + self.character.to_prompt(),
            instructions=self._build_base_instruction()
            + "\n"
            + self._build_reveal_context()
            + "\n"
            + self._build_response_instructions(),
            history_processors=[self._keep_recent_messages],
            output_type=NativeOutput(ChallengeAgentOutput),
        )
        self.run_result: AgentRunResult[ChallengeAgentOutput] = None

    async def chat(
        self,
        player_transcript: str,
    ) -> str:
        try:
            history = self.run_result.all_messages() if self.run_result else None
            self.run_result = await self.agent.run(
                user_prompt=player_transcript,
                message_history=history,
            )
            return self.run_result.output.response
        except Exception as e:
            logger.error(f"Challenge agent failure. {e}")
            raise

    def _build_reveal_context(self) -> str:
        """Build reveal context"""
        reveal_context = """
            # Reveals
            The following information should be used in your response.
            """

        if self.memories:
            for reveal in self.reveals:
                reveal_context += f"""
            - {reveal}
            """

        return reveal_context

    def _build_response_instructions(self) -> str:
        """Build reveal context"""
        if self.d20_value == D20Outcomes.CRITICAL_SUCCESS:
            instructions = "**CRITICAL SUCCESS**: should be a VERY enthusiastic response to the players inquiry and contain as much information (e.g., reveals, memories) as possible, and can ignore character limits."
        elif self.d20_value == D20Outcomes.CRITICAL_FAILURE:
            instructions = "**CRITICAL FAILURE**: should be a VERY negative response (e.g., total rejection) to the players inquiry and be harsh (e.g., include profanity)."
        else:
            instructions = "**STANDARD**: should be generic and without much depth."

        return f"""
            # Response Instructions
            **IMPORTANT**: Follow these speaking style instructions closely.
            {instructions}
            """
