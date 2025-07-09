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
            # Receive message from frontend
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"Received message type: {message.get('type')}")
            
            if message["type"] == "audio_chunk":
                # Store audio chunk for processing
                audio_data = base64.b64decode(message["audio"])
                audio_chunks.append(audio_data)
                logger.info(f"Received audio chunk ({len(audio_data)} bytes)")
                
            elif message["type"] == "end_recording":
                logger.info("Recording ended, processing audio...")
                
                webm_path = None
                wav_path = None
                
                try:
                    # Save audio chunks to temporary WebM file
                    webm_path = audio_processor.save_webm_chunks(audio_chunks)
                    
                    # Convert WebM to WAV using system ffmpeg
                    wav_path = audio_processor.convert_webm_to_wav(webm_path)
                    
                    # Transcribe with Whisper
                    transcription = await transcription_service.transcribe_audio(wav_path)
                    
                    # Send transcription back to frontend
                    await websocket.send_text(json.dumps({
                        "type": "transcription",
                        "text": transcription
                    }))
                    
                    # Send mock audio response chunks (will be replaced with xttx v2 later)
                    mock_audio_chunks = [
                        "mock_audio_chunk_1_base64",
                        "mock_audio_chunk_2_base64", 
                        "mock_audio_chunk_3_base64"
                    ]
                    
                    for chunk in mock_audio_chunks:
                        await websocket.send_text(json.dumps({
                            "type": "audio_chunk",
                            "audio": chunk
                        }))
                    
                    # Signal processing complete
                    await websocket.send_text(json.dumps({
                        "type": "response_complete"
                    }))
                    
                except Exception as e:
                    logger.error(f"Audio processing failed: {e}")
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"Audio processing failed: {str(e)}"
                    }))
                    
                finally:
                    # Clean up temporary files
                    audio_processor.cleanup_files(webm_path, wav_path)
                    audio_chunks.clear()
                
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
