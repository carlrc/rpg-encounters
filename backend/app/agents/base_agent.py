from pydantic_ai.messages import ModelMessage

MAX_MESSAGE_HISTORY = 20

MAX_RETRIES = 3


class BaseAgent:
    """Base class for agents that provides shared functionality."""

    def __init__(self):
        self.retries = MAX_RETRIES

    async def _keep_recent_messages(
        self, messages: list[ModelMessage]
    ) -> list[ModelMessage]:
        """Keep only the last N messages to manage token usage."""
        return (
            messages[-MAX_MESSAGE_HISTORY:]
            if len(messages) > MAX_MESSAGE_HISTORY
            else messages
        )
