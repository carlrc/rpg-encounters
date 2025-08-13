import logging

from fastapi import WebSocket, WebSocketDisconnect

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
