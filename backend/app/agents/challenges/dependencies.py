from typing import List

from pydantic_ai.messages import ModelMessage

from app.agents.base_agent import AgentDeps
from app.models.encounter import Encounter


class ChallengeAgentDeps(AgentDeps):
    encounter: Encounter
    messages: List[ModelMessage] | None
