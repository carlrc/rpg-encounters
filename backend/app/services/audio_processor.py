import subprocess
import tempfile
import os
import logging
from typing import List

logger = logging.getLogger(__name__)

class AudioProcessor:
    @staticmethod
    def save_webm_chunks(chunks: List[bytes]) -> str:
        """Save audio chunks to temporary WebM file"""
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
            for chunk in chunks:
                f.write(chunk)
            logger.info(f"Saved {len(chunks)} audio chunks to {f.name}")
            return f.name
    
    @staticmethod
    def convert_webm_to_wav(webm_path: str) -> str:
        """Convert WebM to WAV using system ffmpeg"""
        wav_path = webm_path.replace('.webm', '.wav')
        
        cmd = [
            'ffmpeg', '-i', webm_path,
            '-ar', '16000',  # 16kHz sample rate (optimal for Whisper)
            '-ac', '1',      # Mono channel
            '-c:a', 'pcm_s16le',  # PCM 16-bit encoding
            '-y',            # Overwrite output file
            wav_path
        ]
        
        logger.info(f"Converting {webm_path} to {wav_path}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"FFmpeg conversion successful: {wav_path}")
            return wav_path
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg conversion failed: {e.stderr}")
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
