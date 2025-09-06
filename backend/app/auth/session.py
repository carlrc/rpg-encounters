import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from starlette.middleware.sessions import SessionMiddleware

from app.data.user_store import UserStore
from app.models.user import User


class SessionConfig:
    SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "dev-secret-change-in-production")
    SESSION_COOKIE_NAME = "session"
    MAX_AGE = 60 * 60 * 24 * 7  # 7 days
    SECURE = True
    HTTPONLY = True
    SAMESITE = "lax"


def get_session_middleware():
    """Get configured SessionMiddleware class for FastAPI"""
    return SessionMiddleware


def create_session(request: Request, user_id: int) -> None:
    """Create a new session for the user"""
    request.session["user_id"] = user_id
    request.session["authenticated_at"] = datetime.now(timezone.utc).isoformat()


def destroy_session(request: Request) -> None:
    """Destroy the current session"""
    request.session.clear()


def get_current_user_id(request: Request) -> int | None:
    """Get current user ID from session, returns None if not authenticated"""
    user_id = request.session.get("user_id")
    authenticated_at = request.session.get("authenticated_at")

    if not user_id or not authenticated_at:
        return None

    # Check if session is expired (optional additional check)
    try:
        auth_time = datetime.fromisoformat(authenticated_at)
        if datetime.now(timezone.utc) - auth_time > timedelta(
            seconds=SessionConfig.MAX_AGE
        ):
            return None
    except (ValueError, TypeError):
        return None

    return user_id


async def get_current_user(request: Request) -> User:
    """
    FastAPI dependency to get the current authenticated user.
    Raises HTTPException if not authenticated.
    """
    user_id = get_current_user_id(request)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # Get user from database
    user_store = UserStore(user_id=user_id)
    user = await user_store.get_by_id(user_id)

    if not user:
        # User was deleted but session still exists
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_optional_current_user(request: Request) -> User | None:
    """
    FastAPI dependency to get the current authenticated user.
    Returns None if not authenticated (does not raise exception).
    """
    user_id = get_current_user_id(request)

    if not user_id:
        return None

    # Get user from database
    user_store = UserStore(user_id=user_id)
    user = await user_store.get_by_id(user_id)

    return user


def require_auth() -> Annotated[User, Depends(get_current_user)]:
    """Convenience function for requiring authentication in route dependencies"""
    return Depends(get_current_user)


def optional_auth() -> Annotated[User | None, Depends(get_optional_current_user)]:
    """Convenience function for optional authentication in route dependencies"""
    return Depends(get_optional_current_user)
