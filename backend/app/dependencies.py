from functools import lru_cache
from typing import Tuple

from fastapi import Header, HTTPException, Request, status

from app.auth.session import get_session_user_id
from app.services.transcription import WhisperTranscriptionService


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


@lru_cache(maxsize=1)
def get_transcription_service() -> WhisperTranscriptionService:
    """Factory function for transcription service"""
    return WhisperTranscriptionService(model_size="base")
