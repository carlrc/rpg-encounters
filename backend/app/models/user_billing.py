from datetime import datetime

from pydantic import BaseModel, Field


class UserBillingBase(BaseModel):
    user_id: int = Field(..., description="User ID tied to this billing summary")
    available_tokens: int = Field(..., description="Current available token balance")
    last_used_tokens: int = Field(..., description="Last persisted usage baseline")
    total_used_tokens: int = Field(..., description="Total lifetime token usage")


class UserBillingCreate(UserBillingBase):
    pass


class UserBillingUpdate(BaseModel):
    available_tokens: int | None = Field(None)
    last_used_tokens: int | None = Field(None)
    total_used_tokens: int | None = Field(None)


class UserBilling(UserBillingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
