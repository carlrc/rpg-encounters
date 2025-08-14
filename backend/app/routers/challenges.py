import logging

from fastapi import APIRouter, WebSocket

from app.agents.challenge_agent import ChallengeAgent
from app.agents.critical_failure_agent import CriticalFailureAgent
from app.agents.critical_success_agent import CriticalSuccessAgent
from app.agents.prompts.import_prompts import import_system_prompt
from app.data.player_store import PlayerStore
from app.dependencies import (
    get_character_store,
    get_memory_store,
    get_reveal_store,
    get_transcription_service,
    get_tts_service,
)
from app.services.ability_challenge import (
    D20Outcomes,
    calculate_skill_check,
    filter_reveals_by_roll,
)
from app.services.audio_processor import cleanup_files, save_chunks_to_wav
from app.services.websocket import get_audio_chunks

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/challenge", tags=["challenges"])

challenge_agent_system_prompt = import_system_prompt("challenge_agent")
challenge_agent_critical_success_system_prompt = import_system_prompt(
    "challenge_agent_critical_success"
)
challenge_agent_critical_failure_system_prompt = import_system_prompt(
    "challenge_agent_critical_failure"
)


@router.websocket("/{player_id}/{character_id}")
async def websocket_endpoint(
    websocket: WebSocket, player_id: int, character_id: int, skill: str, d20_roll: int
):
    # TODO: We should be able to cancel on the frontend if the player made a mistake for instance before closing the connection
    audio_chunks = await get_audio_chunks(websocket=websocket)
    # TODO: saving to WAV needs to be made async
    wav_path = save_chunks_to_wav(audio_chunks)
    transcription = await get_transcription_service().transcribe_audio(wav_path)
    logger.info(f"Transcribed audio text: {transcription}")

    try:
        # Get player and character data
        character = get_character_store().get_character_by_id(character_id)
        player = PlayerStore().get_player_by_id(player_id=player_id)
        # Calculate skill check: d20 + player skill bonus
        total_roll = calculate_skill_check(
            skill=skill, player=player, d20_roll=d20_roll
        )

        # Get information tied to character
        all_reveals = get_reveal_store().get_by_character_id(character_id)
        filtered_reveals = filter_reveals_by_roll(all_reveals, total_roll)
        all_memories = get_memory_store().get_by_character_id(character_id)

        if d20_roll == D20Outcomes.CRITICAL_SUCCESS.value:
            agent = CriticalSuccessAgent(
                character=character,
                player=player,
                system_prompt=challenge_agent_critical_success_system_prompt,
                memories=all_memories,
                reveals=filtered_reveals,
            )
        elif d20_roll == D20Outcomes.CRITICAL_FAILURE.value:
            agent = CriticalFailureAgent(
                character=character,
                player=player,
                system_prompt=challenge_agent_critical_failure_system_prompt,
                memories=all_memories,
            )
        else:
            agent = ChallengeAgent(
                character=character,
                player=player,
                system_prompt=challenge_agent_system_prompt,
                memories=all_memories,
                reveals=filtered_reveals,
            )

        response = await agent.chat(player_transcript=transcription)
        logger.debug(
            f"Generated character response for D20 roll {d20_roll}: {response}"
        )
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
