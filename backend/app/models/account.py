from datetime import datetime

from pydantic import BaseModel


class AccountBase(BaseModel):
    email: str
    elevenlabs_token: str | None = None


class AccountCreate(AccountBase):
    user_id: int


class AccountUpdate(BaseModel):
    email: str | None = None
    elevenlabs_token: str | None = None


class Account(AccountBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
