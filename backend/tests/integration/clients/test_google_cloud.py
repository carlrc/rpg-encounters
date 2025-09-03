from app.clients.google_cloud_tts import GoogleCloudTTS


def test_gcloud_tts_streaming():
    response_count = 0
    for audio_chunk in GoogleCloudTTS().text_to_speech_stream(
        "test on how the google api actually works!"
    ):
        response_count += 1
        assert audio_chunk is not None

    assert response_count != 0
