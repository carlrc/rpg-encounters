from pydantic import BaseModel


class CharacterAgentOutput(BaseModel):
    standard_response: str
    negative_response: str
    privileged_response: str | None = None
    exclusive_response: str | None = None
    reveal_id: int | None = None
