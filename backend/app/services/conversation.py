import logging
import os
from typing import List, Tuple

from fastapi import WebSocket
from langfuse import get_client
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter
from sqlalchemy.orm import sessionmaker

from app.agents.conversations.conversation_agent import (
    ConversationAgent,
    ConversationAgentDeps,
)
from app.agents.conversations.negative_conversation_agent import (
    NegativeConvoAgent,
    NegativeConvoAgentDeps,
)
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.agents.prompts.import_prompts import import_system_prompt
from app.data.character_store import CharacterStore
from app.data.conversation_store import ConversationStore
from app.data.influence_store import InfluenceStore
from app.data.memory_store import MemoryStore
from app.data.player_store import PlayerStore
from app.data.reveal_store import RevealStore
from app.db.connection import get_db_engine
from app.db.models.character import CharacterORM
from app.db.models.conversation import ConversationORM
from app.db.models.encounter import EncounterORM
from app.db.models.influence import InfluenceORM
from app.db.models.memory import MemoryORM
from app.db.models.reveal import RevealORM
from app.dependencies import (
    get_transcription_service,
    get_tts_service,
)
from app.models.encounter import Encounter
from app.models.influence import Influence
from app.models.memory import Memory
from app.models.reveal import REVEAL_DEFAULT_THRESHOLDS, Reveal, RevealLayer
from app.services.audio_processor import cleanup_files, save_chunks_to_wav
from app.services.influence_calculator import calculate_base_influence
from app.services.reveal_progress import calculate_reveal_progress
from app.services.websocket import get_audio_chunks

logger = logging.getLogger(__name__)

char_system_prompt = import_system_prompt("conversation_agent")
negative_char_system_prompt = import_system_prompt("negative_conversation_agent")
scoring_system_prompt = import_system_prompt("influence_scoring_agent")


def get_conversation_context(
    world_id: int,
    player_id: int,
    user_id: int,
    character_id: int,
    encounter_id: int,
    base_influence: int,
) -> Tuple[Encounter, Influence, List[Reveal], List[Memory], List[ModelMessage] | None]:
    """
    Get all conversation-related data for a character in a single database session.
    Auto-adds character to encounter if not already present.
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
                    EncounterORM.user_id == user_id,
                )
                .first()
            )

            # Auto-add character to encounter if not already present
            current_character_ids = [char.id for char in encounter_orm.characters]
            if character_id not in current_character_ids:
                logger.debug(
                    f"Auto-adding character {character_id} to encounter {encounter_id}"
                )
                # Get the character ORM object and add to relationship
                character_orm = (
                    session.query(CharacterORM)
                    .filter(
                        CharacterORM.id == character_id,
                        CharacterORM.world_id == world_id,
                        CharacterORM.user_id == user_id,
                    )
                    .first()
                )
                encounter_orm.characters.append(character_orm)
                session.flush()
                session.commit()

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

            conversation_orm = (
                session.query(ConversationORM)
                .filter(
                    ConversationORM.player_id == player_id,
                    ConversationORM.character_id == character_id,
                    ConversationORM.encounter_id == encounter_id,
                    ConversationORM.user_id == user_id,
                    ConversationORM.world_id == world_id,
                )
                .first()
            )

            # Create conversation if it doesn't exist
            if not conversation_orm:
                conversation_orm = ConversationORM(
                    player_id=player_id,
                    character_id=character_id,
                    encounter_id=encounter_id,
                    user_id=user_id,
                    world_id=world_id,
                    messages=None,
                )
                session.add(conversation_orm)
                session.flush()
                session.commit()
                session.refresh(conversation_orm)

            # Get or create influence in the same session
            influence_orm = (
                session.query(InfluenceORM)
                .filter(
                    InfluenceORM.character_id == character_id,
                    InfluenceORM.player_id == player_id,
                    InfluenceORM.user_id == user_id,
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
                    user_id=user_id,
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
            messages = (
                ModelMessagesTypeAdapter.validate_json(conversation_orm.messages)
                if conversation_orm and conversation_orm.messages
                else None
            )

            return encounter, influence, reveals, memories, messages
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
        base_influence = calculate_base_influence(character=character, player=player)
        # Get all conversation context
        encounter, influence, all_reveals, all_memories, messages = (
            get_conversation_context(
                world_id=world_id,
                user_id=user_id,
                player_id=player.id,
                character_id=character.id,
                encounter_id=encounter_id,
                base_influence=base_influence,
            )
        )

        # TODO: getting all reveals and memories even through the agent manager caches instances
        # TODO: Need to only cache convo manager realistically and pass in reveals and memories dynamically
        # If the DM removes memories between conversations or adds something it should be used
        # TODO: Convo history not persisting between convo agents

        # If negative sentiment, make the conversation negative
        negative_attitude = (
            influence.score < REVEAL_DEFAULT_THRESHOLDS[RevealLayer.STANDARD]
        )
        logger.info(
            f"char {character.id} influence to player {player.id} = {influence.score}"
        )
        if negative_attitude:
            logger.info("Using negative conversation agent...")
            agent = NegativeConvoAgent(
                character=character,
                player=player,
                system_prompt=negative_char_system_prompt,
                memories=all_memories,
                conversation_store=ConversationStore(
                    user_id=user_id, world_id=world_id
                ),
                influence_calculator_agent=InfluenceCalculatorAgent(
                    system_prompt=scoring_system_prompt,
                    character=character,
                    player=player,
                ),
            )

            # Reveals thresholds cannot be negative, so don't pass any
            response, influence = await agent.chat(
                player_transcript=transcription,
                deps=NegativeConvoAgentDeps(
                    encounter=encounter,
                    influence=influence,
                    user_id=user_id,
                    telemetry=lambda: get_client().update_current_trace(
                        user_id=user_id,
                        name="negative-convo-agent",
                        tags=["conversation"],
                        metadata={
                            "service": "backend",
                            "env": os.getenv("ENVIRONMENT"),
                        },
                    ),
                    message_history=messages,
                ),
            )
        else:
            logger.info("Using positive conversation agent...")
            agent = ConversationAgent(
                character=character,
                player=player,
                system_prompt=char_system_prompt,
                memories=all_memories,
                conversation_store=ConversationStore(
                    user_id=user_id, world_id=world_id
                ),
                influence_calculator_agent=InfluenceCalculatorAgent(
                    system_prompt=scoring_system_prompt,
                    character=character,
                    player=player,
                ),
            )

            response, _, influence = await agent.chat(
                player_transcript=transcription,
                deps=ConversationAgentDeps(
                    reveals=all_reveals,
                    encounter=encounter,
                    influence=influence,
                    user_id=user_id,
                    message_history=messages,
                    telemetry=lambda: get_client().update_current_trace(
                        user_id=user_id,
                        name="positive-convo-agent",
                        tags=["conversation"],
                        metadata={
                            "service": "backend",
                            "env": os.getenv("ENVIRONMENT"),
                        },
                    ),
                ),
            )

        InfluenceStore(user_id=user_id, world_id=world_id).update_influence(
            influence=influence
        )

        # Send conversation data before audio streaming
        conversation_data = {
            "type": "conversation_data",
            "influence": influence.score,
            "reveals": [
                calculate_reveal_progress(reveal, influence.score)
                for reveal in all_reveals
            ],
        }

        try:
            await websocket.send_json(conversation_data)
        except Exception as e:
            logger.error(f"Failed to send conversation data: {e}")

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
            raise

    except Exception as e:
        logger.error(f"Processing conversation failed: {e}")
        raise
    finally:
        try:
            # TODO: This crashes if no transcription was recorded and its an empty file
            # Clean up temporary files
            cleanup_files(wav_path)
        except Exception as e:
            logger.error(f"Could not destroy temp wav_path {wav_path}. {e}")
