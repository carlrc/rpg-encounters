from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
import uvicorn
import base64
from app.services.audio_processor import AudioProcessor
from app.services.transcription import WhisperTranscriptionService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="D&D AI Character Backend")

# Initialize services
audio_processor = AudioProcessor()
transcription_service = WhisperTranscriptionService(model_size="base")

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
    logger.info("WebSocket connection established")
    
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
                logger.info(f"Received binary audio chunk ({len(audio_data)} bytes)")
                
            elif "text" in message:
                # Text control signal
                if message["text"] == "END":
                    logger.info("Received END signal, processing accumulated audio...")
                    break
                else:
                    logger.info(f"Received text message: {message['text']}")
                
    except WebSocketDisconnect:
        logger.error("WebSocket connection closed unexpectedly")
        raise

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()
        raise
    
    # Process accumulated audio chunks
    if audio_chunks:
        wav_path = None
        
        try:
            # Save audio chunks directly to WAV file using ffmpeg
            wav_path = audio_processor.save_chunks_to_wav(audio_chunks)
            
            # Transcribe with Whisper
            transcription = await transcription_service.transcribe_audio(wav_path)
            logger.info(f"Transcription: {transcription}")
            
            # TODO: In a real implementation, you would:
            # 1. Generate text response using OpenAI API
            # 2. Generate audio response using xttx v2
            # 3. Send response back via a new WebSocket connection or other mechanism
            
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            
        finally:
            # Clean up temporary files
            audio_processor.cleanup_files(wav_path)
    
    await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
