import logging

from langfuse import observe
from pydantic_ai import UnexpectedModelBehavior

from app.agents.base_agent import AgentDeps, BaseAgent
from app.models.encounter import Encounter

logger = logging.getLogger(__name__)


class ChallengeAgentDeps(AgentDeps):
    encounter: Encounter


class ChallengeAgent(BaseAgent):
    def __init__(self, system_prompt: str, instructions: str | None = None):
        super().__init__()
        self.agent = self._generate_agent(
            system_prompt=system_prompt, instructions=instructions
        )

    @observe(as_type="generation")
    async def chat(self, player_transcript: str, deps: ChallengeAgentDeps) -> str:
        try:
            run_result = await self.agent.run(user_prompt=player_transcript, deps=deps)
            self.last_total_tokens = run_result.usage().total_tokens

            deps.telemetry()

            return run_result.output
        except UnexpectedModelBehavior as e:
            logger.error(f"Agent failure. {e.message}")
            raise
        except Exception as e:
            logger.error(f"Agent response generation failed. {e}")
            raise
