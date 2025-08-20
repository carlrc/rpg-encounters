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

from app.agents.agent_output import ConversationAgentOutput
from app.agents.base_agent import BaseAgent
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.agents.prompts.utils import (
    structure_character_memories,
    structure_encounter,
    structure_reveals,
)
from app.http import create_retrying_client
from app.models.character import Character
from app.models.influence import Influence
from app.models.memory import Memory
from app.models.player import Player
from app.models.reveal import Reveal, RevealLayer
from app.services.conversation_manager import ConversationManager, select_response

logger = logging.getLogger(__name__)


class ConversationAgentDeps(BaseModel):
    reveals: List[Reveal]
    encounter_description: str
    influence: Influence
    user_id: int


class ConversationAgent(BaseAgent):
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
                ConversationAgentOutput,
                description="Fill in the different response levels and return the ID of the reveal you used if it exists.",
            ),
            retries=self.retries,
            instrument=True,
        )
        self.run_result: AgentRunResult[ConversationAgentOutput] = None

        # Decorator does not work on self.agent.instructions
        @agent.instructions
        def add_reveals(ctx: RunContext[ConversationAgentDeps]) -> str:
            all_reveals = [reveal for reveal in ctx.deps.reveals]

            return structure_reveals(reveals=all_reveals)

        @agent.instructions
        def add_encounter(ctx: RunContext[ConversationAgentDeps]) -> str:
            return structure_encounter(ctx.deps.encounter_description)

        # Decorator does not work on self.agent.output_validator
        @agent.output_validator
        def validate_reveal_id(
            ctx: RunContext[ConversationAgentDeps], output: ConversationAgentOutput
        ) -> ConversationAgentOutput:
            # If empty array of reveals, don't allow hallucinations of reveal_id
            if not ctx.deps.reveals:
                output.reveal_id = None
            return output

        # Set instance variable after decorators defined
        self.agent = agent

    @langfuse_observe
    async def chat(
        self, player_transcript: str, deps: ConversationAgentDeps
    ) -> tuple[str, RevealLayer, Influence]:
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

        selected_response, level = select_response(
            reveals=deps.reveals,
            agent_result=self.run_result.output,
            # Pass total influence score
            influence_score=deps.influence.score,
        )

        # Persist messages in custom history
        # Cannot rely on the built in message history of Pydantic because it contains all the possible messages not only what was chosen
        self.convo_manager.add_user_message(message=self.run_result.new_messages()[0])
        self.convo_manager.add_agent_response(response=selected_response)

        get_client().update_current_trace(
            user_id=deps.user_id, name="positive-convo-agent", tags=["conversation"]
        )

        return selected_response, level, deps.influence
