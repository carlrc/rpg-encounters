import logging
from fastapi import APIRouter, WebSocket
from app.services.websocket import get_audio_chunks
from app.dependencies import get_transcription_service
from app.services.audio_processor import cleanup_files, save_chunks_to_wav
from app.data import character_store, player_store, reveal_store, memory_store
from app.agents.challenge_agent import ChallengeAgent
from app.agents.prompts.import_prompts import import_system_prompt
from app.services.ability_challenge import (
    calculate_skill_check,
    filter_reveals_by_roll,
)
from backend.app.services.conversation_manager import ConversationManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/challenge", tags=["challenges"])

challenge_system_prompt = import_system_prompt("challenge_agent")


@router.websocket("/{player_id}/{character_id}")
async def websocket_endpoint(
    websocket: WebSocket, player_id: int, character_id: int, skill: str
):
    # TODO: We should be able to cancel on the frontend if the player made a mistake for instance before closing the connection
    audio_chunks = await get_audio_chunks(websocket=websocket)
    # TODO: saving to WAV needs to be made async
    wav_path = save_chunks_to_wav(audio_chunks)
    transcription = await get_transcription_service().transcribe_audio(wav_path)
    logger.info(f"Transcribed audio text: {transcription}")

    try:
        # Get player and character data
        character = character_store.get_character_by_id(character_id)
        player = player_store.get_player_by_id(player_id)
        # Calculate skill check: d20 + player skill bonus
        d20_roll, skill_bonus, total_roll = calculate_skill_check(skill, player)

        # Get information tied to character
        all_reveals = reveal_store.get_by_character_id(character_id)
        # TODO: This would need to be lazy updated across instances in case DM wants to update information on the fly
        all_memories = memory_store.get_by_character_id(character_id)

        filtered_reveals = filter_reveals_by_roll(all_reveals, total_roll)

        agent = ChallengeAgent(
            character=character,
            player=player,
            system_prompt=challenge_system_prompt,
            memories=all_memories,
            conversation_manager=ConversationManager(),
        )
        agent.chat(player_transcript=transcription, reveals=filtered_reveals)

        # TODO: Pass all memories and filtered reveals to agent
        # TODO: Need to incorporate sentiment based on the success or failure of this

    except Exception as e:
        logger.error(f"Processing challenge failed: {e}")
    finally:
        try:
            # TODO: This crashes if no transcription was recorded and its an empty file
            # Clean up temporary files
            cleanup_files(wav_path)
        except Exception as e:
            logger.warning(f"Could not destroy temp wav_path {wav_path}. {e}")

    # WebSocket will be closed automatically by FastAPI
    logger.debug("Closing websocket connection...")
