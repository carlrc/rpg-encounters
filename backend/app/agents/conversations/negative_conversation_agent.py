import asyncio
import logging

from langfuse import observe as langfuse_observe
from pydantic_ai import UnexpectedModelBehavior
from pydantic_ai.messages import ModelResponse, TextPart

from app.agents.base_agent import AgentDeps, BaseAgent
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.data.conversation_store import ConversationStore
from app.models.influence import Influence
from app.services.context import ConvoContext

logger = logging.getLogger(__name__)


class NegativeConvoAgentDeps(AgentDeps):
    context: ConvoContext


class NegativeConvoAgent(BaseAgent):
    def __init__(
        self,
        system_prompt: str,
        conversation_store: ConversationStore,
        influence_calculator_agent: InfluenceCalculatorAgent,
    ):
        super().__init__()
        self.conversation_store = conversation_store
        self.influence_calculator_agent = influence_calculator_agent

        agent = self._generate_agent(system_prompt=system_prompt)

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
                message_history=deps.context.messages,
            )
            influence_task = self.influence_calculator_agent.process(player_transcript)
            run_result, influence_result = await asyncio.gather(
                agent_task, influence_task
            )
        except UnexpectedModelBehavior as e:
            logger.error(f"Agent failure. {e.message}")
            raise
        except Exception as e:
            logger.error(f"Agent response generation failed. {e}")
            raise

        try:
            # Add to running earned total
            deps.context.influence.earned += influence_result.score

            # User model request
            model_request = run_result.new_messages()[0]
            # Cannot rely on the built in message history of Pydantic because it contains all the possible messages not only what was chosen
            model_response = ModelResponse(parts=[TextPart(content=run_result.output)])
            await self.conversation_store.add_messages(
                player_id=deps.context.player.id,
                character_id=deps.context.character.id,
                encounter_id=deps.context.encounter.id,
                new_messages=[model_request, model_response],
            )

            # Add trace and span metadata
            deps.telemetry()

            return run_result.output, deps.context.influence
        except Exception as e:
            logger.error(f"Could not process agent response. {e}")
            raise
