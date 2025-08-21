import asyncio
import logging
from typing import List, Optional

from langfuse import observe as langfuse_observe
from pydantic import BaseModel
from pydantic_ai import Agent, NativeOutput, RunContext, UnexpectedModelBehavior
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.messages import (
    ModelMessage,
    ModelResponse,
    TextPart,
)
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
from app.data.conversation_store import ConversationStore
from app.http import create_retrying_client
from app.models.character import Character
from app.models.encounter import Encounter
from app.models.influence import Influence
from app.models.memory import Memory
from app.models.player import Player
from app.models.reveal import Reveal, RevealLayer
from app.services.conversation_manager import select_response
from app.telemetry import TelemetryFunc

logger = logging.getLogger(__name__)


class ConversationAgentDeps(BaseModel):
    reveals: List[Reveal]
    encounter: Encounter
    influence: Influence
    user_id: int
    telemetry: Optional[TelemetryFunc]
    message_history: List[ModelMessage] | None


class ConversationAgent(BaseAgent):
    def __init__(
        self,
        character: Character,
        player: Player,
        system_prompt: str,
        memories: List[Memory],
        conversation_store: ConversationStore,
        influence_calculator_agent: InfluenceCalculatorAgent,
    ):
        super().__init__()
        self.conversation_store = conversation_store
        self.influence_calculator_agent = influence_calculator_agent
        self.player = player
        self.character = character
        agent = Agent(
            OpenAIModel(
                model_name="gpt-4o-mini",
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
            return structure_encounter(ctx.deps.encounter.description)

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
                message_history=deps.message_history,
            )
            influence_task = self.influence_calculator_agent.process(player_transcript)
            self.run_result, influence_result = await asyncio.gather(
                agent_task, influence_task
            )
        except UnexpectedModelBehavior as e:
            logger.error(f"Convo agent failure. {e.message}")
            raise
        except Exception as e:
            logger.error(f"Convo agent response generation failed. {e}")
            raise

        try:
            # Add to running earned total
            deps.influence.earned += influence_result.score

            selected_response, level = select_response(
                reveals=deps.reveals,
                agent_result=self.run_result.output,
                influence_score=deps.influence.score,
            )

            # TODO: I think this is a bit blunt and can remove failed calls we might want to keep
            # User model request
            model_request = self.run_result.new_messages()[0]
            # Cannot rely on the built in message history of Pydantic because it contains all the possible messages not only what was chosen
            model_response = ModelResponse(parts=[TextPart(content=selected_response)])
            self.conversation_store.add_messages(
                player_id=self.player.id,
                character_id=self.character.id,
                encounter_id=deps.encounter.id,
                new_messages=[model_request, model_response],
            )

            # Add trace and span metadata
            deps.telemetry()
        except Exception as e:
            logger.error(f"Convo agent could not process response. {e}")
            raise

        return selected_response, level, deps.influence
