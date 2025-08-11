from pydantic import BaseModel


class CharacterAgentOutput(BaseModel):
    public_response: str
    privileged_response: str | None = None
    exclusive_response: str | None = None
    reveal_id: int | None = None
