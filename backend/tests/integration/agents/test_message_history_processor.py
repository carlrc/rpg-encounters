from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, ToolReturnPart

from app.agents.base_agent import (
    MAX_MESSAGE_HISTORY,
    BaseAgent,
    get_latest_user_message,
)

AGENT = BaseAgent()


def create_message_history(num_pairs: int):
    """Create a list of alternating user and assistant messages."""
    messages = []
    for i in range(num_pairs):
        # User message
        user_message = ModelRequest.user_text_prompt(f"User message {i + 1}")
        messages.append(user_message)

        # Assistant response
        assistant_response = ModelResponse(
            parts=[TextPart(content=f"Assistant response {i + 1}")]
        )
        messages.append(assistant_response)

    return messages


async def test_message_history_processor_keeps_all_when_below_limit():
    """Test that the message history processor keeps all messages when below MAX_MESSAGE_HISTORY."""
    few_messages = create_message_history(5)  # 10 messages total
    result = await AGENT._keep_recent_messages(few_messages)

    assert len(result) == 10
    assert result == few_messages


async def test_message_history_processor_keeps_all_when_at_limit():
    """Test that the message history processor keeps all messages when at MAX_MESSAGE_HISTORY."""
    exact_messages = create_message_history(
        MAX_MESSAGE_HISTORY // 2
    )  # Exactly MAX_MESSAGE_HISTORY messages
    result = await AGENT._keep_recent_messages(exact_messages)

    assert len(result) == MAX_MESSAGE_HISTORY
    assert result == exact_messages


async def test_message_history_processor_trims_when_exceeding_limit():
    """Test that the message history processor trims to last N messages when exceeding MAX_MESSAGE_HISTORY."""

    excess_message_pairs = (
        MAX_MESSAGE_HISTORY + 10
    ) // 2  # Create more than MAX_MESSAGE_HISTORY messages
    excess_messages = create_message_history(excess_message_pairs)
    result = await AGENT._keep_recent_messages(excess_messages)

    # Should return only the last MAX_MESSAGE_HISTORY messages
    assert len(result) == MAX_MESSAGE_HISTORY
    assert result == excess_messages[-MAX_MESSAGE_HISTORY:]


async def test_message_history_processor_keeps_all_when_tool_return_at_boundary():
    """Test that the message history processor keeps all messages when a ToolReturnPart is at the trimming boundary."""

    # Create more messages than the limit
    excess_message_pairs = (MAX_MESSAGE_HISTORY + 10) // 2
    excess_messages = create_message_history(excess_message_pairs)

    # Add a ToolReturnPart to the message that would be at the trimming boundary
    boundary_index = len(excess_messages) - MAX_MESSAGE_HISTORY
    tool_return_part = ToolReturnPart(
        tool_name="test_tool", content="tool result", tool_call_id="call_123"
    )
    excess_messages[boundary_index] = ModelResponse(parts=[tool_return_part])

    result = await AGENT._keep_recent_messages(excess_messages)

    # Should return ALL messages because there's a ToolReturnPart at the boundary
    assert len(result) == len(excess_messages)
    assert result == excess_messages


async def test_message_history_processor_handles_empty_messages():
    """Test that the message history processor handles empty message lists gracefully."""
    base_agent = BaseAgent()

    empty_messages = []
    result = await base_agent._keep_recent_messages(empty_messages)

    assert len(result) == 0
    assert result == []


async def test_agent_new_messages_with_history_processor():
    """Test that latest user message is available after history processing."""

    base_agent = BaseAgent()

    # Create the actual pydantic-ai Agent with our history processor
    agent = base_agent._generate_agent(
        system_prompt="You are a test agent. Respond with 'OK'.",
        output_type=str,
    )

    # Create a message history that exceeds MAX_MESSAGE_HISTORY
    excess_message_pairs = (MAX_MESSAGE_HISTORY + 10) // 2
    initial_messages = create_message_history(excess_message_pairs)

    # Run the agent with the excessive message history
    # This should trigger the history processor to trim messages
    run_result = await agent.run(
        user_prompt="Test message", message_history=initial_messages
    )

    new_message = get_latest_user_message(run_result=run_result)

    assert new_message
    assert new_message.parts[0].content == "Test message"
