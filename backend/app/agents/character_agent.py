from typing import List
from dotenv import load_dotenv
from app.models.character import Character
from pydantic_ai import Agent, NativeOutput, RunContext, UnexpectedModelBehavior
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.messages import ModelMessage
from pydantic_ai.agent import AgentRunResult
from app.models.player import Player
from app.models.trust import TrustState
from app.models.reveal import RevealLayer, Reveal
from app.services.conversation_manager import ConversationManager
import logging
from app.agents.trust_scoring_agent import TrustCalculatorAgent
import asyncio
from app.models.memory import Memory
from app.agents.character_agent_output import CharacterAgentOutput
from pydantic_ai.providers.openai import OpenAIProvider
from app.http import create_retrying_client

logger = logging.getLogger(__name__)

MAX_MESSAGE_HISTORY = 10


class CharacterAgent:
    def __init__(
        self,
        character: Character,
        player: Player,
        system_prompt: str,
        memories: List[Memory],
        # TODO: Trust should not be in this class
        trust_state: TrustState,
        conversation_manager: ConversationManager,
        trust_calculator_agent: TrustCalculatorAgent,
    ):
        load_dotenv()
        self.character = character
        self.player = player
        self.memories = memories
        self.trust = trust_state
        self.convo_manager = conversation_manager
        self.trust_calculator_agent = trust_calculator_agent

        agent = Agent(
            OpenAIModel(
                model_name="gpt-4o",
                provider=OpenAIProvider(http_client=create_retrying_client()),
            ),
            # Moving character.to_prompt() to instructions caused instability in output validation
            system_prompt=system_prompt + "\n" + self.character.to_prompt(),
            instructions=self._build_base_instruction(self.player),
            history_processors=[self._keep_recent_messages],
            output_type=NativeOutput(
                CharacterAgentOutput,
                description="Fill in the different response levels and return the ID of the reveal you used if it exists.",
            ),
        )
        self.run_result: AgentRunResult[CharacterAgentOutput] = None

        # Decorator does not work on self.agent.instructions
        @agent.instructions
        def add_reveals(ctx: RunContext[list[Reveal]]) -> str:
            all_reveals = [reveal for reveal in ctx.deps]

            if not all_reveals:
                return """**IMPORTANT**: No reveals available for this character. Refer to memories and character background."""

            instruction_parts = []
            instruction_parts.append("\n# Available Reveals")
            instruction_parts.append(
                "**IMPORTANT**: Select the reveal which is most relevant to the players message."
            )

            for reveal in all_reveals:
                instruction_parts.append(
                    f"""
                    \n## ID {reveal.id} - {reveal.title}
                    **{RevealLayer.PUBLIC.name}:** {reveal.level_1_content}
                    **{RevealLayer.PRIVILEGED.name}:** {reveal.level_2_content or 'NONE'}
                    **{RevealLayer.EXCLUSIVE.name}:** {reveal.level_3_content or 'NONE'}
                    """
                )

            return "".join(instruction_parts)

        # Decorator does not work on self.agent.output_validator
        @agent.output_validator
        def validate_reveal_id(
            ctx: RunContext[list[Reveal]], output: CharacterAgentOutput
        ) -> CharacterAgentOutput:
            # If empty array of reveals, don't allow hallucinations of reveal_id
            if not ctx.deps:
                output.reveal_id = None
            return output

        # Set instance variable after decorators defined
        self.agent = agent

    async def chat(
        self, player_transcript: str, reveals: list[Reveal]
    ) -> tuple[str, RevealLayer, int]:
        try:
            agent_task = self.agent.run(
                user_prompt=player_transcript,
                deps=reveals,
                message_history=self.convo_manager.get_history(),
            )
            trust_task = self.trust_calculator_agent.process(player_transcript)
            self.run_result, trust_result = await asyncio.gather(agent_task, trust_task)
        except UnexpectedModelBehavior as e:
            logger.error(f"Agent failure. {e.message}")
            raise
        except Exception as e:
            logger.error(f"Response generation failed. {e}")
            raise

        self.trust.earned_trust += trust_result.score

        selected_response, level = self.convo_manager.select_response(
            reveals=reveals,
            agent_result=self.run_result.output,
            total_trust=self.trust.total_trust,
        )

        # Persist messages in custom history
        # Cannot rely on the built in message history of Pydantic because it contains all the possible messages not only what was chosen
        self.convo_manager.add_user_message(message=self.run_result.new_messages()[0])
        self.convo_manager.add_agent_response(response=selected_response)

        return selected_response, level, trust_result.score

    def _build_base_instruction(self, player: Player) -> str:
        base_instruction = """
            # World Context
            The following are memories that shape your understanding of the world:
            """

        if self.memories:
            for memory in self.memories:
                base_instruction += f"""
            - {memory.content}
            """

        base_instruction += f"""
            # Current Interaction Context
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
