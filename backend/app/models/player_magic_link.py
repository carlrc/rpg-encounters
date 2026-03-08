import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class PlayerMagicLinkRequest(BaseModel):
    player_id: int = Field(description="ID of the player to generate login link for")


class PlayerMagicLinkBase(BaseModel):
    player_id: int = Field(description="ID of the player this magic link belongs to")
    user_id: int = Field(description="ID of the user user this magic link belongs to")
    world_id: int = Field(description="ID of the world this magic link belongs to")
    token_hash: str = Field(description="SHA-256 hash of the magic link token")
    expires_at: datetime = Field(description="When this magic link expires")
    used: bool = Field(description="Whether this magic link has been used")


class PlayerMagicLinkCreate(PlayerMagicLinkBase):
    pass


class PlayerMagicLink(PlayerMagicLinkBase):
    id: uuid.UUID = Field(description="Unique identifier for this magic link")
    created_at: datetime = Field(description="When this magic link was created")
    used_at: datetime | None = Field(
        None, description="When this magic link was used, if applicable"
    )

    model_config = {"from_attributes": True}


class PlayerLoginResponse(BaseModel):
    login_url: str = Field(description="The login URL for the player")
    expires_at: datetime = Field(description="When this login link expires")
