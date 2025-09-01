import logging
import os
from enum import Enum
from typing import AsyncGenerator, List

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class VoiceType(Enum):
    PERSONAL = "personal"
    COMMUNITY = "community"
    DEFAULT = "default"
    WORKSPACE = "workspace"
    NON_DEFAULT = "non-default"


class VoiceLabels(BaseModel):
    """Voice labels for additional metadata"""

    gender: str | None = Field(None, description="Voice gender")
    accent: str | None = Field(None, description="Voice accent")
    descriptive: str | None = Field(None, description="Descriptive label")
    age: str | None = Field(None, description="Voice age")
    language: str | None = Field(None, description="Voice language")


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


class ElevenLabs:
    def __init__(self, page_size: int = 15):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io"
        self.output_format = "mp3_44100_128"
        self.model = "eleven_flash_v2_5"
        self.page_size = page_size

    async def text_to_speech_stream(
        self, text: str, voice_id: str
    ) -> AsyncGenerator[bytes, None]:
        """Stream text-to-speech audio chunks"""

        url = f"{self.base_url}/v1/text-to-speech/{voice_id}/stream"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        params = {"output_format": self.output_format}
        payload = {"text": text, "model_id": self.model}

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST", url, headers=headers, params=params, json=payload
                ) as response:
                    response.raise_for_status()

                    async for chunk in response.aiter_bytes():
                        if chunk:
                            yield chunk

        except httpx.HTTPStatusError as e:
            logger.error(f"Elevant Labs {e.response.status_code} error. {e}")
            raise
        except Exception as e:
            logger.error(f"TTS streaming failed: {e}")
            raise

    async def search_voices(
        self,
        voice_type: VoiceType | None = None,
        search_term: str | None = None,
        next_page_token: str = None,
    ) -> VoicesResponse:
        """Search for available voices"""

        url = f"{self.base_url}/v2/voices"
        headers = {
            "xi-api-key": self.api_key,
        }

        # Build query parameters
        params = {}
        params["page_size"] = self.page_size
        params["search"] = search_term
        params["voice_type"] = voice_type.value if voice_type else voice_type
        params["next_page_token"] = next_page_token
        params["include_total_count"] = True

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()

                return VoicesResponse.model_validate(response.json())

        except httpx.HTTPStatusError as e:
            logger.error(f"Elevant Labs {e.response.status_code} error. {e}")
            raise
        except Exception as e:
            logger.error(f"Voice search failed: {e}")
            raise
