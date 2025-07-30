from typing import Any, Optional
from dotenv import load_dotenv
from app.models.character import Character
from pydantic_ai import Agent, NativeOutput, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage
from pydantic_ai.agent import AgentRunResult
from app.models.player import Player
from app.models.trust import TRUST_CHANGE_MIN, TRUST_CHANGE_MAX, TrustState
from app.models.nugget import NuggetLevelInfo
from app.services.nugget_service import NuggetService
from app.services.conversation_manager import ConversationManager

MAX_MESSAGE_HISTORY = 10


class CharacterAgentOutput(BaseModel):
    public_response: str
    privileged_response: Optional[str] = None
    exclusive_response: str
    trust_level_adjustment: float


class CharacterAgent:
    def __init__(
        self,
        character: Character,
        player: Player,
        system_prompt: str,
        trust_state: TrustState,
        conversation_manager: ConversationManager,
    ):
        load_dotenv()
        self.character = character
        self.player = player
        self.trust = trust_state
        self.convo_manager = conversation_manager

        # Build trust-aware instructions
        trust_instruction = self._build_base_instruction(
            self.character, self.player, self.trust
        )

        agent = Agent(
            OpenAIModel(model_name="gpt-4o"),
            system_prompt=system_prompt + "\n" + self.character.to_prompt(),
            instructions=trust_instruction,
            history_processors=[self._keep_recent_messages],
            output_type=NativeOutput(
                CharacterAgentOutput,
                description="Fill in the different response levels and accompanying with trust adjustment.",
            ),
        )
        self.run_result: AgentRunResult[CharacterAgentOutput] = None

        # Decorator does not work on self.agent
        @agent.instructions
        def add_nuggets(ctx: RunContext[list[NuggetLevelInfo]]) -> str:
            all_nuggets = [nugget for nugget in ctx.deps]

            instruction_parts = []

            for nugget in all_nuggets:
                instruction_parts.append("\n# Nuggets")
                instruction_parts.append("".join(f"- {nugget.level}: {nugget.content}"))

            return "".join(instruction_parts)

        @agent.output_validator
        def validate_trust_adjustment(
            ctx: RunContext[Any], output: CharacterAgentOutput
        ) -> CharacterAgentOutput:
            # Clamp trust adjustment to valid range
            output.trust_level_adjustment = max(
                TRUST_CHANGE_MIN, min(TRUST_CHANGE_MAX, output.trust_level_adjustment)
            )
            # Updated earned trust
            self.trust.earned_trust += output.trust_level_adjustment

            return output

        # Set instance variable after decorators defined
        self.agent = agent

    async def chat(
        self, player_transcript: str, nugget_levels: list[NuggetLevelInfo]
    ) -> str:
        self.run_result = await self.agent.run(
            player_transcript,
            deps=nugget_levels,
            message_history=self.convo_manager.get_history(),
        )

        selected_response = NuggetService.select_response_by_trust(
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

        return selected_response

    def _build_base_instruction(
        self, character: Character, player: Player, trust_state
    ) -> str:
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
