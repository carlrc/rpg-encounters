from pydantic import BaseModel


class ConversationAgentOutput(BaseModel):
    standard_response: str
    negative_response: str
    privileged_response: str | None = None
    exclusive_response: str | None = None
    reveal_id: int | None = None


class ChallengeAgentOutput(BaseModel):
    response: str
