import logging
import os
from enum import Enum
from typing import AsyncGenerator

import httpx

from app.clients.tts_base import TTSProvider, VoicesResponse

logger = logging.getLogger(__name__)


class VoiceType(Enum):
    PERSONAL = "personal"
    COMMUNITY = "community"
    DEFAULT = "default"
    WORKSPACE = "workspace"
    NON_DEFAULT = "non-default"


class ElevenLabs(TTSProvider):
    def __init__(self, page_size: int = 15):
        super().__init__()
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
            logger.error(f"ElevenLabs HTTP {e.response.status_code} error: {e}")
            raise
        except httpx.ConnectTimeout as e:
            logger.error(
                f"ElevenLabs connection timeout: Failed to connect to {url}. Error: {e}"
            )
            raise
        except httpx.TimeoutException as e:
            logger.error(f"ElevenLabs request timeout: {e}")
            raise
        except Exception as e:
            logger.error(f"ElevenLabs TTS streaming failed: {type(e).__name__}: {e}")
            raise

    async def search_voices(
        self,
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
        params["voice_type"] = None
        params["next_page_token"] = next_page_token
        params["include_total_count"] = True

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()

                return VoicesResponse.model_validate(response.json())

        except httpx.HTTPStatusError as e:
            logger.error(f"ElevenLabs HTTP {e.response.status_code} error: {e}")
            raise
        except httpx.ConnectTimeout as e:
            logger.error(
                f"ElevenLabs connection timeout: Failed to connect to {url}. Error: {e}"
            )
            raise
        except httpx.TimeoutException as e:
            logger.error(f"ElevenLabs request timeout: {e}")
            raise
        except Exception as e:
            logger.error(f"ElevenLabs voice search failed: {e}")
            raise
