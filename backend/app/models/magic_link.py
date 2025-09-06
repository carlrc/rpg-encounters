import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class MagicLinkRequest(BaseModel):
    email: EmailStr = Field(description="Email address to send the magic link to")
    redirect_to: str | None = Field(
        None, description="URL to redirect to after successful authentication"
    )


class MagicLinkConsume(BaseModel):
    token: str = Field(description="Magic link token to consume for authentication")


class MagicLinkBase(BaseModel):
    user_id: int = Field(description="ID of the user this magic link belongs to")
    expires_at: datetime = Field(description="When this magic link expires")
    used: bool = Field(description="Whether this magic link has been used")
    redirect_to: str | None = Field(
        None, description="URL to redirect to after authentication"
    )


class MagicLinkCreate(MagicLinkBase):
    token_hash: str = Field(description="SHA-256 hash of the magic link token")
    device_nonce_hash: str = Field(
        description="SHA-256 hash of the device nonce for binding"
    )


class MagicLink(MagicLinkBase):
    id: uuid.UUID = Field(description="Unique identifier for this magic link")
    token_hash: str = Field(description="SHA-256 hash of the magic link token")
    device_nonce_hash: str = Field(
        description="SHA-256 hash of the device nonce for binding"
    )
    created_at: datetime = Field(description="When this magic link was created")
    used_at: datetime | None = Field(
        None, description="When this magic link was used, if applicable"
    )

    model_config = {"from_attributes": True}


class MagicLinkResponse(BaseModel):
    success: bool = Field(description="Whether the magic link request was successful")
    token: str | None = Field(
        None,
        description="Magic link token for testing (will be removed when implementing email)",
    )
    message: str = Field(description="Human-readable message about the request result")


class MagicLinkConsumeResponse(BaseModel):
    success: bool = Field(
        description="Whether the magic link consumption was successful"
    )
    redirect_to: str | None = Field(
        None, description="URL to redirect to after successful authentication"
    )
    message: str = Field(
        description="Human-readable message about the consumption result"
    )
