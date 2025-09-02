from typing import Dict, List, Literal

from pydantic import BaseModel, Field
from pydantic_ai.messages import ModelMessage


class ConversationBase(BaseModel):
    player_id: int = Field(..., description="ID of the player in this conversation")
    character_id: int = Field(
        ..., description="ID of the character in this conversation"
    )
    encounter_id: int = Field(
        ..., description="ID of the encounter this conversation belongs to"
    )
    messages: List[ModelMessage] = Field(
        ..., description="List of conversation messages"
    )


class ConversationCreate(ConversationBase):
    """Conversation creation model"""

    pass


class ConversationUpdate(ConversationBase):
    """Conversation update model"""

    messages: List[ModelMessage] | None = None


class Conversation(ConversationBase):
    id: int

    model_config = {"from_attributes": True}


class ConversationData(BaseModel):
    type: Literal["conversation_data"] = Field(
        "conversation_data", description="Data type for websocket listener"
    )
    influence: int = Field(
        ..., description="Influence score. Can be earned or from D20 roll"
    )
    reveals: List[Dict] = Field(
        [], description="Available manipulated reveals with level information"
    )
