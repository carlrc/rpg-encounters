import logging
import os

from fastapi import WebSocket
from langfuse import get_client

from app.agents.challenges.challenge_agent import ChallengeAgent, ChallengeAgentDeps
from app.agents.challenges.critical_failure_agent import CriticalFailureAgent
from app.agents.challenges.critical_success_agent import CriticalSuccessAgent
from app.agents.prompts.import_prompts import import_system_prompt
from app.data.character_store import CharacterStore
from app.data.conversation_store import ConversationStore
from app.data.encounter_store import EncounterStore
from app.data.memory_store import MemoryStore
from app.data.player_store import PlayerStore
from app.data.reveal_store import RevealStore
from app.dependencies import (
    get_transcription_service,
    get_tts_service,
)
from app.models.encounter import EncounterUpdate
from app.services.ability_challenge import (
    D20Outcomes,
    calculate_skill_check,
    filter_reveals_by_roll,
)
from app.services.audio_processor import cleanup_files, save_chunks_to_wav
from app.services.websocket import get_audio_chunks

logger = logging.getLogger(__name__)

challenge_agent_system_prompt = import_system_prompt("challenge_agent")
challenge_agent_critical_success_system_prompt = import_system_prompt(
    "challenge_agent_critical_success"
)
challenge_agent_critical_failure_system_prompt = import_system_prompt(
    "challenge_agent_critical_failure"
)


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
    # TODO: Need to get chat history and incorporate it into responses
    # TODO: We should be able to cancel on the frontend if the player made a mistake for instance before closing the connection
    audio_chunks = await get_audio_chunks(websocket=websocket)
    # TODO: saving to WAV needs to be made async
    wav_path = save_chunks_to_wav(audio_chunks)
    transcription = await get_transcription_service().transcribe_audio(wav_path)
    logger.info(f"Transcribed audio text: {transcription}")

    try:
        # Get player and character data
        character = CharacterStore(
            world_id=world_id, user_id=user_id
        ).get_character_by_id(character_id)
        player = PlayerStore(world_id=world_id, user_id=user_id).get_player_by_id(
            player_id=player_id
        )
        encounter_store = EncounterStore(world_id=world_id, user_id=user_id)
        encounter = encounter_store.get_encounter_by_id(encounter_id=encounter_id)

        # Auto-add character to encounter if not already present
        # Can happen if you create an encounter and add a character without saving
        current_character_ids = encounter.character_ids or []
        if character_id not in current_character_ids:
            current_character_ids.append(character_id)
            encounter_update = EncounterUpdate(
                id=encounter_id, character_ids=current_character_ids
            )
            encounter_store.update_encounter(encounter_id, encounter_update)

        # Calculate skill check: d20 + player skill bonus
        total_roll = calculate_skill_check(
            skill=skill, player=player, d20_roll=d20_roll
        )

        # Get information tied to character
        all_reveals = RevealStore(
            world_id=world_id, user_id=user_id
        ).get_by_character_id(character_id)
        conversation = ConversationStore(user_id=user_id, world_id=world_id).get(
            player_id=player_id, character_id=character_id, encounter_id=encounter_id
        )
        filtered_reveals = filter_reveals_by_roll(all_reveals, total_roll)
        all_memories = MemoryStore(
            world_id=world_id, user_id=user_id
        ).get_by_character_id(character_id)

        if d20_roll == D20Outcomes.CRITICAL_SUCCESS.value:
            agent = CriticalSuccessAgent(
                character=character,
                player=player,
                system_prompt=challenge_agent_critical_success_system_prompt,
                memories=all_memories,
                reveals=filtered_reveals,
            )
            challenge_agent_name = "crit-success-agent"
        elif d20_roll == D20Outcomes.CRITICAL_FAILURE.value:
            agent = CriticalFailureAgent(
                character=character,
                player=player,
                system_prompt=challenge_agent_critical_failure_system_prompt,
                memories=all_memories,
            )
            challenge_agent_name = "crit-failure-agent"
        else:
            agent = ChallengeAgent(
                character=character,
                player=player,
                system_prompt=challenge_agent_system_prompt,
                memories=all_memories,
                reveals=filtered_reveals,
            )
            challenge_agent_name = "challenge-agent"

        # Create deps with encounter context
        deps = ChallengeAgentDeps(
            encounter=encounter,
            messages=conversation.messages if conversation else None,
            telemetry=lambda: get_client().update_current_trace(
                user_id=user_id,
                name=challenge_agent_name,
                tags=["challenge"],
                metadata={
                    "service": "backend",
                    "env": os.getenv("ENVIRONMENT"),
                },
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
