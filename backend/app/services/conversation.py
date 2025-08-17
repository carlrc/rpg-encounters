import logging

from fastapi import WebSocket

from app.agents.conversation_agent import ConversationAgentDeps
from app.agents.prompts.import_prompts import import_system_prompt
from app.data.character_store import CharacterStore
from app.data.encounter_store import EncounterStore
from app.data.influence_store import InfluenceStore
from app.data.memory_store import MemoryStore
from app.data.player_store import PlayerStore
from app.data.reveal_store import RevealStore
from app.dependencies import (
    get_agent_manager,
    get_transcription_service,
    get_tts_service,
)
from app.services.audio_processor import cleanup_files, save_chunks_to_wav
from app.services.influence_calculator import calculate_base_influence
from app.services.websocket import get_audio_chunks

logger = logging.getLogger(__name__)

char_system_prompt = import_system_prompt("conversation_agent")
scoring_system_prompt = import_system_prompt("influence_scoring_agent")


async def have_conversation(
    websocket: WebSocket, player_id: int, character_id: int, encounter_id: int
) -> None:

    # TODO: We should be able to cancel on the frontend if the player made a mistake for instance before closing the connection
    audio_chunks = await get_audio_chunks(websocket=websocket)
    # TODO: saving to WAV needs to be made async
    wav_path = save_chunks_to_wav(chunks=audio_chunks)
    transcription = await get_transcription_service().transcribe_audio(
        wav_file_path=wav_path
    )
    logger.info(f"Transcribed audio text: {transcription}")

    try:
        # Get character and player information
        encounter = EncounterStore().get_encounter_by_id(encounter_id=encounter_id)
        character = CharacterStore().get_character_by_id(character_id=character_id)
        player = PlayerStore().get_player_by_id(player_id=player_id)

        # Get static influence metric between character and player
        base_influence = calculate_base_influence(character=character, player=player)
        # Get or create persistent influence state
        influence = InfluenceStore().get_or_create(
            character_id=character_id, player_id=player_id, base=base_influence
        )
        # Get information tied to character
        all_reveals = RevealStore().get_by_character_id(character_id=character_id)
        # TODO: This would need to be lazy updated across instances in case DM wants to update information on the fly
        all_memories = MemoryStore().get_by_character_id(character_id=character_id)

        # Get or create persistent character agent
        agent = get_agent_manager().get_or_create_agent(
            player_id=player_id,
            character_id=character_id,
            character=character,
            player=player,
            char_system_prompt=char_system_prompt,
            scoring_system_prompt=scoring_system_prompt,
            memories=all_memories,
            influence=influence,
        )

        # Generate AI response using character agent
        deps = ConversationAgentDeps(
            reveals=all_reveals, encounter_description=encounter.description
        )
        response, level, _ = await agent.chat(
            player_transcript=transcription, deps=deps
        )
        logger.debug(
            f"Generated character response for level ${level.name}: {response}"
        )

        # TODO: Persist the influence adjustments as a background task here for restart continuity

        # Stream TTS audio chunks back to frontend
        for audio_chunk in get_tts_service().text_to_speech_stream(
            text=response, voice_id=character.voice
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
