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

    def text_to_speech_stream(self, text: str) -> Generator[bytes, None, None]:
        """
        Stream text-to-speech audio chunks
        
        Args:
            text: Text to convert to speech
            
        Yields:
            bytes: Audio chunks as they are generated
        """
        try:
            audio_stream = self.client.text_to_speech.stream(
                text=text,
                voice_id="JBFqnCBsd6RMkjVDRZzb",
                model_id="eleven_flash_v2_5"
            )
            
            for chunk in audio_stream:
                if isinstance(chunk, bytes):
                    logger.debug("Yielded another chunk...")
                    yield chunk
                                
        except Exception as e:
            logger.error(f"TTS streaming failed: {e}")
            raise
