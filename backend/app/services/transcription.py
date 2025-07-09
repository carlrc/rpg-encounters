import whisper
import os
import logging
from typing import Optional
import asyncio
import functools

logger = logging.getLogger(__name__)

class WhisperTranscriptionService:
    def __init__(self, model_size: str = "base"):
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
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info(f"Whisper model {self.model_size} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model {self.model_size}: {e}")
            raise
    
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
            logger.info(f"Transcribing audio file: {wav_file_path}")
            
            # Run transcription in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                functools.partial(self.model.transcribe, wav_file_path)
            )
            
            transcription = result["text"].strip()
            logger.info(f"Transcription completed: '{transcription[:50]}...'")
            
            return transcription
            
        except Exception as e:
            logger.error(f"Transcription failed for {wav_file_path}: {e}")
            raise
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        return {
            "model_size": self.model_size,
            "is_loaded": self.model is not None
        }
