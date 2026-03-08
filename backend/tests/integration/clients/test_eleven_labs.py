#!/usr/bin/env python3

import pytest
from dotenv import load_dotenv

from app.clients.elevan_labs import ElevenLabs
from app.utils import get_or_throw

pytestmark = pytest.mark.skip(
    reason="ElevenLabs integration disabled: paid provider not used"
)


@pytest.fixture
def eleven_labs_client():
    """Create an ElevenLabs client instance"""
    load_dotenv()
    api_key = get_or_throw("ELEVENLABS_TTS_API_KEY")
    if not api_key:
        pytest.skip("ELEVENLABS_API_KEY not found in environment")
    return ElevenLabs(page_size=5, api_key=api_key)


async def test_search_voices_for_english(eleven_labs_client):
    """Test searching for voices with the term 'english'"""
    result = await eleven_labs_client.search_voices(search_term="en")
    assert result is not None


async def test_search_voices_pagination(eleven_labs_client):
    """Test pagination functionality in voice search"""
    # Get first page
    first_page = await eleven_labs_client.search_voices(search_term="en")
    assert first_page is not None
    assert first_page.voices

    # Check if pagination is available
    if first_page.next_page_token and first_page.has_more:
        second_page = await eleven_labs_client.search_voices(
            search_term="en", next_page_token=first_page.next_page_token
        )
        assert second_page is not None
        assert second_page.voices
    else:
        assert (
            False
        ), "Search for 'en' should always return more than 5 voices and have pagination"
