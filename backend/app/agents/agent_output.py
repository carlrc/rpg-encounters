from pydantic import BaseModel, Field


class ConversationAgentOutput(BaseModel):
    standard_response: str = Field(
        ..., description="Response using the standard reveal content"
    )
    negative_response: str = Field(
        ..., description="Negative response to the users message"
    )
    privileged_response: str | None = Field(
        None, description="Response using the privileged reveal content"
    )
    exclusive_response: str | None = Field(
        None, description="Response using the exclusive reveal content"
    )
    reveal_id: int | None = Field(
        None, description="Reveal ID used for generating responses"
    )


class StandardAgentOutput(BaseModel):
    response: str
