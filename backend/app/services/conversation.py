import logging

from fastapi import WebSocket
from langfuse import get_client

from app.agents.conversations.conversation_agent import (
    ConversationAgent,
    ConversationAgentDeps,
)
from app.agents.conversations.negative_conversation_agent import (
    NegativeConvoAgent,
    NegativeConvoAgentDeps,
)
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.agents.prompts.import_prompts import render_jinja_prompt
from app.clients.elevan_labs import ElevenLabs
from app.data.character_store import CharacterStore
from app.data.conversation_store import ConversationStore
from app.data.influence_store import InfluenceStore
from app.data.player_store import PlayerStore
from app.db.connection import get_db_session
from app.dependencies import (
    get_transcription_service,
)
from app.models.reveal import REVEAL_DEFAULT_THRESHOLDS, RevealLayer
from app.services.audio_processor import cleanup_files, save_chunks_to_wav
from app.services.context import get_conversation_context
from app.services.influence_calculator import calculate_base_influence
from app.services.reveal_progress import calculate_reveal_progress
from app.services.websocket import get_audio_chunks

logger = logging.getLogger(__name__)


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
        with get_db_session() as session:
            # Get character and player information
            character = CharacterStore(
                world_id=world_id, user_id=user_id, session=session
            ).get_character_by_id(character_id=character_id)
            player = PlayerStore(
                world_id=world_id, user_id=user_id, session=session
            ).get_player_by_id(player_id=player_id)

            base_influence = calculate_base_influence(
                character=character, player=player
            )
            context = get_conversation_context(
                world_id=world_id,
                user_id=user_id,
                player_id=player.id,
                character_id=character.id,
                encounter_id=encounter_id,
                base_influence=base_influence,
                session=session,
            )

            # Common template context for both conversation agents
            template_context = {
                "max_response_length": 30,
                "character": character,
                "character_memories": context.memories,
                "player": player,
                "encounter": context.encounter,
            }

            influence_agent = InfluenceCalculatorAgent(
                system_prompt=render_jinja_prompt(
                    "influence_scoring_agent",
                    {
                        "character": character,
                        "player": player,
                    },
                ),
            )

            # If negative sentiment, make the conversation negative
            negative_attitude = (
                context.influence.score
                < REVEAL_DEFAULT_THRESHOLDS[RevealLayer.STANDARD]
            )
            if negative_attitude:
                logger.info("Using negative conversation agent...")

                # Render the Jinja template
                rendered_negative_system_prompt = render_jinja_prompt(
                    "negative_conversation_agent", template_context
                )

                agent = NegativeConvoAgent(
                    system_prompt=rendered_negative_system_prompt,
                    conversation_store=ConversationStore(
                        user_id=user_id, world_id=world_id, session=session
                    ),
                    influence_calculator_agent=influence_agent,
                )

                # Reveals thresholds cannot be negative, so don't pass any
                response, influence = await agent.chat(
                    player_transcript=transcription,
                    deps=NegativeConvoAgentDeps(
                        player=player,
                        character=character,
                        context=context,
                        user_id=user_id,
                        telemetry=lambda: get_client().update_current_trace(
                            user_id=user_id,
                            name="negative-convo-agent",
                            tags=["conversation"],
                            metadata=agent.metadata,
                        ),
                    ),
                )
            else:
                logger.info("Using positive conversation agent...")

                # Add reveals for positive conversation agent
                template_context["character_reveals"] = context.reveals

                # Render the Jinja template
                rendered_system_prompt = render_jinja_prompt(
                    "conversation_agent", template_context
                )
                # LLM does not handle choosing reveals and memories well when combined in system prompt
                rendered_instructions = render_jinja_prompt(
                    "conversation_agent_instructions", template_context
                )

                agent = ConversationAgent(
                    system_prompt=rendered_system_prompt,
                    instructions=rendered_instructions,
                    conversation_store=ConversationStore(
                        user_id=user_id, world_id=world_id, session=session
                    ),
                    influence_calculator_agent=influence_agent,
                )

                response, _, influence = await agent.chat(
                    player_transcript=transcription,
                    deps=ConversationAgentDeps(
                        player=player,
                        character=character,
                        context=context,
                        user_id=user_id,
                        telemetry=lambda: get_client().update_current_trace(
                            user_id=user_id,
                            name="positive-convo-agent",
                            tags=["conversation"],
                            metadata=agent.metadata,
                        ),
                    ),
                )

            InfluenceStore(
                user_id=user_id, world_id=world_id, session=session
            ).update_influence(influence=influence)

            # Send conversation data before audio streaming
            conversation_data = {
                "type": "conversation_data",
                "influence": influence.score,
                "reveals": [
                    calculate_reveal_progress(reveal, influence.score)
                    for reveal in context.reveals
                ],
            }

            try:
                await websocket.send_json(conversation_data)
            except Exception as e:
                logger.error(f"Failed to send conversation data: {e}")

            # Stream TTS audio chunks back to frontend
            async for audio_chunk in ElevenLabs().text_to_speech_stream(
                text=response, voice_id=character.voice_id
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
