import logging
import os

from fastapi import HTTPException, Request, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
is_local = os.getenv("ENVIRONMENT") != "local"


# https://www.starlette.io/middleware/#sessionmiddleware
class SessionConfig(BaseModel):
    secret_key: str = Field(
        default_factory=lambda: os.getenv(
            "SESSION_SECRET_KEY", "dev-secret-change-in-production"
        ),
        frozen=True,
    )
    session_cookie_name: str = Field(default="session", frozen=True)
    max_age: int = Field(default=60 * 60 * 12, frozen=True)  # 12 hours
    secure: bool = Field(default=not is_local, frozen=True)
    httponly: bool = Field(default=not is_local, frozen=True)


# Global config instance
SESSION_CONFIG = SessionConfig()


def destroy_session(request: Request) -> None:
    """Destroy the current session"""
    request.session.clear()


def get_session_user_id(request: Request) -> int:
    """
    Get user_id from trusted session - no DB lookup needed.
    The session is signed/encrypted, so we trust its contents.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return user_id
