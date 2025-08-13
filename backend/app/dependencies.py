from functools import lru_cache

from app.data.character_store import CharacterStore
from app.data.memory_store import MemoryStore
from app.data.player_store import PlayerStore
from app.data.reveal_store import RevealStore
from app.data.trust_store import TrustStateStore
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
def get_character_store() -> CharacterStore:
    """Factory function for character store"""
    return CharacterStore()


@lru_cache(maxsize=1)
def get_player_store() -> PlayerStore:
    """Factory function for player store"""
    return PlayerStore()


@lru_cache(maxsize=1)
def get_reveal_store() -> RevealStore:
    """Factory function for reveal store"""
    return RevealStore()


@lru_cache(maxsize=1)
def get_memory_store() -> MemoryStore:
    """Factory function for memory store"""
    return MemoryStore()


@lru_cache(maxsize=1)
def get_trust_state_store() -> TrustStateStore:
    """Factory function for trust state store"""
    return TrustStateStore()
