import logging
import os

from google.cloud import texttospeech

logger = logging.getLogger(__name__)


class GoogleCloudTTS:
    def __init__(self, page_size: int = 15):
        self.page_size = page_size
        self.client = texttospeech.TextToSpeechClient(
            client_options={"api_key": os.getenv("GOOGLE_CLOUD_TTS_API_KEY")}
        )

    def text_to_speech_stream(self, text: str):
        # See https://cloud.google.com/text-to-speech/docs/voices for all voices.
        streaming_config = texttospeech.StreamingSynthesizeConfig(
            voice=texttospeech.VoiceSelectionParams(
                name="en-US-Chirp3-HD-Charon",
                language_code="en-US",
            ),
            # https://cloud.google.com/text-to-speech/docs/reference/rest/Shared.Types/StreamingAudioConfig
            # Streaming supports PCM, ALAW, MULAW and OGG_OPUS. All other encodings return an error.
            streaming_audio_config=texttospeech.StreamingAudioConfig(
                audio_encoding=texttospeech.AudioEncoding.OGG_OPUS
            ),
        )

        config_request = texttospeech.StreamingSynthesizeRequest(
            streaming_config=streaming_config
        )

        text_iterator = [text]

        def request_generator():
            yield config_request
            for item in text_iterator:
                yield texttospeech.StreamingSynthesizeRequest(
                    input=texttospeech.StreamingSynthesisInput(text=item)
                )

        try:
            streaming_responses = self.client.streaming_synthesize(request_generator())

            for response in streaming_responses:
                yield response
        except Exception as e:
            logger.error(f"Google Cloud TTS error: {e}")
            raise
