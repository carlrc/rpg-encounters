import logging
from typing import List

from langfuse import observe as langfuse_observe
from pydantic_ai import Agent, NativeOutput, RunContext, UnexpectedModelBehavior
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.agents.agent_output import StandardAgentOutput
from app.agents.base_agent import BaseAgent
from app.agents.challenges.dependencies import ChallengeAgentDeps
from app.agents.prompts.utils import structure_character_memories
from app.http import create_retrying_client
from app.models.character import Character
from app.models.memory import Memory
from app.models.player import Player

logger = logging.getLogger(__name__)


class CriticalFailureAgent(BaseAgent):
    def __init__(
        self,
        character: Character,
        player: Player,
        system_prompt: str,
        memories: List[Memory],
    ):
        super().__init__()
        agent = Agent(
            OpenAIModel(
                model_name="gpt-4o-mini",
                provider=OpenAIProvider(http_client=create_retrying_client()),
            ),
            instructions=system_prompt
            + "\n"
            + character.to_prompt()
            + "\n"
            + structure_character_memories(memories=memories, player=player),
            history_processors=[self._keep_recent_messages],
            output_type=NativeOutput(StandardAgentOutput),
            retries=self.retries,
            instrument=True,
        )
        self.run_result: AgentRunResult[StandardAgentOutput] = None

        @agent.instructions
        def add_encounter(ctx: RunContext[ChallengeAgentDeps]) -> str:
            if ctx.deps.encounter.description:
                return f"""# Physical Location Context
                    Your character is currently in the following encounter. Use this information as your physical world context.
                    {ctx.deps.encounter.description}
                    """
            else:
                return ""

        # Set instance variable after decorators defined
        self.agent = agent

    @langfuse_observe
    async def chat(self, player_transcript: str, deps: ChallengeAgentDeps) -> str:
        try:
            self.run_result = await self.agent.run(
                user_prompt=player_transcript, message_history=deps.messages, deps=deps
            )

            deps.telemetry()

            return self.run_result.output.response
        except UnexpectedModelBehavior as e:
            logger.error(f"Agent failure. {e.message}")
            raise
        except Exception as e:
            logger.error(f"Agent response generation failed. {e}")
            raise
