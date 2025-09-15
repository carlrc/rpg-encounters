from typing import Tuple

from fastapi import Header, HTTPException, Request, WebSocket, status

from app.auth.session import get_session_user_id


def get_current_user_world(
    request: Request, x_world_id: int = Header(None)
) -> Tuple[int, int]:
    """Get user ID and world ID efficiently without DB lookup."""
    user_id = get_session_user_id(request)

    if x_world_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-World-Id header is required",
        )

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
