from fastapi import Header, HTTPException, Request, WebSocket, status

from app.auth.session import (
    PlayerSession,
    UserSession,
    get_session_player_id,
    get_session_user_id,
    get_session_world_id,
    get_websocket_session_ids,
)


def _validate_user_world(
    request: Request, x_world_id: str = Header(None)
) -> UserSession:
    user_id = get_session_user_id(request=request)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if not x_world_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-World-Id header is required",
        )

    return UserSession(user_id=int(user_id), world_id=int(x_world_id))


def validate_current_user_world(
    request: Request, x_world_id: str = Header(None)
) -> UserSession:
    """Get user ID and world ID efficiently without DB lookup."""
    user_session = _validate_user_world(request=request, x_world_id=x_world_id)

    player_id = get_session_player_id(request=request)
    if player_id:
        # Players should not use sessions for standard endpoints
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return user_session


async def validate_websocket_session(
    websocket: WebSocket,
) -> UserSession | PlayerSession | None:
    """Get session IDs from WebSocket connection and return a typed session or None."""
    user_id, world_id, player_id = get_websocket_session_ids(websocket)
    # Assert on standard session elements
    if not user_id or not world_id:
        return None

    if player_id:
        return PlayerSession(
            user_id=int(user_id),
            world_id=int(world_id),
            player_id=int(player_id),
        )
    else:
        return UserSession(user_id=int(user_id), world_id=int(world_id))


def validate_current_player(request: Request) -> PlayerSession:
    """Get player_id, user_id, and world_id for player sessions only."""
    user_id = get_session_user_id(request=request)
    world_id = get_session_world_id(request=request)
    player_id = get_session_player_id(request=request)

    if not user_id or not world_id or not player_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return PlayerSession(
        user_id=int(user_id), world_id=int(world_id), player_id=int(player_id)
    )


def validate_current_player_or_user(
    request: Request, x_world_id: str = Header(None)
) -> UserSession | PlayerSession:
    """Validate player or user session."""
    # If player validate player session
    if get_session_player_id(request=request):
        return validate_current_player(request=request)
    else:
        # If user validate session and header
        return validate_current_user_world(request=request, x_world_id=x_world_id)


def validate_current_user_id(request: Request) -> int:
    """Validate user session only."""
    user_id = get_session_user_id(request=request)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    # Endpoints which include players should use different validation fn
    if get_session_player_id(request=request):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return int(user_id)
