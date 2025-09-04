from abc import ABC, abstractmethod
from typing import AsyncGenerator, List

from pydantic import BaseModel, Field


class VoiceLabels(BaseModel):
    """Voice labels for additional metadata"""

    gender: str | None = Field(None, description="Voice gender")
    accent: str | None = Field(None, description="Voice accent")
    descriptive: str | None = Field(None, description="Descriptive label")
    age: str | None = Field(None, description="Voice age")
    language: str | None = Field(None, description="Voice language")
    use_case: str | None = Field(None, description="Voice use case")


class Voice(BaseModel):
    """Simplified voice model for frontend display"""

    voice_id: str = Field(..., description="Voice ID")
    name: str = Field(..., description="Voice name")
    description: str | None = Field(..., description="Voice description")
    category: str = Field(..., description="Voice category")
    labels: VoiceLabels | None = Field(None, description="Voice labels")


class VoicesResponse(BaseModel):
    """Response model for voices search with pagination"""

    voices: List[Voice] | None = Field(..., description="List of available voices")
    has_more: bool = Field(..., description="Whether there are more voices available")
    next_page_token: str | None = Field(None, description="Token for next page")
    total_count: int = Field(None, description="Total available voices")


class TTSProvider(ABC):
    """Abstract base class for TTS providers with unified interface"""

    @abstractmethod
    async def text_to_speech_stream(
        self, text: str, voice_id: str
    ) -> AsyncGenerator[bytes, None]:
        """Stream text-to-speech audio chunks"""
        pass

    @abstractmethod
    async def search_voices(
        self,
        search_term: str | None = None,
        next_page_token: str | None = None,
    ) -> VoicesResponse:
        """Unified search interface for all TTS providers"""
        pass
