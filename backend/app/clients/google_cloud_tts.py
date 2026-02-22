import logging
from typing import AsyncGenerator

from google.cloud import texttospeech

from app.clients.tts_base import TTSProvider, Voice, VoiceLabels, VoicesResponse
from app.services.audio_processor import convert_ogg_to_mp4_stream
from app.utils import get_or_throw

logger = logging.getLogger(__name__)


class GoogleCloudTTS(TTSProvider):
    def __init__(self):
        super().__init__()
        self.client = texttospeech.TextToSpeechAsyncClient(
            client_options={"api_key": get_or_throw("GOOGLE_CLOUD_TTS_API_KEY")}
        )

    async def text_to_speech_stream(self, text: str, voice_id: str):
        """Stream speech audio chunks for text using the selected Google voice."""
        # See https://cloud.google.com/text-to-speech/docs/voices for available voices.
        streaming_config = texttospeech.StreamingSynthesizeConfig(
            voice=texttospeech.VoiceSelectionParams(name=voice_id),
            # https://cloud.google.com/text-to-speech/docs/reference/rest/Shared.Types/StreamingAudioConfig
            # Streaming supports PCM, ALAW, MULAW and OGG_OPUS. All other encodings return an error.
            streaming_audio_config=texttospeech.StreamingAudioConfig(
                audio_encoding=texttospeech.AudioEncoding.OGG_OPUS
            ),
        )

        config_request = texttospeech.StreamingSynthesizeRequest(
            streaming_config=streaming_config
        )

        # Must be bidirectional streaming
        async def request_generator():
            yield config_request
            for item in [text]:
                yield texttospeech.StreamingSynthesizeRequest(
                    input=texttospeech.StreamingSynthesisInput(text=item)
                )

        try:
            streaming_responses = await self.client.streaming_synthesize(
                request_generator()
            )

            async for response in streaming_responses:
                yield response.audio_content
        except Exception as e:
            logger.error(f"Google Cloud TTS error: {e}")
            raise

    async def text_to_speech_mp4_stream(
        self, text: str, voice_id: str
    ) -> AsyncGenerator[bytes, None]:
        """Stream text-to-speech audio chunks converted to MP4 format"""
        async for mp4_chunk in convert_ogg_to_mp4_stream(
            tts_provider=self, text=text, voice_id=voice_id
        ):
            yield mp4_chunk

    async def search_voices(self, search_term: str, next_page_token: str | None = None):
        request = texttospeech.ListVoicesRequest(language_code=search_term)
        response = await self.client.list_voices(request=request)

        # TODO: Issue where GCP TTS won't accept names, which are returned in this list, without multiple additional prefixes added
        # Filtering by names which can be used as is for simplicity
        filtered_voices = []

        for voice in response.voices:
            if "chirp3-hd" in voice.name.lower():
                filtered_voices.append(
                    Voice(
                        voice_id=voice.name,
                        # Assume its in the format of en-AU-Chirp3-HD-Achernar
                        name=voice.name.split("-")[-1],
                        description=None,
                        category="HD",
                        labels=VoiceLabels(
                            gender=voice.ssml_gender.name,
                            language=voice.language_codes[0],
                        ),
                    )
                )

        return VoicesResponse(
            voices=filtered_voices,
            total_count=len(filtered_voices),
            has_more=False,
            next_page_token=None,
        )
