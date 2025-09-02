import os
from typing import Any

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.agent import ModelSettings
from pydantic_ai.messages import ModelMessage
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIModel

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
        self.temp = float(os.getenv("DEFAULT_MODEL_TEMP", "0.5"))
        self.metadata = {"temperature": self.temp}

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
            model = OpenAIModel(model_name="gpt-4o-mini")

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
