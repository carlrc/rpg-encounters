from app.clients.google_cloud_tts import GoogleCloudTTS


async def test_gcloud_tts_streaming():
    response_count = 0
    async for audio_chunk in GoogleCloudTTS().text_to_speech_stream(
        "test on how the google api actually works!"
    ):
        response_count += 1
        assert audio_chunk is not None

    assert response_count != 0


async def test_list_voices():
    responses = await GoogleCloudTTS().search_voices("en")

    for response in responses.voices:
        assert response is not None
