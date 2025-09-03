from app.clients.google_cloud_tts import GoogleCloudTTS


async def test_gcloud_tts_streaming():
    response_count = 0
    async for audio_chunk in GoogleCloudTTS().text_to_speech_stream(
        text="test on how the google api actually works!",
        voice_id="en-AU-Chirp3-HD-Achernar",
    ):
        response_count += 1
        assert audio_chunk is not None

    assert response_count != 0


async def test_list_voices():
    response = await GoogleCloudTTS().search_voices("en")

    assert len(response) > 10
