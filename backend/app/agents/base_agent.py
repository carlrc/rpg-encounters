import os
from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.agent import ModelSettings
from pydantic_ai.messages import ModelMessage, ToolReturnPart
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel

from app.telemetry import TelemetryFunc

# TODO: Set arbitrarily high to avoid trimming issue (_keep_recent_messages doesn't work). Should be based on tokens in the future anyways.
MAX_MESSAGE_HISTORY = 20

MAX_RETRIES = 3


class AgentDeps(BaseModel):
    telemetry: TelemetryFunc


class BaseAgent:
    """Base class for agents that provides shared functionality."""

    def __init__(self):
        self.retries = MAX_RETRIES
        self.temp = float(os.getenv("DEFAULT_MODEL_TEMP", "0.5"))
        self.metadata = {"temperature": self.temp}

    # https://ai.pydantic.dev/message-history/#summarize-old-messages
    async def _keep_recent_messages(
        self, messages: list[ModelMessage]
    ) -> list[ModelMessage]:
        """Keep only the last N messages to manage token usage."""

        # https://github.com/pydantic/pydantic-ai/issues/2050#issuecomment-3185056339
        def message_at_index_contains_tool_return_parts(
            messages: list[ModelMessage], index: int
        ) -> bool:
            return any(
                isinstance(part, ToolReturnPart) for part in messages[index].parts
            )

        number_of_messages = len(messages)

        if number_of_messages <= MAX_MESSAGE_HISTORY:
            return messages

        # Calculate how many complete pairs we can keep within the limit
        # Ensure we always keep an even number of messages (complete pairs)
        messages_to_keep = MAX_MESSAGE_HISTORY
        if messages_to_keep % 2 != 0:
            messages_to_keep -= 1  # Make it even to preserve pairs

        # Check for tool return parts at the boundary
        if message_at_index_contains_tool_return_parts(
            messages, number_of_messages - messages_to_keep
        ):
            return messages

        # TODO: Internally pydantic doesn't adjust the index of latest messages after this and then using new_messages() returns an empty array incorrectly
        trimmed_messages = messages[-messages_to_keep:]
        return trimmed_messages

    def _generate_agent(
        self,
        model: Model | None = None,
        system_prompt: str | None = None,
        instructions: str | None = None,
        output_type: Any | None = None,
        model_temp: float | None = None,
    ):
        """Generate a standard agent with common configuration."""
        agent_kwargs = {
            "history_processors": [self._keep_recent_messages],
            "retries": self.retries,
            "instrument": True,
        }

        if not model:
            model = OpenAIChatModel(model_name=os.getenv("DEFAULT_MODEL_NAME"))

        agent_kwargs["model"] = model

        if not model_temp:
            model_temp = self.temp

        agent_kwargs["model_settings"] = ModelSettings(temperature=model_temp)

        if system_prompt:
            agent_kwargs["system_prompt"] = system_prompt

        if instructions:
            agent_kwargs["instructions"] = instructions

        if output_type:
            agent_kwargs["output_type"] = output_type

        return Agent(**agent_kwargs)
