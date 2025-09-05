import logging

from fastapi import WebSocket
from langfuse import get_client

from app.clients.tts import create_tts_provider
from app.moderation.check import ModerationResponse, get_random_moderation_response
from app.services.websocket import stream_tts_audio

logger = logging.getLogger(__name__)


async def handle_moderation_response(
    websocket: WebSocket,
    user_id: int,
    response: ModerationResponse,
    tts_provider_name: str,
    voice_id: str,
) -> None:
    """
    Handle moderation response when content is blocked.

    Args:
        websocket: WebSocket connection to send audio to
        user_id: ID of the user whose content was blocked
        response: The moderation response containing block details
        tts_provider_name: TTS provider to use for audio generation
        voice_id: Voice ID for TTS
    """
    # TODO: Save the text the user said to a table with their violations for auditing down the road
    logger.error(f"User {user_id} msg violated TOS. Using default replies...")
    get_client().update_current_trace(
        tags=["moderation"],
        metadata={"mod_response_id": response.id, "mod_response_model": response.model},
    )
    await stream_tts_audio(
        websocket=websocket,
        tts_provider=create_tts_provider(provider=tts_provider_name),
        text=get_random_moderation_response(),
        voice_id=voice_id,
    )
