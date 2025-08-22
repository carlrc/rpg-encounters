from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage

from app.telemetry import TelemetryFunc

# TODO: Put this very high to avoid message trimming issue. This should be based on tokens anyways in future
MAX_MESSAGE_HISTORY = 30

MAX_RETRIES = 3


class AgentDeps(BaseModel):
    telemetry: TelemetryFunc


class BaseAgent:
    """Base class for agents that provides shared functionality."""

    def __init__(self):
        self.retries = MAX_RETRIES

    # TODO: This doesn't work well. Needs to be summarizing convo instead
    # https://ai.pydantic.dev/message-history/#summarize-old-messages
    async def _keep_recent_messages(
        self, messages: list[ModelMessage]
    ) -> list[ModelMessage]:
        """Keep only the last N messages to manage token usage."""
        return (
            messages[-MAX_MESSAGE_HISTORY:]
            if len(messages) > MAX_MESSAGE_HISTORY
            else messages
        )
