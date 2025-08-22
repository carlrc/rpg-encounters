from functools import lru_cache
from typing import Optional, Tuple

from fastapi import Header

from app.services.transcription import WhisperTranscriptionService
from app.services.tts import ElevenLabsTTS


def get_current_user_world(x_world_id: Optional[int] = Header(None)) -> Tuple[int, int]:
    """Get the current user ID and world ID. User ID is hardcoded, world ID comes from header."""
    user_id = 1  # Still hardcoded for now
    world_id = x_world_id if x_world_id is not None else 1  # Default to world 1
    return user_id, world_id


@lru_cache(maxsize=1)
def get_transcription_service() -> WhisperTranscriptionService:
    """Factory function for transcription service"""
    return WhisperTranscriptionService(model_size="base")


@lru_cache(maxsize=1)
def get_tts_service() -> ElevenLabsTTS:
    """Factory function for TTS service"""
    return ElevenLabsTTS()
