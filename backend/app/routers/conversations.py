from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
from app.services.audio_processor import AudioProcessor
from app.services.transcription import WhisperTranscriptionService
from app.services.tts import ElevenLabsTTS
from app.ai.character_agent import CharacterAgent
from app.services.memory_manager import MemoryManager
from app.data.character_store import character_store
from app.data.player_store import player_store

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversation", tags=["conversations"])

# Initialize services
audio_processor = AudioProcessor()
transcription_service = WhisperTranscriptionService(model_size="base")
tts_service = ElevenLabsTTS()
memory_manager = MemoryManager()

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
                    logger.warning(f"Received unexpected socket message: {message['text']}")
                
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
            
            transcription = await transcription_service.transcribe_audio(wav_path)
            logger.info(f"Transcribed audio text: {transcription}")
            
            character = character_store.get_character_by_id(character_id)
            player = player_store.get_player_by_id(player_id)
            
            # Get relevant memories for this character and player
            memories = memory_manager.get_memories(character_id, player_id)
            
            # Create character agent
            agent = CharacterAgent(character, player)
            
            # Generate AI response using character agent
            result = await agent.chat(transcription, memories)
            logger.debug(f"Generated character response: {result.output}")
            
            
            
            # Stream TTS audio chunks back to frontend
            for audio_chunk in tts_service.text_to_speech_stream(result.output):
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
