from typing import List

from pydantic_ai.messages import ModelMessage

from app.models.character import Character
from app.models.memory import Memory
from app.models.player import Player

MAX_MESSAGE_HISTORY = 10

MAX_RETRIES = 3


class BaseAgent:
    """Base class for agents that provides shared functionality."""

    def __init__(self, character: Character, player: Player, memories: List[Memory]):
        self.character = character
        self.player = player
        self.memories = memories
        self.retries = MAX_RETRIES

    def _build_base_instruction(self) -> str:
        """Build base instruction with world context and player information."""
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
            You are speaking with a {self.player.race}, {self.player.gender}, {self.player.class_name} who looks like {self.player.appearance}."""

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
