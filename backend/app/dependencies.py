from functools import lru_cache

from app.data.connection_store import ConnectionStore
from app.data.encounter_store import EncounterStore
from app.data.influence_store import InfluenceStore
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


@lru_cache(maxsize=1)
def get_influence_store() -> InfluenceStore:
    """Factory function for influence store"""
    return InfluenceStore()


@lru_cache(maxsize=1)
def get_encounter_store() -> EncounterStore:
    """Factory function for encounter store"""
    return EncounterStore()


@lru_cache(maxsize=1)
def get_connection_store() -> ConnectionStore:
    """Factory function for connection store"""
    return ConnectionStore()
