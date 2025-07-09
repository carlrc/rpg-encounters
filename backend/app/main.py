from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
import uvicorn

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="D&D AI Character Backend")

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
    
    try:
        while True:
            # Receive message from frontend
            data = await websocket.receive_text()
            message = json.loads(data)
            
            logger.info(f"Received message type: {message.get('type')}")
            
            if message["type"] == "audio_chunk":
                # For now, just acknowledge receipt of audio chunk
                logger.info("Received audio chunk")
                # In the future, this will be sent to Whisper for transcription
                
            elif message["type"] == "end_recording":
                logger.info("Recording ended, processing audio...")
                
                # Send mock transcription
                await websocket.send_text(json.dumps({
                    "type": "transcription",
                    "text": "Hello, I heard your message!"
                }))
                
                # Send mock audio response chunks
                # In the future, this will come from xttx v2
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
                
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
