import logging

from dotenv import load_dotenv
from fastapi import Request
from pydantic import BaseModel, Field

from app.http import SESSION_COOKIE
from app.utils import get_or_throw

logger = logging.getLogger(__name__)


# main.app loads session config before load, so re-declaring
load_dotenv()

IS_LOCAL = get_or_throw("ENVIRONMENT") == "local"


# https://www.starlette.io/middleware/#sessionmiddleware
class SessionConfig(BaseModel):
    secret_key: str = Field(
        default_factory=lambda: get_or_throw("SESSION_SECRET_KEY"),
        frozen=True,
    )
    session_cookie_name: str = Field(default=SESSION_COOKIE, frozen=True)
    max_age: int = Field(default=60 * 60 * 2, frozen=True)  # 2 hours
    secure: bool = Field(default=not IS_LOCAL, frozen=True)
    httponly: bool = Field(default=not IS_LOCAL, frozen=True)


# Global config instance
SESSION_CONFIG = SessionConfig()


def destroy_session(request: Request) -> None:
    """Destroy the current session"""
    request.session.clear()


def get_session_user_id(request: Request) -> str | None:
    """
    Get user_id from session if it exists.
    """
    return request.session.get("user_id")


def get_session_player_id(request: Request) -> str | None:
    """
    Get player_id from session if it exists.
    """
    return request.session.get("player_id")
