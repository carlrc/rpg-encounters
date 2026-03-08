import os

from app.clients.elevan_labs import ElevenLabs
from app.clients.google_cloud_tts import GoogleCloudTTS
from app.clients.tts_base import TTSProvider

GOOGLE_TTS = "google"
ELEVANLABS_TTS = "elevanlabs"
GOOGLE_TTS_ENV_VAR = "GOOGLE_CLOUD_TTS_API_KEY"
ELEVENLABS_ENV_VAR = "ELEVENLABS_TTS_API_KEY"
GOOGLE_TTS_API_KEY = os.getenv(GOOGLE_TTS_ENV_VAR)
ELEVENLABS_API_KEY = os.getenv(ELEVENLABS_ENV_VAR)


def is_google_tts_enabled() -> bool:
    """Return True if Google TTS is available for the current user/context."""
    return bool(GOOGLE_TTS_API_KEY)


def is_elevenlabs_enabled() -> bool:
    """Return True if ElevenLabs is available for the current user/context."""
    return bool(ELEVENLABS_API_KEY)


def get_available_tts_providers() -> list[str]:
    providers = []
    if is_google_tts_enabled():
        providers.append(GOOGLE_TTS)
    if is_elevenlabs_enabled():
        providers.append(ELEVANLABS_TTS)
    return providers


def create_tts_provider(provider: str) -> TTSProvider:
    """Factory function to create TTS provider instances"""

    if provider == GOOGLE_TTS:
        if not GOOGLE_TTS_API_KEY:
            raise RuntimeError(
                "GOOGLE_CLOUD_TTS_API_KEY is required to use Google TTS."
            )
        return GoogleCloudTTS()

    if provider == ELEVANLABS_TTS:
        if not ELEVENLABS_API_KEY:
            raise RuntimeError(
                "ELEVENLABS_TTS_API_KEY is required to use ElevenLabs TTS."
            )
        return ElevenLabs(api_key=ELEVENLABS_API_KEY)

    raise RuntimeError(f"Unsupported TTS provider: {provider}")
