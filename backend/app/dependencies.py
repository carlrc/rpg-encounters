from typing import Tuple

from fastapi import Header, HTTPException, Request, WebSocket, status

from app.auth.session import (
    get_session_player_id,
    get_session_user_id,
    get_session_world_id,
)


def _validate_user_world(
    request: Request, x_world_id: str = Header(None)
) -> Tuple[int, int]:
    user_id = get_session_user_id(request=request)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if not x_world_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-World-Id header is required",
        )

    return int(user_id), int(x_world_id)


def validate_current_user_world(
    request: Request, x_world_id: str = Header(None)
) -> Tuple[int, int]:
    """Get user ID and world ID efficiently without DB lookup."""
    user_id, x_world_id = _validate_user_world(request=request, x_world_id=x_world_id)

    player_id = get_session_player_id(request=request)
    if player_id:
        # Players should not use sessions for standard endpoints
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return user_id, x_world_id


async def get_websocket_user_world(websocket: WebSocket) -> Tuple[int, int]:
    """Get user ID and world ID from WebSocket connection."""

    # Extract user_id from session (session middleware handles decoding)
    user_id = websocket.session.get("user_id")
    if not user_id:
        await websocket.close(code=1008)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # Get world_id from query parameters
    world_id = websocket.query_params.get("world_id")
    if not world_id:
        await websocket.close(code=1008)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return int(user_id), int(world_id)


def validate_current_player(request: Request) -> Tuple[int, int, int]:
    """Get player_id, user_id, and world_id for player sessions only."""
    user_id = get_session_user_id(request=request)
    world_id = get_session_world_id(request=request)
    player_id = get_session_player_id(request=request)

    if not user_id or not world_id or not player_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return int(player_id), int(user_id), int(world_id)


def validate_current_player_or_user(
    request: Request, x_world_id: str = Header(None)
) -> None:
    # If player validate player session
    if get_session_player_id(request=request):
        validate_current_player(request=request)
    else:
        # If user validate session and header
        validate_current_user_world(request=request, x_world_id=x_world_id)
