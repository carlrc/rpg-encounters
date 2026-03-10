import asyncio
import logging

from fastapi import WebSocket
from langfuse import get_client, observe

from app.agents.base_agent import AgentGenerationError
from app.agents.conversations.conversation_agent import (
    ConversationAgent,
    ConversationAgentDeps,
)
from app.agents.conversations.negative_conversation_agent import (
    NegativeConvoAgent,
    NegativeConvoAgentDeps,
)
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.agents.prompts.import_prompts import render_prompt
from app.agents.prompts.limits import STANDARD_RESPONSE_WORD_LENGTH
from app.clients.tts import TtsGenerationError, create_tts_provider
from app.data.conversation_store import ConversationStore
from app.data.influence_store import InfluenceStore
from app.db.connection import get_async_db_session
from app.models.conversation import ConversationData
from app.models.reveal import REVEAL_DEFAULT_THRESHOLDS, RevealLayer
from app.moderation.response_handler import handle_moderation_response
from app.services.audio_processor import cleanup_files, save_chunks_to_wav
from app.services.billing_responses import send_insufficient_tokens_response
from app.services.context import get_conversation_context
from app.services.llm_latency import llm_latency_notice
from app.services.reveal_progress import calculate_reveal_progress
from app.services.transcription import TranscriptionError, transcribe_and_moderate
from app.services.user_token import UserTokenService
from app.services.websocket import (
    WARNING_MESSAGE_LLM_FAILED,
    WARNING_MESSAGE_TRANSCRIPTION_FAILED,
    WARNING_MESSAGE_TTS_FAILED,
    get_audio_chunks,
    send_warning_and_close,
    stream_tts_audio,
)

logger = logging.getLogger(__name__)


@observe
async def have_conversation(
    websocket: WebSocket,
    world_id: int,
    user_id: int,
    player_id: int,
    character_id: int,
    encounter_id: int,
    player_initiated: bool = False,
) -> None:
    audio_chunks = await get_audio_chunks(websocket=websocket)
    audio_format = websocket.query_params.get("audio_format", "webm")
    token_service = UserTokenService()
    wav_path, sufficient_tokens = await asyncio.gather(
        save_chunks_to_wav(chunks=audio_chunks, audio_format=audio_format),
        token_service.check_token_balance(user_id=user_id),
    )

    try:
        if not sufficient_tokens:
            logger.info(
                f"Insufficient tokens for conversation user={user_id} player={player_id} encounter={encounter_id}"
            )
            await send_insufficient_tokens_response(websocket=websocket)
            return

        async with get_async_db_session() as session:
            # Do large DB context lookup along with transcription and moderation checks
            ctx, (transcription, is_blocked) = await asyncio.gather(
                get_conversation_context(
                    world_id=world_id,
                    user_id=user_id,
                    player_id=player_id,
                    character_id=character_id,
                    encounter_id=encounter_id,
                    session=session,
                ),
                transcribe_and_moderate(user_id=user_id, wav_file_path=wav_path),
            )

            # If flagged, fallback to default reply
            if is_blocked:
                await handle_moderation_response(
                    websocket=websocket,
                    user_id=user_id,
                    text=transcription,
                    response=is_blocked,
                    ctx=ctx,
                )
                return

            # Set user message as overall trace input
            get_client().update_current_trace(input=transcription)

            # Common prompt template for positive/negative conversation agents
            template_ctx = {
                "max_response_length": STANDARD_RESPONSE_WORD_LENGTH,
                "character": ctx.character,
                "memories": ctx.memories,
                "player": ctx.player,
                "encounter": ctx.encounter,
            }

            # Agent for scoring user input against character motivations
            influence_agent = InfluenceCalculatorAgent(
                system_prompt=render_prompt(
                    "influence_scoring_agent",
                    template_ctx,
                ),
            )

            # If negative influence, use negative sentiment agent
            negative_attitude = (
                ctx.influence.score < REVEAL_DEFAULT_THRESHOLDS[RevealLayer.STANDARD]
            )
            if negative_attitude:
                agent = NegativeConvoAgent(
                    instructions=render_prompt(
                        "negative_conversation_agent", template_ctx
                    ),
                    conversation_store=ConversationStore(
                        user_id=user_id, world_id=world_id, session=session
                    ),
                    influence_calculator_agent=influence_agent,
                )

                # Reveal thresholds cannot be negative, so don't pass any
                async with llm_latency_notice(websocket=websocket):
                    response, influence = await agent.chat(
                        player_transcript=transcription,
                        deps=NegativeConvoAgentDeps(
                            context=ctx,
                            telemetry=lambda: get_client().update_current_span(
                                name="negative-convo-agent",
                                metadata=agent.metadata,
                            ),
                        ),
                    )
            else:
                # Add reveals for positive conversation agent
                template_ctx["reveals"] = ctx.reveals

                agent = ConversationAgent(
                    instructions=render_prompt("conversation_agent", template_ctx),
                    conversation_store=ConversationStore(
                        user_id=user_id, world_id=world_id, session=session
                    ),
                    influence_calculator_agent=influence_agent,
                )

                async with llm_latency_notice(websocket=websocket):
                    response, _, influence = await agent.chat(
                        player_transcript=transcription,
                        deps=ConversationAgentDeps(
                            context=ctx,
                            telemetry=lambda: get_client().update_current_span(
                                name="positive-convo-agent",
                                metadata=agent.metadata,
                            ),
                        ),
                    )

            # Force overall trace output to be LLM response
            get_client().update_current_trace(output=response)

            # Record token usage after successful generation
            await token_service.update_token_usage(
                user_id=user_id,
                usage_tokens=agent.last_total_tokens
                + influence_agent.last_total_tokens,
            )

            # Persist influence adjustment
            await InfluenceStore(
                user_id=user_id, world_id=world_id, session=session
            ).update(influence=influence)

            # If not player initiated return adjusted influence etc for detailed view
            if not player_initiated:
                try:
                    await websocket.send_json(
                        ConversationData(
                            type="conversation_data",
                            influence=influence.score,
                            reveals=[
                                calculate_reveal_progress(reveal, influence.score)
                                for reveal in ctx.reveals
                            ],
                        ).model_dump()
                    )
                except Exception as e:
                    logger.error(f"Failed to send conversation data: {e}")

            # Stream TTS audio chunks back to frontend
            await stream_tts_audio(
                websocket=websocket,
                tts_provider=create_tts_provider(
                    provider=ctx.character.tts_provider,
                ),
                text=response,
                voice_id=ctx.character.voice_id,
            )

    except TranscriptionError:
        return await send_warning_and_close(
            websocket=websocket,
            message=WARNING_MESSAGE_TRANSCRIPTION_FAILED,
        )
    except AgentGenerationError:
        return await send_warning_and_close(
            websocket=websocket,
            message=WARNING_MESSAGE_LLM_FAILED,
        )
    except TtsGenerationError:
        return await send_warning_and_close(
            websocket=websocket,
            message=WARNING_MESSAGE_TTS_FAILED,
        )
    except Exception as e:
        logger.error(f"Processing conversation failed: {e}")
        raise
    finally:
        try:
            # Clean up temporary files
            cleanup_files(wav_path)
        except Exception as e:
            logger.error(f"Could not destroy temp wav_path {wav_path}. {e}")
