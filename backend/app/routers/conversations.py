from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
from app.services.audio_processor import AudioProcessor
from app.services.transcription import WhisperTranscriptionService
from app.services.tts import ElevenLabsTTS
from app.services.agent_manager import AgentManager
from app.data.character_store import character_store
from app.data.player_store import player_store
from app.data.trust_store import trust_state_store
from app.data.nugget_store import nugget_store
from app.services.nugget_service import NuggetService
from app.agents.prompts.import_prompts import import_system_prompt
from app.services.trust_calculator import TrustCalculator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversation", tags=["conversations"])

# Initialize services
audio_processor = AudioProcessor()
transcription_service = WhisperTranscriptionService(model_size="base")
tts_service = ElevenLabsTTS()
agent_manager = AgentManager()
system_prompt = import_system_prompt("character_agent")


@router.websocket("/{player_id}/{character_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: int, character_id: int):
    await websocket.accept()
    logger.debug("WebSocket connection established...")

    # Buffer for audio chunks during recording
    audio_chunks = []

    try:
        while True:
            # Receive message (can be text or binary)
            message = await websocket.receive()

            if "bytes" in message:
                # Binary audio data
                audio_data = message["bytes"]
                audio_chunks.append(audio_data)

            elif "text" in message:
                # Text control signal
                if message["text"] == "END":
                    logger.debug("Received END signal, processing accumulated audio...")
                    break
                else:
                    logger.warning(
                        f"Received unexpected socket message: {message['text']}"
                    )

    except WebSocketDisconnect:
        logger.error("WebSocket connection closed by client...")
        raise

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        raise

    # Process accumulated audio chunks
    if audio_chunks:
        try:
            # Save audio chunks directly to WAV file using ffmpeg
            wav_path = audio_processor.save_chunks_to_wav(audio_chunks)

            # Transcribe player audio from WAV file
            transcription = await transcription_service.transcribe_audio(wav_path)
            logger.info(f"Transcribed audio text: {transcription}")

            # Get character and player information
            character = character_store.get_character_by_id(character_id)
            player = player_store.get_player_by_id(player_id)

            # Get static trust metric between character and player
            base_trust = TrustCalculator.calculate_base_trust(character, player)
            # Get or create persistent trust state
            trust_state = trust_state_store.get_or_create(
                character_id, player_id, base_trust
            )
            # Get information tied to character
            all_nuggets = nugget_store.get_by_character_id(character_id)
            nugget_levels = NuggetService.categorize_nuggets_by_trust(
                trust_state, all_nuggets
            )

            # Get or create persistent character agent
            agent = agent_manager.get_or_create_agent(
                player_id, character_id, character, player, system_prompt, trust_state
            )

            # Generate AI response using character agent
            response = await agent.chat(transcription, nugget_levels)
            logger.debug(f"Generated character response: {response}")

            # TODO: Persist the trust adjustments as a background task here for restart continuity

            # Stream TTS audio chunks back to frontend
            for audio_chunk in tts_service.text_to_speech_stream(
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

        except Exception as e:
            logger.error(f"Audio processing failed: {e}")

        finally:
            # Clean up temporary files
            audio_processor.cleanup_files(wav_path)

    # WebSocket will be closed automatically by FastAPI
    logger.debug("Closing websocket connection...")
