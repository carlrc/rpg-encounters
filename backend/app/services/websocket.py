import logging

from fastapi import WebSocket, WebSocketDisconnect

from app.clients.tts import TTSProvider
from app.services.audio_processor import convert_ogg_to_mp4_stream

logger = logging.getLogger(__name__)


async def get_audio_chunks(websocket: WebSocket):
    await websocket.accept()
    logger.debug("WebSocket connection established...")

    # Buffer for audio chunks during recording
    audio_chunks = []

    try:
        while True:
            # Receive message (can be text or binary)
            message = await websocket.receive()

            if "bytes" in message:
                # Binary audio data
                audio_data = message["bytes"]
                audio_chunks.append(audio_data)

            elif "text" in message:
                # Text control signal
                if message["text"] == "END":
                    logger.debug("Received END signal, processing accumulated audio...")
                    break
                else:
                    logger.warning(
                        f"Received unexpected socket message: {message['text']}"
                    )

    except WebSocketDisconnect:
        logger.error("Audio receive websocket closed by client.")
        raise

    except Exception as e:
        logger.error(f"Audio receive websocket error: {e}")
        raise

    return audio_chunks


async def stream_tts_audio(
    websocket: WebSocket, tts_provider: TTSProvider, text: str, voice_id: str
) -> None:
    """
    Stream TTS audio by converting OGG_OPUS to MP4 using audio processor service.

    Args:
        websocket: The WebSocket connection to send audio through
        tts_provider: The TTS provider instance to use
        text: The text to convert to speech
        voice_id: The voice ID to use for TTS
    """
    # Use audio processor to convert OGG to MP4 and stream chunks
    async for audio_chunk in convert_ogg_to_mp4_stream(
        tts_provider=tts_provider, text=text, voice_id=voice_id
    ):
        try:
            await websocket.send_bytes(audio_chunk)
        except Exception as e:
            logger.error(f"Failed to send audio chunk: {e}")
            break

    # Send completion signal
    try:
        await websocket.send_text("AUDIO_COMPLETE")
    except Exception as e:
        logger.error(f"Failed to send completion signal: {e}")
