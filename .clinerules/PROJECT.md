# Project Guidelines

This project provides a real-time, voice-based AI character interaction system for tabletop RPGs. Users speak into their mic, and the AI character responds with streamed speech.

## Dependencies

- Vue.js + vite frontend
- FastAPI backend
- Whisper.cpp for transcribing
- OpenAI 4o API for text response generation
- ElevanLab for TTS

## Architecture

- Everything should be streamed in chunks for getting to as close to real time as possible

### Frontend

- Button to start and stop recording audio
- Send audio chunks via websockets
- Receive audio response chunks and play them as they arrive

### Backend

- Websocket to accept audio chunks
- Transcription layer (Whisper)
- Text response generation layer (OpenAI API)
- Audio response generation layer (ElevanLab)
