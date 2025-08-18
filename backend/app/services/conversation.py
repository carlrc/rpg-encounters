import logging
from typing import List, Tuple

from fastapi import WebSocket
from sqlalchemy.orm import sessionmaker

from app.agents.conversation_agent import ConversationAgent, ConversationAgentDeps
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.agents.prompts.import_prompts import import_system_prompt
from app.data.character_store import CharacterStore
from app.data.influence_store import InfluenceStore
from app.data.memory_store import MemoryStore
from app.data.player_store import PlayerStore
from app.data.reveal_store import RevealStore
from app.db.connection import get_db_engine
from app.db.models.character import CharacterORM
from app.db.models.encounter import EncounterORM
from app.db.models.influence import InfluenceORM
from app.db.models.memory import MemoryORM
from app.db.models.reveal import RevealORM
from app.dependencies import (
    get_conversation_manager,
    get_transcription_service,
    get_tts_service,
)
from app.models.encounter import Encounter
from app.models.influence import Influence
from app.models.memory import Memory
from app.models.reveal import Reveal
from app.services.audio_processor import cleanup_files, save_chunks_to_wav
from app.services.influence_calculator import calculate_base_influence
from app.services.websocket import get_audio_chunks

logger = logging.getLogger(__name__)

char_system_prompt = import_system_prompt("conversation_agent")
scoring_system_prompt = import_system_prompt("influence_scoring_agent")


def get_conversation_context(
    world_id: int,
    player_id: int,
    character_id: int,
    encounter_id: int,
    base_influence: int,
) -> Tuple[Encounter, Influence, List[Reveal], List[Memory]]:
    """
    Get all conversation-related data for a character in a single database session.
    """
    Session = sessionmaker(get_db_engine())

    try:
        with Session() as session:
            # Get encounter
            encounter_orm = (
                session.query(EncounterORM)
                .filter(
                    EncounterORM.id == encounter_id,
                    EncounterORM.world_id == world_id,
                    EncounterORM.user_id == player_id,
                )
                .first()
            )

            reveals_orm = (
                session.query(RevealORM)
                .join(RevealORM.characters)
                .filter(CharacterORM.id == character_id)
                .all()
            )

            memories_orm = (
                session.query(MemoryORM)
                .join(MemoryORM.characters)
                .filter(CharacterORM.id == character_id)
                .all()
            )

            # Get or create influence in the same session
            influence_orm = (
                session.query(InfluenceORM)
                .filter(
                    InfluenceORM.character_id == character_id,
                    InfluenceORM.player_id == player_id,
                    InfluenceORM.user_id == player_id,
                    InfluenceORM.world_id == world_id,
                )
                .first()
            )

            # Create influence if it doesn't exist
            if not influence_orm:
                influence_orm = InfluenceORM(
                    character_id=character_id,
                    player_id=player_id,
                    base=base_influence,
                    earned=0,
                    user_id=player_id,
                    world_id=world_id,
                )
                session.add(influence_orm)
                session.flush()
                session.commit()
                session.refresh(influence_orm)

            # Convert to domain models
            encounter = Encounter.model_validate(encounter_orm)
            influence = Influence.model_validate(influence_orm)
            reveals = [RevealStore.orm_to_reveal(reveal) for reveal in reveals_orm]
            memories = [MemoryStore.orm_to_memory(memory) for memory in memories_orm]

            return encounter, influence, reveals, memories
    except Exception as e:
        logger.error(f"Failed to get conversation context: {e}")
        raise e


async def have_conversation(
    websocket: WebSocket,
    world_id: int,
    user_id: int,
    player_id: int,
    character_id: int,
    encounter_id: int,
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
        character = CharacterStore(
            world_id=world_id, user_id=user_id
        ).get_character_by_id(character_id=character_id)
        player = PlayerStore(world_id=world_id, user_id=user_id).get_player_by_id(
            player_id=player_id
        )

        # Get all conversation context
        encounter, influence, all_reveals, all_memories = get_conversation_context(
            world_id=world_id,
            player_id=player.id,
            character_id=character.id,
            encounter_id=encounter_id,
            base_influence=calculate_base_influence(character=character, player=player),
        )

        # TODO: getting all reveals and memories even through the agent manager caches instances
        # TODO: Need to only cache convo manager realistically and pass in reveals and memories dynamically
        # If the DM removes memories between conversations or adds something it should be used

        agent = ConversationAgent(
            character=character,
            player=player,
            system_prompt=char_system_prompt,
            memories=all_memories,
            conversation_manager=get_conversation_manager(
                player_id=player.id, character_id=character.id
            ),
            influence_calculator_agent=InfluenceCalculatorAgent(
                system_prompt=scoring_system_prompt,
                character=character,
                player=player,
            ),
        )

        # Generate AI response using character agent
        response, level, influence = await agent.chat(
            player_transcript=transcription,
            deps=ConversationAgentDeps(
                reveals=all_reveals,
                encounter_description=encounter.description,
                influence=influence,
            ),
        )
        logger.debug(
            f"Generated character response for level ${level.name}: {response}"
        )

        InfluenceStore(user_id=user_id, world_id=world_id).update_influence(
            influence=influence
        )

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
