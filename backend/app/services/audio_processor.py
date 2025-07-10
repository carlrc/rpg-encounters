import subprocess
import tempfile
import os
import logging
from typing import List

logger = logging.getLogger(__name__)

class AudioProcessor:
    @staticmethod
    def save_chunks_to_wav(chunks: List[bytes]) -> str:
        """Save audio chunks directly to WAV file using ffmpeg"""
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            wav_path = f.name
        
        cmd = [
            'ffmpeg',
            '-f', 'webm',    # Input format (WebM from MediaRecorder)
            '-i', 'pipe:0',  # Read from stdin
            '-ar', '16000',  # 16kHz sample rate (optimal for Whisper)
            '-ac', '1',      # Mono channel
            '-c:a', 'pcm_s16le',  # PCM 16-bit encoding
            '-y',            # Overwrite output file
            wav_path
        ]
        
        logger.info(f"Converting {len(chunks)} audio chunks directly to WAV: {wav_path}")
        
        try:
            # Combine all chunks into a single bytes object
            audio_data = b''.join(chunks)
            
            # Run ffmpeg with audio data piped to stdin
            subprocess.run(
                cmd, 
                input=audio_data,
                check=True, 
                capture_output=True
            )
            
            logger.info(f"Direct WAV conversion successful: {wav_path}")
            return wav_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg direct conversion failed: {e.stderr}")
            raise
    
    @staticmethod
    def cleanup_files(*file_paths: str) -> None:
        """Clean up temporary files"""
        for path in file_paths:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                    logger.info(f"Cleaned up temporary file: {path}")
                except OSError as e:
                    logger.warning(f"Failed to cleanup file {path}: {e}")
