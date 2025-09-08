from app.clients.elevan_labs import ElevenLabs
from app.clients.google_cloud_tts import GoogleCloudTTS
from app.clients.tts_base import TTSProvider
from app.utils import get_or_throw

GOOGLE_TTS = "google"
ELEVANLABS_TTS = "elevanlabs"
TTS_PROVIDER = get_or_throw("TTS_PROVIDER")


def create_tts_provider(provider: str) -> TTSProvider:
    """Factory function to create TTS provider instances"""

    service = provider if provider else TTS_PROVIDER

    if service == GOOGLE_TTS:
        return GoogleCloudTTS()
    else:
        return ElevenLabs()
