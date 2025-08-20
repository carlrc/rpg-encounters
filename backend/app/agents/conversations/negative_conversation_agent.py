import asyncio
import logging
from typing import List

from langfuse import get_client
from langfuse import observe as langfuse_observe
from pydantic import BaseModel
from pydantic_ai import Agent, NativeOutput, RunContext, UnexpectedModelBehavior
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from app.agents.agent_output import StandardAgentOutput
from app.agents.base_agent import BaseAgent
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.agents.prompts.utils import (
    structure_character_memories,
    structure_encounter,
)
from app.http import create_retrying_client
from app.models.character import Character
from app.models.influence import Influence
from app.models.memory import Memory
from app.models.player import Player
from app.services.conversation_manager import ConversationManager

logger = logging.getLogger(__name__)


class NegativeConvoAgentDeps(BaseModel):
    encounter_description: str
    influence: Influence
    user_id: int


class NegativeConvoAgent(BaseAgent):
    def __init__(
        self,
        character: Character,
        player: Player,
        system_prompt: str,
        memories: List[Memory],
        conversation_manager: ConversationManager,
        influence_calculator_agent: InfluenceCalculatorAgent,
    ):
        super().__init__()
        self.convo_manager = conversation_manager
        self.influence_calculator_agent = influence_calculator_agent

        agent = Agent(
            OpenAIModel(
                model_name="gpt-4o",
                provider=OpenAIProvider(http_client=create_retrying_client()),
            ),
            # Moving character.to_prompt() to instructions caused instability in output validation
            system_prompt=system_prompt + "\n" + character.to_prompt(),
            instructions=structure_character_memories(memories=memories, player=player),
            history_processors=[self._keep_recent_messages],
            output_type=NativeOutput(
                StandardAgentOutput,
                description="Fill in the different response levels and return the ID of the reveal you used if it exists.",
            ),
            retries=self.retries,
            instrument=True,
        )
        self.run_result: AgentRunResult[StandardAgentOutput] = None

        @agent.instructions
        def add_encounter(ctx: RunContext[NegativeConvoAgentDeps]) -> str:
            return structure_encounter(ctx.deps.encounter_description)

        # Set instance variable after decorators defined
        self.agent = agent

    @langfuse_observe
    async def chat(
        self, player_transcript: str, deps: NegativeConvoAgentDeps
    ) -> tuple[str, Influence]:
        try:
            agent_task = self.agent.run(
                user_prompt=player_transcript,
                deps=deps,
                message_history=self.convo_manager.get_history(),
            )
            influence_task = self.influence_calculator_agent.process(player_transcript)
            self.run_result, influence_result = await asyncio.gather(
                agent_task, influence_task
            )
        except UnexpectedModelBehavior as e:
            logger.error(f"Agent failure. {e.message}")
            raise
        except Exception as e:
            logger.error(f"Response generation failed. {e}")
            raise

        # Add to running earned total
        deps.influence.earned += influence_result.score

        # Persist messages in custom history
        # Cannot rely on the built in message history of Pydantic because this must be possibly shared with the standard conversation agent
        self.convo_manager.add_user_message(message=self.run_result.new_messages()[0])
        self.convo_manager.add_agent_response(response=self.run_result.output.response)

        get_client().update_current_trace(
            user_id=deps.user_id, name="negative-convo-agent", tags=["conversation"]
        )

        return self.run_result.output.response, deps.influence
