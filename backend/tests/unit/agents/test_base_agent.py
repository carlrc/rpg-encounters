from unittest.mock import Mock

import pytest
from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, UserPromptPart

from app.agents.base_agent import get_latest_user_message


def test_get_latest_user_message_happy_path():
    """Test get_latest_user_message returns first new message when available."""
    # Mock run result with new_messages() returning data
    run_result = Mock()

    # Create a mock user message
    user_message = ModelRequest(
        parts=[UserPromptPart(content="Hello", timestamp=None)], kind="request"
    )

    run_result.new_messages.return_value = [user_message]

    result = get_latest_user_message(run_result)

    assert result == user_message
    run_result.new_messages.assert_called_once()


def test_get_latest_user_message_fallback_path():
    """Test get_latest_user_message falls back to all_messages when new_messages is empty."""
    # Mock run result with empty new_messages but valid all_messages
    run_result = Mock()
    run_result.new_messages.return_value = []

    # Create mock messages - system message and user message
    system_message = ModelResponse(
        parts=[TextPart(content="System message")], kind="response"
    )

    user_message = ModelRequest(
        parts=[UserPromptPart(content="Hello", timestamp=None)], kind="request"
    )

    run_result.all_messages.return_value = [system_message, user_message]

    result = get_latest_user_message(run_result)

    assert result == user_message
    run_result.new_messages.assert_called_once()
    run_result.all_messages.assert_called_once()


def test_get_latest_user_message_multiple_user_messages():
    """Test get_latest_user_message returns most recent user message from all_messages."""
    run_result = Mock()
    run_result.new_messages.return_value = []

    # Create multiple user messages - should return the most recent (last) one
    older_user_message = ModelRequest(
        parts=[UserPromptPart(content="First message", timestamp=None)], kind="request"
    )

    newer_user_message = ModelRequest(
        parts=[UserPromptPart(content="Second message", timestamp=None)], kind="request"
    )

    system_message = ModelResponse(
        parts=[TextPart(content="System response")], kind="response"
    )

    run_result.all_messages.return_value = [
        older_user_message,
        system_message,
        newer_user_message,
    ]

    result = get_latest_user_message(run_result)

    assert result == newer_user_message
    assert result.parts[0].content == "Second message"


def test_get_latest_user_message_no_user_messages():
    """Test get_latest_user_message raises ValueError when no user messages exist."""
    run_result = Mock()
    run_result.new_messages.return_value = []

    # Only system messages, no user messages
    system_message = ModelResponse(
        parts=[TextPart(content="System message")], kind="response"
    )

    run_result.all_messages.return_value = [system_message]

    with pytest.raises(ValueError, match="No user message found in message history"):
        get_latest_user_message(run_result)


def test_get_latest_user_message_empty_history():
    """Test get_latest_user_message raises ValueError when message history is empty."""
    run_result = Mock()
    run_result.new_messages.return_value = []
    run_result.all_messages.return_value = []

    with pytest.raises(ValueError, match="No user message found in message history"):
        get_latest_user_message(run_result)


def test_get_latest_user_message_non_user_request():
    """Test get_latest_user_message ignores ModelRequest without UserPromptPart."""
    run_result = Mock()
    run_result.new_messages.return_value = []

    # Create a ModelRequest that doesn't have UserPromptPart
    non_user_request = ModelRequest(
        parts=[TextPart(content="System request")], kind="request"
    )

    user_request = ModelRequest(
        parts=[UserPromptPart(content="User message", timestamp=None)], kind="request"
    )

    run_result.all_messages.return_value = [non_user_request, user_request]

    result = get_latest_user_message(run_result)

    assert result == user_request
