import os
import logging
from typing import Generator
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

# Load environment variables from .env file

logger = logging.getLogger(__name__)


class ElevenLabsTTS:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.client = ElevenLabs(api_key=self.api_key)

    def text_to_speech_stream(
        self, text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb"
    ) -> Generator[bytes, None, None]:
        """
        Stream text-to-speech audio chunks

        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID to use for TTS

        Yields:
            bytes: Audio chunks as they are generated
        """
        try:
            audio_stream = self.client.text_to_speech.stream(
                text=text, voice_id=voice_id, model_id="eleven_flash_v2_5"
            )

            for chunk in audio_stream:
                if isinstance(chunk, bytes):
                    yield chunk

        except Exception as e:
            logger.error(f"TTS streaming failed: {e}")
            raise
