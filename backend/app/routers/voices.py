import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.clients.tts import create_tts_provider
from app.clients.tts_base import VoicesResponse
from app.dependencies import get_current_user_world
from app.http import INTERNAL_SERVER_ERROR

router = APIRouter(prefix="/api/voices", tags=["voices"])

logger = logging.getLogger(__name__)

VOICE_SAMPLE_TEXT = "This is a character voice sample"


@router.get("/search", response_model=VoicesResponse)
async def search_voices(
    search_term: str = Query(..., description="Search term for voices"),
    next_page_token: str | None = Query(
        None, description="Pagination token for next page"
    ),
    tts_provider: str = Query(..., description="TTS provider"),
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Search for available voices"""
    user_id, world_id = user_world
    try:
        return await create_tts_provider(provider=tts_provider).search_voices(
            search_term=search_term, next_page_token=next_page_token
        )
    except Exception as e:
        logger.error(
            f"Failed to search voices for user {user_id}, world {world_id}, term '{search_term}'. {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)


@router.get("/{voice_id}/sample")
async def get_voice_sample(
    voice_id: str,
    tts_provider: str = Query(..., description="TTS provider"),
    user_world: tuple[int, int] = Depends(get_current_user_world),
):
    """Generate and stream a voice sample using static text"""
    user_id, world_id = user_world
    try:

        async def generate_sample():
            async for chunk in create_tts_provider(
                provider=tts_provider
            ).text_to_speech_stream(VOICE_SAMPLE_TEXT, voice_id):
                yield chunk

        return StreamingResponse(
            generate_sample(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=voice_sample_{voice_id}.mp3",
                "Cache-Control": "no-cache",
            },
        )
    except Exception as e:
        logger.error(
            f"Failed to generate voice sample {voice_id} for user {user_id}, world {world_id}. {e}"
        )
        raise HTTPException(status_code=500, detail=INTERNAL_SERVER_ERROR)
