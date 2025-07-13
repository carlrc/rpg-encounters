from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn
import asyncio
from app.services.audio_processor import AudioProcessor
from app.services.transcription import WhisperTranscriptionService
from app.services.tts import ElevenLabsTTS
from app.services.llm import OllamaService
from app.services.conversation_manager import ConversationManager
from app.routers import players, characters

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="D&D AI Character Backend")

# Include routers
app.include_router(players.router)
app.include_router(characters.router)

# Initialize services
audio_processor = AudioProcessor()
transcription_service = WhisperTranscriptionService(model_size="base")
tts_service = ElevenLabsTTS()
llm_service = OllamaService(model_name="mistral")
conversation_manager = ConversationManager(exchange_threshold=5)

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite dev server ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "D&D AI Character Backend is running"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
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
            logger.debug(f"Transcribed audio text: {transcription}")
            
            # Add user message to conversation history
            conversation_manager.add_message(f"user: {transcription}")
            
            # Build context-aware prompt with conversation history
            system_prompt = llm_service.get_dnd_character_system_prompt()
            full_prompt = conversation_manager.build_prompt(system_prompt, max_tokens=2048)
            
            # Generate AI response using conversation context
            response_text = await llm_service.generate_response(full_prompt)
            logger.debug(f"Generated LLM response: {response_text}")
            
            # Add assistant response to conversation history
            conversation_manager.add_message(f"agent: {response_text}")
            
            # Check if summarization is needed and handle it
            if conversation_manager.should_summarize():
                logger.info("Triggering conversation summarization...")
                
                # Create async wrapper for the LLM service
                async def llm_wrapper(prompt: str, sys_prompt: str = None) -> str:
                    return await llm_service.generate_response(prompt, sys_prompt)
                
                # Run summarization (this is async but we want it to complete)
                def sync_llm_wrapper(prompt: str, sys_prompt: str = None) -> str:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return loop.run_until_complete(llm_wrapper(prompt, sys_prompt))
                    finally:
                        loop.close()
                
                conversation_manager.summarize_recent_exchanges(sync_llm_wrapper)
            
            # Stream TTS audio chunks back to frontend
            logger.info("Starting TTS streaming...")
            for audio_chunk in tts_service.text_to_speech_stream(response_text):
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
