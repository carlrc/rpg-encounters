from app.clients.elevan_labs import ElevenLabs
from app.clients.google_cloud_tts import GoogleCloudTTS
from app.clients.tts_base import TTSProvider
from app.utils import get_or_throw

GOOGLE_TTS = "google"
ELEVANLABS_TTS = "elevanlabs"
DEFAULT_TTS_PROVIDER = get_or_throw("DEFAULT_TTS_PROVIDER")


def create_tts_provider(
    provider: str, elevenlabs_user_api_key: str | None = None
) -> TTSProvider:
    """Factory function to create TTS provider instances"""

    if provider == ELEVANLABS_TTS and elevenlabs_user_api_key:
        return ElevenLabs(api_key=elevenlabs_user_api_key)
    else:
        return GoogleCloudTTS()
