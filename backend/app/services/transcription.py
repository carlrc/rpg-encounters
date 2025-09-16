import asyncio
import functools
import logging
import os
import random

import torch
import whisper
from langfuse import observe

from app.clients.openai_moderation import ModerationResponse
from app.moderation.check import moderation_pipe
from app.utils import get_or_throw

logger = logging.getLogger(__name__)


@observe
async def transcribe_and_moderate(
    user_id: int, wav_file_path: str
) -> tuple[str, ModerationResponse | None]:
    transcription = await get_transcription_service().transcribe_audio(
        wav_file_path=wav_file_path
    )
    is_blocked = await moderation_pipe(user_id=user_id, text=transcription)

    return transcription, is_blocked


class WhisperTranscriptionService:
    def __init__(self, model_size: str = "tiny.en"):
        """Initialize Whisper transcription service

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the Whisper model"""
        try:
            device = self._get_device()
            logger.info(f"Loading Whisper model: {self.model_size} with {device}")
            self.model = whisper.load_model(
                name=self.model_size, device=device, in_memory=True
            )
        except Exception as e:
            logger.error(f"Failed to load Whisper model {self.model_size}: {e}")
            raise

    def _get_device(self) -> str:
        # TODO: Support MPS on mac
        try:
            if torch.cuda.is_available():
                return "cuda"
            else:
                return "cpu"
        except Exception as e:
            logger.error(f"Failed to determine device. {e}")
            raise

    @observe(capture_input=False, capture_output=False)
    async def transcribe_audio(self, wav_file_path: str) -> str:
        """Transcribe WAV file using Whisper

        Args:
            wav_file_path: Path to WAV audio file

        Returns:
            Transcribed text
        """
        if not os.path.exists(wav_file_path):
            raise FileNotFoundError(f"Audio file not found: {wav_file_path}")

        try:
            # Run transcription in thread pool to avoid blocking
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                functools.partial(
                    self.model.transcribe,
                    audio=wav_file_path,
                    fp16=False,
                    temperature=0.0,
                    beam_size=None,
                ),
            )

            transcription = result["text"].strip()

            return transcription

        except Exception as e:
            logger.error(f"Transcription failed for {wav_file_path}: {e}")
            raise


@functools.lru_cache(maxsize=1)
def _get_transcription_pool() -> list[WhisperTranscriptionService]:
    """Create pool of transcription services"""
    pool_size = int(get_or_throw("TRANSCRIPTION_POOL_SIZE"))
    return [WhisperTranscriptionService() for _ in range(pool_size)]


def get_transcription_service() -> WhisperTranscriptionService:
    """Factory function for transcription service - returns random instance from pool"""
    return random.choice(_get_transcription_pool())
