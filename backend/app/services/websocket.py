import logging

from fastapi import WebSocket, WebSocketDisconnect

from app.clients.tts import TtsGenerationError, TTSProvider

logger = logging.getLogger(__name__)


WARNING_MESSAGE_TRANSCRIPTION_FAILED = "Transcription failed. Please try again..."
WARNING_MESSAGE_LLM_FAILED = "LLM response generation failed. Please try again..."
WARNING_MESSAGE_TTS_FAILED = "Generating audio failed. Please try again..."
WARNING_MESSAGE_PROCESSING_FAILED = "Could not process request. Please try again..."


async def safe_close(websocket: WebSocket, code=1000, reason="end_of_stream") -> None:
    try:
        await websocket.close(code=code, reason=reason)
    except Exception as e:
        logger.error(f"Failed to send websocket close signal: {e}")


async def send_audio_complete(websocket: WebSocket) -> None:
    try:
        await websocket.send_text("AUDIO_COMPLETE")
    except Exception as e:
        logger.error(f"Failed to send websocket completion signal: {e}")


async def send_warning(websocket: WebSocket, message: str) -> None:
    try:
        await websocket.send_json(
            {
                "type": "warning",
                "message": message,
            }
        )
    except Exception as e:
        logger.error(f"Failed to send warning payload: {e}")


async def send_warning_and_close(websocket: WebSocket, message: str, code=1011) -> None:
    await send_warning(websocket=websocket, message=message)
    await send_audio_complete(websocket=websocket)
    await safe_close(websocket=websocket, code=code)


async def get_audio_chunks(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established...")

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
                    logger.info("Received END signal, starting audio processing")
                    logger.info("Received END signal, processing accumulated audio...")
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
    Stream TTS audio in MP4 format directly from TTS provider.

    Args:
        websocket: The WebSocket connection to send audio through
        tts_provider: The TTS provider instance to use
        text: The text to convert to speech
        voice_id: The voice ID to use for TTS
    """
    # Use TTS provider's MP4 stream method
    try:
        async for audio_chunk in tts_provider.text_to_speech_mp4_stream(
            text=text, voice_id=voice_id
        ):
            try:
                await websocket.send_bytes(audio_chunk)
            except Exception as e:
                logger.error(f"Failed to send audio chunk: {e}")
                break
    except Exception as e:
        logger.error(f"TTS streaming failed: {e}")
        raise TtsGenerationError("TTS generation failed") from e

    # Send completion signal
    await send_audio_complete(websocket=websocket)
    await safe_close(websocket=websocket)
