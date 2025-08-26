import logging

from langfuse import observe as langfuse_observe
from pydantic_ai import UnexpectedModelBehavior
from pydantic_ai.agent import AgentRunResult

from app.agents.agent_output import StandardAgentOutput
from app.agents.base_agent import BaseAgent
from app.agents.challenges.dependencies import ChallengeAgentDeps

logger = logging.getLogger(__name__)


class ChallengeAgent(BaseAgent):
    def __init__(self, system_prompt: str):
        super().__init__()
        self.agent = self._generate_agent(system_prompt=system_prompt)
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
