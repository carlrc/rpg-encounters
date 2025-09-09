from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str = Field(description="JWT access token for authentication")
    token_type: str = Field(description="Type of token (usually 'bearer')")


class TokenData(BaseModel):
    user_id: str = Field(description="ID of the authenticated user")
    world_id: str = Field(description="ID of the world/context for this token")
    sub: EmailStr = Field(description="Subject (email) of the token holder")
    purpose: str = Field(description="Purpose/scope of this token")
    exp: int = Field(description="Token expiration timestamp (Unix time)")


class AuthStatusResponse(BaseModel):
    authenticated: bool = Field(
        description="Whether the user is currently authenticated"
    )
    user_id: int | None = Field(description="The authenticated user's ID, if logged in")


class LogoutResponse(BaseModel):
    success: bool = Field(description="Whether the logout operation was successful")
    message: str = Field(description="Human-readable message about the logout result")
