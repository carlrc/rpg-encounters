from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn
from app.services.audio_processor import AudioProcessor
from app.services.transcription import WhisperTranscriptionService
from app.services.tts import ElevenLabsTTS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="D&D AI Character Backend")

# Initialize services
audio_processor = AudioProcessor()
transcription_service = WhisperTranscriptionService(model_size="base")
tts_service = ElevenLabsTTS()

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
            
            # For now, echo back the transcription as TTS
            # TODO: Add OpenAI API call here to generate AI response
            response_text = f"I heard you say: {transcription}"
            
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
