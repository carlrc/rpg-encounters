from functools import lru_cache
from typing import Tuple

from app.services.transcription import WhisperTranscriptionService
from app.services.tts import ElevenLabsTTS


def get_current_user_world() -> Tuple[int, int]:
    """Get the current user ID and world ID. For now, returns hardcoded values."""
    # TODO: Replace with actual authentication and world selection logic
    return 1, 1


@lru_cache(maxsize=1)
def get_transcription_service() -> WhisperTranscriptionService:
    """Factory function for transcription service"""
    return WhisperTranscriptionService(model_size="base")


@lru_cache(maxsize=1)
def get_tts_service() -> ElevenLabsTTS:
    """Factory function for TTS service"""
    return ElevenLabsTTS()
