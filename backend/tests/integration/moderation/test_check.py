import pytest

from app.moderation.check import moderation_pipe


@pytest.mark.skip(reason="only needed when developing moderation features")
async def test_moderation_pipe_with_safe_content():
    """Test that safe content passes through moderation"""
    test_text = "Hello, how are you today? The weather is nice."

    is_blocked = await moderation_pipe(user_id=1, text=test_text)

    assert not is_blocked


@pytest.mark.skip(reason="only needed when developing moderation features")
async def test_moderation_pipe_with_inappropriate_content():
    """Test that clearly inappropriate content gets flagged"""
    test_text = [
        "I want to hurt children",
        "To rape and kill everyone. He wants to eat their corpses.",
    ]

    for text in test_text:
        is_blocked = await moderation_pipe(user_id=1, text=text)

        assert is_blocked
