import logging
from typing import List

from langfuse import observe as langfuse_observe
from pydantic_ai import UnexpectedModelBehavior
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.messages import ModelMessage

from app.agents.agent_output import StandardAgentOutput
from app.agents.base_agent import AgentDeps, BaseAgent
from app.models.encounter import Encounter

logger = logging.getLogger(__name__)


class ChallengeAgentDeps(AgentDeps):
    encounter: Encounter
    messages: List[ModelMessage] | None


class ChallengeAgent(BaseAgent):
    def __init__(self, system_prompt: str, instructions: str | None = None):
        super().__init__()
        self.agent = self._generate_agent(
            system_prompt=system_prompt, instructions=instructions
        )
        self.run_result: AgentRunResult[StandardAgentOutput] = None

    @langfuse_observe
    async def chat(self, player_transcript: str, deps: ChallengeAgentDeps) -> str:
        try:
            self.run_result = await self.agent.run(
                user_prompt=player_transcript, message_history=deps.messages, deps=deps
            )

            deps.telemetry()

            return self.run_result.output
        except UnexpectedModelBehavior as e:
            logger.error(f"Agent failure. {e.message}")
            raise
        except Exception as e:
            logger.error(f"Agent response generation failed. {e}")
            raise
