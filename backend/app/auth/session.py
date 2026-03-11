import logging
import os

from dotenv import load_dotenv
from fastapi import Request, WebSocket
from pydantic import BaseModel, Field

from app.http import SESSION_COOKIE
from app.utils import get_or_throw

logger = logging.getLogger(__name__)


# main.app loads session config before load, so re-declaring
load_dotenv()

IS_LOCAL = get_or_throw("ENVIRONMENT") == "local"
IS_LAN = IS_LOCAL and bool(os.getenv("LAN_PUBLIC_URL"))


class UserSession(BaseModel):
    user_id: int = Field(..., frozen=True)
    world_id: int = Field(..., frozen=True)


class PlayerSession(UserSession):
    player_id: int = Field(..., frozen=True)


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
    same_site: str = Field(default="lax", frozen=True)


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


def get_session_world_id(request: Request) -> str | None:
    """
    Get world_id from session if it exists.
    """
    return request.session.get("world_id")


def get_websocket_session_ids(
    websocket: WebSocket,
) -> tuple[str | None, str | None, str | None]:
    """Parse IDs from websocket session/query params without asserting."""
    user_id = websocket.session.get("user_id")
    player_id = websocket.session.get("player_id")
    if player_id:
        # Player sessions is tied to a world
        world_id = websocket.session.get("world_id")
    else:
        # User sessions are not tied to a world
        world_id = websocket.query_params.get("world_id")
    return user_id, world_id, player_id
