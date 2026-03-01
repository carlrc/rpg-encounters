import asyncio
import logging

from fastapi import WebSocket
from langfuse import get_client, observe

from app.agents.challenge_agent import ChallengeAgent, ChallengeAgentDeps
from app.agents.prompts.import_prompts import render_prompt, render_prompt_section
from app.agents.prompts.limits import (
    MAX_RESPONSE_WORD_LENGTH,
    STANDARD_RESPONSE_WORD_LENGTH,
)
from app.clients.tts import create_tts_provider
from app.db.connection import get_async_db_session
from app.models.conversation import ConversationData
from app.moderation.response_handler import handle_moderation_response
from app.services.ability_challenge import (
    D20Outcomes,
    calculate_skill_check,
    filter_reveals_by_roll,
)
from app.services.audio_processor import cleanup_files, save_chunks_to_wav
from app.services.billing_responses import send_insufficient_tokens_response
from app.services.context import get_conversation_context
from app.services.reveal_progress import calculate_reveal_progress
from app.services.transcription import transcribe_and_moderate
from app.services.user_token import UserTokenService
from app.services.websocket import get_audio_chunks, stream_tts_audio

logger = logging.getLogger(__name__)


def render_challenge_prompts(
    ctx, d20_roll: int, filtered_reveals
) -> tuple[str, str | None]:
    """Render challenge prompts based on D20 roll outcome."""

    # Construct context for all prompts
    base_template_ctx = {
        "character": ctx.character,
        "player": ctx.player,
        "memories": ctx.memories,
        "encounter": ctx.encounter,
        "filtered_reveals": filtered_reveals,
        "max_response_length": STANDARD_RESPONSE_WORD_LENGTH,
    }

    # Render standard prompts
    rendered_prompt = render_prompt("challenge_agent", base_template_ctx)
    rendered_instructions = render_prompt_section(
        "memories_filtered_reveals", base_template_ctx
    )

    if d20_roll == D20Outcomes.CRITICAL_SUCCESS.value:
        # Allow critical success to have longer and more interesting answers
        template_ctx = {
            **base_template_ctx,
            "max_response_length": MAX_RESPONSE_WORD_LENGTH,
        }
        rendered_prompt = render_prompt(
            "challenge_agent_critical_success", template_ctx
        )
    elif d20_roll == D20Outcomes.CRITICAL_FAILURE.value:
        # Critical failures should not share any information so set reveals and memories to None
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
    player_initiated: bool = False,
):
    audio_chunks = await get_audio_chunks(websocket=websocket)
    audio_format = websocket.query_params.get("audio_format", "webm")
    token_service = UserTokenService()
    wav_path, sufficient_tokens = await asyncio.gather(
        save_chunks_to_wav(audio_chunks, audio_format=audio_format),
        token_service.check_token_balance(user_id=user_id),
    )

    try:
        if not sufficient_tokens:
            logger.info(
                f"Insufficient tokens for challenge user={user_id} player={player_id} encounter={encounter_id}"
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

            # Calculate skill check using d20 roll, ability (charisma) and skill
            total_roll = calculate_skill_check(
                skill=skill,
                player=ctx.player,
                d20_roll=d20_roll,
                influence=ctx.influence,
            )

            # Conditionally calculate what reveals are available if not player initiated (e.g., for detailed view or not)
            reveals: list[dict] = (
                [
                    calculate_reveal_progress(reveal, total_roll)
                    for reveal in ctx.reveals
                ]
                if not player_initiated
                else []
            )

            try:
                await websocket.send_json(
                    ConversationData(
                        type="conversation_data",
                        influence=total_roll,
                        reveals=reveals,
                    ).model_dump(mode="json")
                )
            except Exception as e:
                logger.error(f"Failed to send challenge data: {e}")

            # Filter out reveals which are below the total roll score (e.g., prioritize high level reveals) and render agent prompt
            rendered_prompt, rendered_instructions = render_challenge_prompts(
                ctx, d20_roll, filter_reveals_by_roll(ctx.reveals, total_roll)
            )
            agent = ChallengeAgent(
                system_prompt=rendered_prompt,
                # In the case of critical failure there is no additional context (e.g., reveals) to give
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

            await token_service.update_token_usage(
                user_id=user_id,
                usage_tokens=agent.last_total_tokens,
            )

            # Stream TTS audio chunks back to frontend
            await stream_tts_audio(
                websocket=websocket,
                tts_provider=create_tts_provider(
                    provider=ctx.character.tts_provider,
                    elevenlabs_user_api_key=ctx.elevenlabs_token,
                ),
                text=response,
                voice_id=ctx.character.voice_id,
            )

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
