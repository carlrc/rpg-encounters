from unittest.mock import Mock

import pytest

from app.services.transcription import TranscriptionError, WhisperTranscriptionService


@pytest.mark.asyncio
async def test_transcribe_audio_missing_file_raises_transcription_error(monkeypatch):
    monkeypatch.setattr(WhisperTranscriptionService, "_load_model", lambda self: None)
    service = WhisperTranscriptionService()
    service.model = Mock()
    monkeypatch.setattr("app.services.transcription.os.path.exists", lambda _path: False)

    with pytest.raises(TranscriptionError, match="Transcription failed"):
        await service.transcribe_audio("missing.wav")
