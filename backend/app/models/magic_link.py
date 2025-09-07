import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class MagicLinkRequest(BaseModel):
    email: EmailStr = Field(description="Email address to send the magic link to")
    redirect_to: str = Field(
        description="URL to redirect to after successful authentication"
    )


class MagicLinkBase(BaseModel):
    user_id: int = Field(description="ID of the user this magic link belongs to")
    token_hash: str = Field(description="SHA-256 hash of the magic link token")
    device_nonce_hash: str = Field(
        description="SHA-256 hash of the device nonce for binding"
    )
    expires_at: datetime = Field(description="When this magic link expires")
    used: bool = Field(description="Whether this magic link has been used")
    redirect_to: str = Field(description="URL to redirect to after authentication")


class MagicLinkCreate(MagicLinkBase):
    pass


class MagicLink(MagicLinkBase):
    id: uuid.UUID = Field(description="Unique identifier for this magic link")
    created_at: datetime = Field(description="When this magic link was created")
    used_at: datetime | None = Field(
        None, description="When this magic link was used, if applicable"
    )

    model_config = {"from_attributes": True}


class MagicLinkConsumeResponse(BaseModel):
    redirect_to: str = Field(
        description="URL to redirect to after successful authentication"
    )
