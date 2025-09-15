import logging

from fastapi import WebSocket
from langfuse import get_client

from app.clients.tts import create_tts_provider
from app.data.moderation_store import ModerationStore
from app.models.moderation import ModerationCreate
from app.moderation.check import ModerationResponse, get_random_moderation_response
from app.services.websocket import stream_tts_audio

logger = logging.getLogger(__name__)


async def handle_moderation_response(
    websocket: WebSocket,
    user_id: int,
    text: str,
    response: ModerationResponse,
    tts_provider_name: str,
    voice_id: str,
) -> None:
    """
    Handle moderation response when content is blocked.

    Args:
        websocket: WebSocket connection to send audio to
        user_id: ID of the user whose content was blocked
        text: The flagged text content from the user
        response: The moderation response containing block details
        tts_provider_name: TTS provider to use for audio generation
        voice_id: Voice ID for TTS
    """
    # Save the flagged text to the moderation table for auditing
    try:
        record = await ModerationStore().create(
            moderation_data=ModerationCreate(
                user_id=user_id, text=text, openai_id=response.id
            )
        )
        logger.warning(f"Saved moderation record {record.id} for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to save moderation record for user {user_id}: {e}")
        raise e

    logger.info(f"User {user_id} msg violated TOS. Using default replies...")
    default_response = get_random_moderation_response()
    telem_client = get_client()
    telem_client.update_current_trace(input=f"MODERATED MESSAGE {record.id}")
    telem_client.update_current_trace(
        output=default_response,
        tags=["moderation"],
        metadata={
            "moderated_response_id": response.id,
            "moderated_response_model": response.model,
        },
    )
    await stream_tts_audio(
        websocket=websocket,
        tts_provider=create_tts_provider(provider=tts_provider_name),
        text=default_response,
        voice_id=voice_id,
    )
