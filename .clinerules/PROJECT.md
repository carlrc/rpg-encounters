# Project Guidelines

This project provides a real-time, voice-based AI character interaction system for tabletop RPGs. Users speak into their mic, and the AI character responds with streamed speech, featuring dynamic character personalities and trust-based interactions.

## Dependencies

- Vue.js + Vite frontend
- FastAPI backend
- Whisper.cpp for speech transcription
- OpenAI GPT-4 API for character response generation
- ElevenLabs for text-to-speech synthesis

## Architecture

- Everything should be streamed in chunks for getting to as close to real time as possible

### Frontend

- Button to start and stop recording audio
- Send audio chunks via WebSockets
- Receive audio response chunks and play them as they arrive
- Character and player selection interface
- Real-time conversation status indicators

### Backend

- WebSocket endpoint for real-time audio streaming (`/conversation/{player_id}/{character_id}`)
- Transcription layer (Whisper.cpp)
- Character agent system with personality-driven responses
- Trust scoring system for dynamic character relationships
- Text response generation layer (OpenAI GPT-4)
- Audio response generation layer (ElevenLabs TTS)
- Character, player, and nugget (trust elements) management
