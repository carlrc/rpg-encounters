import logging

from fastapi import WebSocket
from langfuse import get_client
from sqlalchemy.orm import sessionmaker

from app.agents.challenge_agent import ChallengeAgent, ChallengeAgentDeps
from app.agents.prompts.import_prompts import render_jinja_prompt
from app.data.character_store import CharacterStore
from app.data.encounter_store import EncounterStore
from app.data.memory_store import MemoryStore
from app.data.player_store import PlayerStore
from app.data.reveal_store import RevealStore
from app.db.connection import get_db_engine
from app.dependencies import (
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


async def challenge_character(
    websocket: WebSocket,
    world_id: int,
    user_id: int,
    encounter_id: int,
    player_id: int,
    character_id: int,
    skill: str,
    d20_roll: int,
):
    # TODO: We should be able to cancel on the frontend if the player made a mistake for instance before closing the connection
    audio_chunks = await get_audio_chunks(websocket=websocket)
    # TODO: saving to WAV needs to be made async
    wav_path = save_chunks_to_wav(audio_chunks)
    transcription = await get_transcription_service().transcribe_audio(wav_path)
    logger.info(f"Transcribed audio text: {transcription}")

    try:
        Session = sessionmaker(get_db_engine())
        with Session() as session:
            # Create store instances with shared session
            character_store = CharacterStore(
                user_id=user_id, world_id=world_id, session=session
            )
            player_store = PlayerStore(
                user_id=user_id, world_id=world_id, session=session
            )
            encounter_store = EncounterStore(
                user_id=user_id, world_id=world_id, session=session
            )
            reveal_store = RevealStore(
                user_id=user_id, world_id=world_id, session=session
            )
            memory_store = MemoryStore(
                user_id=user_id, world_id=world_id, session=session
            )

            # Get all data using shared session
            character = character_store.get_character_by_id(character_id)
            player = player_store.get_player_by_id(player_id)
            encounter = encounter_store.get_encounter_by_id(encounter_id)

            # Auto-add character to encounter if not already present
            # Can happen if you create an encounter and add a character without saving
            if character_id not in encounter.character_ids:
                encounter_store.add_character_to_encounter(encounter_id, character_id)
                # Refresh encounter data after adding character
                encounter = encounter_store.get_encounter_by_id(encounter_id)

            all_reveals = reveal_store.get_by_character_id(character_id)
            all_memories = memory_store.get_by_character_id(character_id)

        # Calculate skill check and filter reveals outside of session
        total_roll = calculate_skill_check(
            skill=skill, player=player, d20_roll=d20_roll
        )
        filtered_reveals = filter_reveals_by_roll(all_reveals, total_roll)

        # Common template context for all challenge agents
        base_template_context = {
            "character": character,
            "player": player,
            "character_memories": all_memories,
            "encounter": encounter,
        }

        if d20_roll == D20Outcomes.CRITICAL_SUCCESS.value:
            # Add filtered reveals and 70 word limit for critical success
            template_context = {
                **base_template_context,
                "filtered_reveals": filtered_reveals,
                "max_response_length": 70,
            }
            rendered_prompt = render_jinja_prompt(
                "challenge_agent_critical_success", template_context
            )
            rendered_instructions = render_jinja_prompt(
                "challenge_agent_instructions", template_context
            )
        elif d20_roll == D20Outcomes.CRITICAL_FAILURE.value:
            rendered_prompt = render_jinja_prompt(
                "challenge_agent_critical_failure",
                {**base_template_context, "max_response_length": 40},
            )
        else:
            # Add filtered reveals, d20_roll, and 40 word limit for standard challenge
            template_context = {
                **base_template_context,
                "filtered_reveals": filtered_reveals,
                "max_response_length": 40,
                "d20_roll": total_roll,
            }
            rendered_prompt = render_jinja_prompt("challenge_agent", template_context)
            rendered_instructions = render_jinja_prompt(
                "challenge_agent_instructions", template_context
            )

        agent = ChallengeAgent(
            system_prompt=rendered_prompt,
            instructions=rendered_instructions if rendered_instructions else None,
        )
        # Create deps with encounter context
        deps = ChallengeAgentDeps(
            encounter=encounter,
            # TODO: Adding history seems to reduce the chance the LLM answers with reveals, which is the purpose of challenges
            messages=None,
            telemetry=lambda: get_client().update_current_trace(
                user_id=user_id,
                name="challenge-agent",
                tags=["challenge"],
                metadata=agent.metadata,
            ),
        )
        response = await agent.chat(player_transcript=transcription, deps=deps)
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
            raise

    except Exception as e:
        logger.error(f"Processing challenge failed: {e}")
        raise
    finally:
        try:
            # TODO: This crashes if no transcription was recorded and its an empty file
            # Clean up temporary files
            cleanup_files(wav_path)
        except Exception as e:
            logger.error(f"Could not destroy temp wav_path {wav_path}. {e}")
