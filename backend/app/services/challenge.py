import logging

from fastapi import WebSocket
from langfuse import get_client, observe

from app.agents.challenge_agent import ChallengeAgent, ChallengeAgentDeps
from app.agents.prompts.import_prompts import render_prompt, render_prompt_section
from app.agents.prompts.limits import (
    MAX_CHALLENGE_RESPONSE_WORD_LENGTH,
    MAX_RESPONSE_WORD_LENGTH,
)
from app.clients.tts import create_tts_provider
from app.db.connection import get_async_db_session
from app.dependencies import get_transcription_service
from app.models.conversation import ConversationData
from app.services.ability_challenge import (
    D20Outcomes,
    calculate_skill_check,
    filter_reveals_by_roll,
)
from app.services.audio_processor import cleanup_files, save_chunks_to_wav
from app.services.context import get_conversation_context
from app.services.reveal_progress import calculate_reveal_progress
from app.services.websocket import get_audio_chunks

logger = logging.getLogger(__name__)


def render_challenge_prompts(
    ctx, d20_roll: int, filtered_reveals
) -> tuple[str, str | None]:
    """Render challenge prompts based on D20 roll outcome."""

    base_template_ctx = {
        "character": ctx.character,
        "player": ctx.player,
        "memories": ctx.memories,
        "encounter": ctx.encounter,
        "filtered_reveals": filtered_reveals,
        "max_response_length": MAX_RESPONSE_WORD_LENGTH,
    }

    # Render standard prompts
    rendered_prompt = render_prompt("challenge_agent", base_template_ctx)
    rendered_instructions = render_prompt_section(
        "memories_filtered_reveals", base_template_ctx
    )

    if d20_roll == D20Outcomes.CRITICAL_SUCCESS.value:
        # Set 70 word limit for critical success for longer answers
        template_ctx = {
            **base_template_ctx,
            "max_response_length": MAX_CHALLENGE_RESPONSE_WORD_LENGTH,
        }
        rendered_prompt = render_prompt(
            "challenge_agent_critical_success", template_ctx
        )
    elif d20_roll == D20Outcomes.CRITICAL_FAILURE.value:
        # Set reveals and memories to None such that LLM can't share anything
        rendered_prompt = render_prompt(
            "challenge_agent_critical_failure",
            {**base_template_ctx, "filtered_reveals": None, "memories": None},
        )
        rendered_instructions = None

    return rendered_prompt, rendered_instructions


@observe
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
    audio_chunks = await get_audio_chunks(websocket=websocket)
    wav_path = await save_chunks_to_wav(audio_chunks)
    transcription = await get_transcription_service().transcribe_audio(wav_path)
    get_client().update_current_trace(input=transcription)
    logger.info(f"Transcribed audio text: {transcription}")

    try:
        async with get_async_db_session() as session:
            ctx = await get_conversation_context(
                world_id=world_id,
                user_id=user_id,
                player_id=player_id,
                character_id=character_id,
                encounter_id=encounter_id,
                session=session,
            )

        # Calculate skill check and filter reveals outside of session
        total_roll = calculate_skill_check(
            skill=skill, player=ctx.player, d20_roll=d20_roll, influence=ctx.influence
        )

        try:
            # TODO: Need to send the modifier (e.g., influence) in this case to make it clear whats happening
            await websocket.send_json(
                ConversationData(
                    influence=total_roll,
                    reveals=[
                        calculate_reveal_progress(reveal, total_roll)
                        for reveal in ctx.reveals
                    ],
                ).model_dump()
            )
        except Exception as e:
            logger.error(f"Failed to send challenge data: {e}")

        # Filter out reveals which are below the total roll score (e.g., prioritize high level reveals) and render prompt
        rendered_prompt, rendered_instructions = render_challenge_prompts(
            ctx, d20_roll, filter_reveals_by_roll(ctx.reveals, total_roll)
        )
        agent = ChallengeAgent(
            system_prompt=rendered_prompt,
            # In the case of critical failure there are no instructions
            instructions=rendered_instructions if rendered_instructions else None,
        )

        # Generate LLM response
        response = await agent.chat(
            player_transcript=transcription,
            deps=ChallengeAgentDeps(
                encounter=ctx.encounter,
                telemetry=lambda: get_client().update_current_span(
                    name="challenge-agent",
                    metadata=agent.metadata,
                ),
            ),
        )

        # Force overall trace output to be LLM response
        get_client().update_current_trace(output=response)

        # Stream TTS audio chunks back to frontend
        async for audio_chunk in create_tts_provider(
            provider=ctx.character.tts_provider
        ).text_to_speech_stream(text=response, voice_id=ctx.character.voice_id):
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
            # Clean up temporary files
            cleanup_files(wav_path)
        except Exception as e:
            logger.error(f"Could not destroy temp wav_path {wav_path}. {e}")
            raise
