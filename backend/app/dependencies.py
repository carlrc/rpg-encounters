from functools import lru_cache
from app.services.agent_manager import AgentManager
from app.services.transcription import WhisperTranscriptionService
from app.services.tts import ElevenLabsTTS


@lru_cache(maxsize=1)
def get_transcription_service() -> WhisperTranscriptionService:
    """Factory function for transcription service"""
    return WhisperTranscriptionService(model_size="base")


@lru_cache(maxsize=1)
def get_agent_manager() -> AgentManager:
    """Factory function for agent manager"""
    return AgentManager()


@lru_cache(maxsize=1)
def get_tts_service() -> ElevenLabsTTS:
    """Factory function for TTS service"""
    return ElevenLabsTTS()
