import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.auth.session import UserSession
from app.clients.tts import ELEVANLABS_TTS, GOOGLE_TTS, create_tts_provider
from app.clients.tts_base import VoicesResponse
from app.data.account_store import get_user_elevenlabs_token
from app.dependencies import validate_current_user_world
from app.http import INTERNAL_SERVER_ERROR

router = APIRouter(prefix="/api/voices", tags=["voices"])

logger = logging.getLogger(__name__)

VOICE_SAMPLE_TEXT = "This is a character voice sample"


@router.get("/tts_providers", response_model=List[str])
async def get_tts_providers(
    session: UserSession = Depends(validate_current_user_world),
):
    """Get available TTS providers for the current user"""
    user_id, _ = session.user_id, session.world_id

    try:
        providers = [GOOGLE_TTS]

        if await get_user_elevenlabs_token(user_id=user_id):
            providers.append(ELEVANLABS_TTS)

        return providers
    except Exception as e:
        logger.error(f"Failed to get TTS providers for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )


@router.get("/search", response_model=VoicesResponse)
async def search_voices(
    search_term: str = Query(..., description="Search term for voices"),
    next_page_token: str | None = Query(
        None, description="Pagination token for next page"
    ),
    tts_provider: str = Query(..., description="TTS provider"),
    session: UserSession = Depends(validate_current_user_world),
):
    """Search for available voices"""
    user_id, _ = session.user_id, session.world_id

    try:
        elevanlabs_token = await get_user_elevenlabs_token(user_id=user_id)
        tts_client = create_tts_provider(
            provider=tts_provider, elevenlabs_user_api_key=elevanlabs_token
        )

        return await tts_client.search_voices(
            search_term=search_term, next_page_token=next_page_token
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to search voices for user {user_id} and term '{search_term}'. {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )


@router.get("/{voice_id}/sample")
async def get_voice_sample(
    voice_id: str,
    tts_provider: str = Query(..., description="TTS provider"),
    session: UserSession = Depends(validate_current_user_world),
):
    """Generate and stream a voice sample using static text"""
    user_id, _ = session.user_id, session.world_id

    try:
        elevanlabs_token = await get_user_elevenlabs_token(user_id)
        tts_client = create_tts_provider(
            provider=tts_provider, elevenlabs_user_api_key=elevanlabs_token
        )

        async def generate_sample():
            async for chunk in tts_client.text_to_speech_stream(
                VOICE_SAMPLE_TEXT, voice_id
            ):
                yield chunk

        return StreamingResponse(
            generate_sample(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=voice_sample_{voice_id}.mp3",
                "Cache-Control": "no-cache",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to generate voice sample {voice_id} for user {user_id}. {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=INTERNAL_SERVER_ERROR,
        )
