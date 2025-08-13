from fastapi import APIRouter, WebSocket
import logging
from app.services.audio_processor import cleanup_files, save_chunks_to_wav
from app.agents.prompts.import_prompts import import_system_prompt
from app.services.trust_calculator import calculate_base_trust
from app.services.websocket import get_audio_chunks
from app.dependencies import (
    get_agent_manager,
    get_transcription_service,
    get_tts_service,
    get_memory_store,
    get_character_store,
    get_player_store,
    get_reveal_store,
    get_trust_state_store,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversation", tags=["conversations"])

char_system_prompt = import_system_prompt("conversation_agent")
scoring_system_prompt = import_system_prompt("trust_scoring_agent")


@router.websocket("/{player_id}/{character_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: int, character_id: int):

    # TODO: We should be able to cancel on the frontend if the player made a mistake for instance before closing the connection
    audio_chunks = await get_audio_chunks(websocket=websocket)
    # TODO: saving to WAV needs to be made async
    wav_path = save_chunks_to_wav(audio_chunks)
    transcription = await get_transcription_service().transcribe_audio(wav_path)
    logger.info(f"Transcribed audio text: {transcription}")

    try:
        # Get character and player information
        character = get_character_store().get_character_by_id(character_id)
        player = get_player_store().get_player_by_id(player_id)

        # Get static trust metric between character and player
        base_trust = calculate_base_trust(character, player)
        # Get or create persistent trust state
        trust_state = get_trust_state_store().get_or_create(
            character_id, player_id, base_trust
        )
        # Get information tied to character
        all_reveals = get_reveal_store().get_by_character_id(character_id)
        # TODO: This would need to be lazy updated across instances in case DM wants to update information on the fly
        all_memories = get_memory_store().get_by_character_id(character_id)

        # Get or create persistent character agent
        agent = get_agent_manager().get_or_create_agent(
            player_id=player_id,
            character_id=character_id,
            character=character,
            player=player,
            char_system_prompt=char_system_prompt,
            scoring_system_prompt=scoring_system_prompt,
            memories=all_memories,
            trust_state=trust_state,
        )

        # Generate AI response using character agent
        response, level, _ = await agent.chat(
            player_transcript=transcription, reveals=all_reveals
        )
        logger.debug(
            f"Generated character response for level ${level.name}: {response}"
        )

        # TODO: Persist the trust adjustments as a background task here for restart continuity

        # Stream TTS audio chunks back to frontend
        for audio_chunk in get_tts_service().text_to_speech_stream(
            response, character.voice
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
    except Exception as e:
        logger.error(f"Processing conversation failed: {e}")

    finally:
        try:
            # TODO: This crashes if no transcription was recorded and its an empty file
            # Clean up temporary files
            cleanup_files(wav_path)
        except Exception as e:
            logger.warning(f"Could not destroy temp wav_path {wav_path}. {e}")

    # WebSocket will be closed automatically by FastAPI
    logger.debug("Closing websocket connection...")
