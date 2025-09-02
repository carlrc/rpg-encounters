import logging

from fastapi import WebSocket
from langfuse import get_client
from langfuse import observe as langfuse_observe

from app.agents.challenge_agent import ChallengeAgent, ChallengeAgentDeps
from app.agents.prompts.import_prompts import render_jinja_prompt
from app.clients.elevan_labs import ElevenLabs
from app.db.connection import get_async_db_session
from app.dependencies import get_transcription_service
from app.services.ability_challenge import (
    D20Outcomes,
    calculate_skill_check,
    filter_reveals_by_roll,
)
from app.services.audio_processor import cleanup_files, save_chunks_to_wav
from app.services.context import get_conversation_context
from app.services.websocket import get_audio_chunks

logger = logging.getLogger(__name__)


def _render_challenge_prompts(
    ctx, d20_roll: int, filtered_reveals, total_roll: int
) -> tuple[str, str | None]:
    """Render challenge prompts based on D20 roll outcome."""

    # Common template ctx for all challenge agents
    base_template_ctx = {
        "character": ctx.character,
        "player": ctx.player,
        "character_memories": ctx.memories,
        "encounter": ctx.encounter,
    }

    if d20_roll == D20Outcomes.CRITICAL_SUCCESS.value:
        # Add filtered reveals and 70 word limit for critical success
        template_ctx = {
            **base_template_ctx,
            "filtered_reveals": filtered_reveals,
            "max_response_length": 70,
        }
        rendered_prompt = render_jinja_prompt(
            "challenge_agent_critical_success", template_ctx
        )
        rendered_instructions = render_jinja_prompt(
            "challenge_agent_instructions", template_ctx
        )
    elif d20_roll == D20Outcomes.CRITICAL_FAILURE.value:
        rendered_prompt = render_jinja_prompt(
            "challenge_agent_critical_failure",
            {**base_template_ctx, "max_response_length": 40},
        )
        rendered_instructions = None
    else:
        # Add filtered reveals, d20_roll, and 40 word limit for standard challenge
        template_ctx = {
            **base_template_ctx,
            "filtered_reveals": filtered_reveals,
            "max_response_length": 40,
            "d20_roll": total_roll,
        }
        rendered_prompt = render_jinja_prompt("challenge_agent", template_ctx)
        rendered_instructions = render_jinja_prompt(
            "challenge_agent_instructions", template_ctx
        )

    return rendered_prompt, rendered_instructions


@langfuse_observe
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
            skill=skill, player=ctx.player, d20_roll=d20_roll
        )
        filtered_reveals = filter_reveals_by_roll(ctx.reveals, total_roll)

        rendered_prompt, rendered_instructions = _render_challenge_prompts(
            ctx, d20_roll, filtered_reveals, total_roll
        )

        agent = ChallengeAgent(
            system_prompt=rendered_prompt,
            # In the case of critical failure there are no instructions
            instructions=rendered_instructions if rendered_instructions else None,
        )
        # Create deps with encounter ctx
        deps = ChallengeAgentDeps(
            encounter=ctx.encounter,
            # TODO: [SPIKE] Adding message history seems to reduce the chance the LLM answers with reveals, which is the purpose of challenges
            messages=None,
            telemetry=lambda: get_client().update_current_span(
                name="challenge-agent",
                metadata=agent.metadata,
            ),
        )
        response = await agent.chat(player_transcript=transcription, deps=deps)
        logger.debug(
            f"Generated character response for D20 roll {d20_roll}: {response}"
        )

        # Force overall trace output to be LLM response
        get_client().update_current_trace(output=response)

        # Stream TTS audio chunks back to frontend
        async for audio_chunk in ElevenLabs().text_to_speech_stream(
            response, ctx.character.voice_id
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
            # Clean up temporary files
            cleanup_files(wav_path)
        except Exception as e:
            logger.error(f"Could not destroy temp wav_path {wav_path}. {e}")
            raise
