from functools import lru_cache
from typing import Optional, Tuple

from fastapi import Header, Request

from app.auth.session import get_current_user_id
from app.services.transcription import WhisperTranscriptionService


def get_current_user_world(
    request: Request, x_world_id: Optional[int] = Header(None)
) -> Tuple[int, int]:
    """Get the current user ID and world ID from session and header."""
    user_id = get_current_user_id(request)
    if not user_id:
        # Fallback to hardcoded user for backward compatibility during transition
        user_id = 1

    world_id = x_world_id if x_world_id is not None else 1  # Default to world 1
    return user_id, world_id


@lru_cache(maxsize=1)
def get_transcription_service() -> WhisperTranscriptionService:
    """Factory function for transcription service"""
    return WhisperTranscriptionService(model_size="base")
