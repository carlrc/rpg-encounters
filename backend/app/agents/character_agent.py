from typing import Optional
from dotenv import load_dotenv
from app.models.character import Character
from pydantic_ai import Agent, NativeOutput, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage
from pydantic_ai.agent import AgentRunResult
from app.models.player import Player
from app.models.trust import TrustState
from app.models.nugget import NuggetLayer, TrustNugget
from app.services.nugget_service import NuggetService
from app.services.conversation_manager import ConversationManager
import logging
from app.agents.trust_scoring_agent import TrustCalculatorAgent
import asyncio

logger = logging.getLogger(__name__)

MAX_MESSAGE_HISTORY = 10


class CharacterAgentOutput(BaseModel):
    public_response: str
    privileged_response: Optional[str] = None
    exclusive_response: Optional[str] = None


class CharacterAgent:
    def __init__(
        self,
        character: Character,
        player: Player,
        system_prompt: str,
        # TODO: Trust should not be in this class
        trust_state: TrustState,
        conversation_manager: ConversationManager,
        trust_calculator_agent: TrustCalculatorAgent,
    ):
        load_dotenv()
        self.character = character
        self.player = player
        self.trust = trust_state
        self.convo_manager = conversation_manager
        self.trust_calculator_agent = trust_calculator_agent

        # Build trust-aware instructions
        trust_instruction = self._build_base_instruction(self.player)

        agent = Agent(
            OpenAIModel(model_name="gpt-4o"),
            system_prompt=system_prompt + "\n" + self.character.to_prompt(),
            instructions=trust_instruction,
            history_processors=[self._keep_recent_messages],
            output_type=NativeOutput(
                CharacterAgentOutput,
                description="Fill in the different response levels",
            ),
        )
        self.run_result: AgentRunResult[CharacterAgentOutput] = None

        # Decorator does not work on self.agent.instructions
        @agent.instructions
        def add_nuggets(ctx: RunContext[list[TrustNugget]]) -> str:
            all_nuggets = [nugget for nugget in ctx.deps]

            instruction_parts = []
            instruction_parts.append("\n# Available Nuggets")
            instruction_parts.append(
                "**IMPORTANT**: Select the nugget which is most relevant to the players message"
            )

            for nugget in all_nuggets:
                instruction_parts.append(
                    f"""
                    \n## {nugget.title}
                    **{NuggetLayer.PUBLIC.name}:** {nugget.level_1_content}
                    **{NuggetLayer.PRIVILEGED.name}:** {nugget.level_2_content or 'NONE'}
                    **{NuggetLayer.EXCLUSIVE.name}:** {nugget.level_3_content or 'NONE'}
                    """
                )

            return "".join(instruction_parts)

        # Set instance variable after decorators defined
        self.agent = agent

    async def chat(
        self, player_transcript: str, nuggets: list[TrustNugget]
    ) -> tuple[str, NuggetLayer, int]:
        try:
            agent_task = self.agent.run(
                user_prompt=player_transcript,
                deps=nuggets,
                message_history=self.convo_manager.get_history(),
            )
            trust_task = self.trust_calculator_agent.process(player_transcript)
            self.run_result, trust_result = await asyncio.gather(agent_task, trust_task)
        except Exception as e:
            logger.error(f"Response generation failed. {e}")
            raise

        self.trust.earned_trust += trust_result.score

        selected_response, level = NuggetService.select_response_by_trust(
            public_response=self.run_result.output.public_response,
            privileged_response=self.run_result.output.privileged_response,
            exclusive_response=self.run_result.output.exclusive_response,
            total_trust=self.trust.total_trust,
        )

        messages = self.run_result.new_messages()

        # Persist messages in custom history
        # Cannot rely on the built in message history of Pydantic because it contains all the possible messages not only what was chosen
        self.convo_manager.add_user_message(messages[0])
        self.convo_manager.add_agent_response(response=selected_response)

        return selected_response, level, trust_result.score

    def _build_base_instruction(self, player: Player) -> str:
        """Build streamlined trust-aware instruction for the AI"""

        base_instruction = f"""# Current Interaction Context
            You are speaking with **{player.name}**: a {player.race} {player.gender} {player.class_name} who looks like {player.appearance}."""

        return base_instruction

    async def _keep_recent_messages(
        self, messages: list[ModelMessage]
    ) -> list[ModelMessage]:
        """Keep only the last N messages to manage token usage."""
        return (
            messages[-MAX_MESSAGE_HISTORY:]
            if len(messages) > MAX_MESSAGE_HISTORY
            else messages
        )
