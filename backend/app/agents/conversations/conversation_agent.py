import asyncio
import logging

from langfuse import observe
from pydantic_ai import UnexpectedModelBehavior
from pydantic_ai.messages import (
    ModelResponse,
    TextPart,
)

from app.agents.agent_output import ConversationAgentOutput
from app.agents.base_agent import AgentDeps, BaseAgent, get_latest_user_message
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.data.conversation_store import ConversationStore
from app.models.influence import Influence
from app.models.reveal import RevealLayer
from app.services.context import ConvoContext
from app.services.conversation_manager import select_response

logger = logging.getLogger(__name__)


class ConversationAgentDeps(AgentDeps):
    context: ConvoContext


class ConversationAgent(BaseAgent):
    def __init__(
        self,
        system_prompt: str,
        # The LLM cannot reference the memories and reveals well when they are combined in system prompt
        instructions: str,
        conversation_store: ConversationStore,
        influence_calculator_agent: InfluenceCalculatorAgent,
    ):
        super().__init__()
        self.conversation_store = conversation_store
        self.influence_calculator_agent = influence_calculator_agent

        self.agent = self._generate_agent(
            system_prompt=system_prompt,
            instructions=instructions,
            output_type=ConversationAgentOutput,
        )

    @observe(as_type="generation")
    async def chat(
        self, player_transcript: str, deps: ConversationAgentDeps
    ) -> tuple[str, RevealLayer, Influence]:
        try:
            agent_task = self.agent.run(
                user_prompt=player_transcript,
                deps=deps,
                message_history=deps.context.messages,
            )
            influence_task = self.influence_calculator_agent.process(player_transcript)
            run_result, influence_result = await asyncio.gather(
                agent_task, influence_task
            )
            self.last_total_tokens = run_result.usage().total_tokens
        except UnexpectedModelBehavior as e:
            logger.error(f"Agent failure. {e.message}")
            raise
        except Exception as e:
            logger.error(f"Agent response generation failed. {e}")
            raise

        try:
            # Add to running earned total
            deps.context.influence.earned += influence_result.score

            selected_response, level = select_response(
                reveals=deps.context.reveals,
                agent_result=run_result.output,
                influence_score=deps.context.influence.score,
            )

            # User model request
            model_message = get_latest_user_message(run_result)
            # Cannot rely on the built in message history of Pydantic because it contains all the possible messages not only what was chosen
            model_response = ModelResponse(parts=[TextPart(content=selected_response)])
            await self.conversation_store.add_messages(
                player_id=deps.context.player.id,
                character_id=deps.context.character.id,
                encounter_id=deps.context.encounter.id,
                new_messages=[model_message, model_response],
            )

            # Add trace and span metadata
            deps.telemetry()
        except Exception as e:
            logger.error(f"Could not process agent response. {e}")
            raise

        return selected_response, level, deps.context.influence
