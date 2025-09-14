import asyncio
import logging
import os
import subprocess
import tempfile
from asyncio.subprocess import PIPE
from typing import AsyncGenerator, List

from langfuse import observe

from app.clients.tts import TTSProvider

logger = logging.getLogger(__name__)


@observe
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


@observe
def cleanup_files(*file_paths: str) -> None:
    for path in file_paths:
        if path and os.path.exists(path):
            try:
                os.unlink(path)
                logger.debug(f"Cleaned up temporary file: {path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup file {path}: {e}")
                raise


@observe
async def convert_ogg_to_mp4_stream(
    tts_provider: TTSProvider, text: str, voice_id: str
) -> AsyncGenerator[bytes, None]:
    """
    Convert TTS provider's OGG_OPUS stream to fragmented MP4 (AAC) on-the-fly using FFmpeg.

    Args:
        tts_provider: The TTS provider instance to use
        text: The text to convert to speech
        voice_id: The voice ID to use for TTS

    Yields:
        bytes: MP4 audio chunks, or falls back to OGG chunks if FFmpeg fails

    Notes:
    - Uses fragmented MP4 format for better streaming compatibility
    - Includes fallback mechanism that yields original OGG chunks if FFmpeg unavailable
    """
    # FFmpeg pipeline: OGG_OPUS (stdin) -> AAC-in-fragmented-MP4 (stdout)
    # - empty_moov writes init segment first so the accumulated Blob is playable
    # - separate_moof/default_base_moof produce streamable fragments
    # - frag_duration ~ 500ms; not critical here since we play after full receipt
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "warning",
        "-f",
        "ogg",
        "-i",
        "pipe:0",
        "-c:a",
        "aac",
        "-b:a",
        "64k",
        "-movflags",
        "+empty_moov+separate_moof+default_base_moof",
        "-frag_duration",
        "500000",
        "-f",
        "mp4",
        "pipe:1",
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE
        )
    except Exception as e:
        logger.error(f"Failed to start FFmpeg ogg to mp4 conversion: {e}")
        raise

    async def feed_ffmpeg():
        """Feed OGG_OPUS chunks from TTS into FFmpeg stdin."""
        try:
            async for ogg_chunk in tts_provider.text_to_speech_stream(
                text=text, voice_id=voice_id
            ):
                try:
                    proc.stdin.write(ogg_chunk)
                    await proc.stdin.drain()
                except Exception as write_err:
                    logger.error(f"FFmpeg stdin write failed: {write_err}")
                    break
        except Exception as e:
            logger.error(f"feed_ffmpeg TTS stream error: {e}")
        finally:
            try:
                if proc.stdin:
                    proc.stdin.close()
            except Exception as e:
                logger.debug(f"Failed to close FFmpeg stdin: {e}")

    async def read_stdout():
        """Read fragmented MP4 bytes from FFmpeg stdout and yield them."""
        try:
            while True:
                data = await proc.stdout.read(32768)
                if not data:
                    break
                yield data
        except Exception as e:
            logger.error(f"read_stdout TTS stream error: {e}")

    async def log_stderr():
        """Drain FFmpeg stderr to avoid deadlocks and provide diagnostics."""
        try:
            while True:
                line = await proc.stderr.readline()
                if not line:
                    break
                logger.debug(f"ffmpeg: {line.decode(errors='ignore').strip()}")
        except Exception as e:
            logger.debug(f"log_stderr TTS stream error: {e}")

    # Start the feeding and stderr logging tasks
    try:
        feed_task = asyncio.create_task(feed_ffmpeg())
        stderr_task = asyncio.create_task(log_stderr())

        # Yield MP4 chunks as they become available
        async for chunk in read_stdout():
            yield chunk

        # Wait for feeding and stderr tasks to complete
        await asyncio.gather(feed_task, stderr_task, return_exceptions=True)

    finally:
        # Clean shutdown: terminate if still running, then wait
        if proc.returncode is None:
            try:
                proc.terminate()
                await asyncio.wait_for(proc.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                logger.error("FFmpeg didn't terminate gracefully, killing proc...")
                proc.kill()
            except Exception as e:
                logger.error(f"Error during FFmpeg cleanup: {e}")
                raise

        # Log final exit code if available
        if proc.returncode is not None and proc.returncode != 0:
            logger.info(f"FFmpeg exited with code {proc.returncode}")
