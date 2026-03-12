# Backend Agents File

## Transcription

- `TRANSCRIPTION_POOL_SIZE` controls how many `WhisperTranscriptionService` instances are created in `_get_transcription_pool()`. Each instance loads its own Whisper model, so loaded models per backend process are `TRANSCRIPTION_POOL_SIZE`.
- `@lru_cache(maxsize=1)` caches one pool object (the list returned by `_get_transcription_pool()`), not one model. If `TRANSCRIPTION_POOL_SIZE=4`, the single cached pool contains 4 loaded model instances.
- Pool/model creation is lazy: models are loaded on the first call path that needs transcription, not at FastAPI startup.
- `get_transcription_service()` chooses a random service from the cached pool for each transcription request.
- Loaded models persist in memory for the lifetime of the backend process (until process restart or explicit cache clear, which is not used here).
