import logging
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent, NativeOutput, RunContext
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models.openai import OpenAIModel

from app.models.character import Character
from app.models.player import Player
from app.models.trust import TRUST_CHANGE_MAX, TRUST_CHANGE_MIN

logger = logging.getLogger(__name__)

MAX_MESSAGE_HISTORY = 10


class TrustCalculatorAgentOutput(BaseModel):
    score: int
    reason: str


class TrustCalculatorAgent:
    def __init__(
        self,
        system_prompt: str,
        character: Character,
        player: Player,
    ):
        self.character = character
        self.player = player
        load_dotenv()

        agent = Agent(
            OpenAIModel(model_name="gpt-4o-mini"),
            system_prompt=system_prompt + "\n" + self.character.to_prompt(),
            instructions=self._build_base_instruction(),
            history_processors=[self._keep_recent_messages],
            output_type=NativeOutput(
                TrustCalculatorAgentOutput,
                description="Score the players message to your character",
            ),
        )

        self.run_result: AgentRunResult[TrustCalculatorAgentOutput] = None

        @agent.output_validator
        def validate_trust_adjustment(
            ctx: RunContext[Any], output: TrustCalculatorAgentOutput
        ) -> TrustCalculatorAgentOutput:
            output.score = max(TRUST_CHANGE_MIN, min(TRUST_CHANGE_MAX, output.score))

            return output

        self.agent = agent

    async def process(self, msg: str) -> TrustCalculatorAgentOutput:
        try:
            message_history = (
                self.run_result.all_messages() if self.run_result else None
            )
            self.run_result = await self.agent.run(
                msg,
                message_history=message_history,
            )
        except Exception as e:
            logger.error(f"Player message scoring failed. {e}")
            raise

        logger.info(
            f"{self.player.name} got trust adjustment {self.run_result.output.score}"
        )

        return self.run_result.output

    def _build_base_instruction(self) -> str:
        """Build streamlined trust-aware instruction for the AI"""

        base_instruction = f"""# Current Interaction Context
            You are speaking with **{self.player.name}**: a {self.player.race} {self.player.gender} {self.player.class_name} who looks like {self.player.appearance}."""

        return base_instruction

    async def _keep_recent_messages(
        self, messages: list[ModelMessage]
    ) -> list[ModelMessage]:
        """Keep only the last N messages to manage token usage."""
        return (
            messages[-MAX_MESSAGE_HISTORY:]
            if len(messages) > MAX_MESSAGE_HISTORY
            else messages
        )
