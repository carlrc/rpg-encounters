import asyncio
import logging
import os
import subprocess
import tempfile
from typing import List

from langfuse import observe as langfuse_observe

logger = logging.getLogger(__name__)


@langfuse_observe
async def save_chunks_to_wav(chunks: List[bytes]) -> str:
    """Save audio chunks directly to WAV file using ffmpeg"""
    # Useful to use tempfile even though we are manually cleaning up after due to auto naming
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav_path = f.name

    cmd = [
        "ffmpeg",
        "-f",
        "webm",  # Input format (WebM from MediaRecorder)
        "-i",
        "pipe:0",  # Read from stdin
        "-ar",
        "16000",  # 16kHz sample rate (optimal for Whisper)
        "-ac",
        "1",  # Mono channel
        "-c:a",
        "pcm_s16le",  # PCM 16-bit encoding
        "-y",  # Overwrite output file
        wav_path,
    ]

    try:
        # Combine all chunks into a single bytes object
        audio_data = b"".join(chunks)

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate(input=audio_data)

        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, cmd, output=stdout, stderr=stderr
            )

        return wav_path
    except Exception as e:
        logger.error(f"FFmpeg WAV conversion failed: {e}")
        raise


@langfuse_observe
def cleanup_files(*file_paths: str) -> None:
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.unlink(path)
                logger.debug(f"Cleaned up temporary file: {path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup file {path}: {e}")
                raise
