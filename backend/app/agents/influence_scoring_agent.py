import logging
from typing import Any

from langfuse import get_client
from langfuse import observe as langfuse_observe
from pydantic import BaseModel
from pydantic_ai import RunContext, UnexpectedModelBehavior

from app.agents.base_agent import BaseAgent
from app.models.character import Character
from app.models.influence import INFLUENCE_CHANGE_MAX, INFLUENCE_CHANGE_MIN
from app.models.player import Player

logger = logging.getLogger(__name__)


class InfluenceCalculatorAgentOutput(BaseModel):
    score: int
    reason: str


class InfluenceCalculatorAgent(BaseAgent):
    def __init__(
        self,
        system_prompt: str,
        character: Character,
        player: Player,
    ):
        super().__init__()
        self.character = character
        self.player = player

        agent = self._generate_agent(
            system_prompt=system_prompt, output_type=InfluenceCalculatorAgentOutput
        )

        @agent.output_validator
        def validate_influence_adjustment(
            ctx: RunContext[Any], output: InfluenceCalculatorAgentOutput
        ) -> InfluenceCalculatorAgentOutput:
            output.score = max(
                INFLUENCE_CHANGE_MIN, min(INFLUENCE_CHANGE_MAX, output.score)
            )

            return output

        self.agent = agent

    @langfuse_observe
    async def process(self, msg: str) -> InfluenceCalculatorAgentOutput:
        try:
            run_result = await self.agent.run(msg)

            logger.info(
                f"{self.player.name} influence adjustment {run_result.output.score}"
            )

            # Called from other agents, therefore add to their traces
            get_client().update_current_span(name="influence-agent")

            return run_result.output
        except UnexpectedModelBehavior as e:
            logger.error(f"Agent failure. {e.message}")
            raise
        except Exception as e:
            logger.error(f"Agent response generation failed. {e}")
            raise

    def _build_base_instruction(self) -> str:
        """Build streamlined influence-aware instruction for the AI"""

        base_instruction = f"""# Current Interaction Context
            You are interacting with **{self.player.name}**: a {self.player.race} {self.player.gender} {self.player.class_name} who looks like {self.player.appearance}."""

        return base_instruction
