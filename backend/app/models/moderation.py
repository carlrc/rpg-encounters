from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ModerationBase(BaseModel):
    text: str = Field(description="Content that was flagged for moderation")
    openai_id: str = Field(description="OpenAI moderation request ID")


class ModerationCreate(ModerationBase):
    user_id: int


class ModerationUpdate(BaseModel):
    text: Optional[str] = None
    openai_id: Optional[str] = None


class Moderation(ModerationBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
