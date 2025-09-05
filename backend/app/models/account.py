from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AccountBase(BaseModel):
    email: str
    token: Optional[str] = None
    elevenlabs_token: Optional[str] = None


class AccountCreate(AccountBase):
    user_id: int


class AccountUpdate(BaseModel):
    email: Optional[str] = None
    token: Optional[str] = None
    elevenlabs_token: Optional[str] = None


class Account(AccountBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
