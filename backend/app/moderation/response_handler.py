import logging

from fastapi import WebSocket
from langfuse import get_client

from app.clients.tts import create_tts_provider
from app.data.moderation_store import ModerationStore
from app.models.moderation import ModerationCreate
from app.moderation.check import ModerationResponse, get_random_moderation_response
from app.services.context import ConvoContext
from app.services.websocket import stream_tts_audio

logger = logging.getLogger(__name__)


async def handle_moderation_response(
    websocket: WebSocket,
    user_id: int,
    text: str,
    ctx: ConvoContext,
    response: ModerationResponse,
) -> None:
    """Handle moderation response when content is blocked."""

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

    default_response = get_random_moderation_response()
    telem_client = get_client()

    # Do not log the moderated message in case it would break TOS of third party services
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
        tts_provider=create_tts_provider(
            provider=ctx.tts_provider_name, elevenlabs_user_api_key=ctx.elevenlabs_token
        ),
        text=default_response,
        voice_id=ctx.character.voice_id,
    )
