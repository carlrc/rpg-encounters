import os
from unittest.mock import Mock

import pytest
from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart

from app.agents.base_agent import MAX_MESSAGE_HISTORY
from app.agents.conversations.negative_conversation_agent import (
    NegativeConvoAgent,
    NegativeConvoAgentDeps,
)
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.agents.prompts.import_prompts import render_prompt
from app.models.influence import BASE_INFLUENCE_MIN
from tests.fixtures.generate import (
    default_character,
    default_encounter,
    default_influence,
    default_memories,
    default_player,
)

# Use default fixtures
CHARACTER = default_character()
PLAYER = default_player()
ALL_MEMORIES = default_memories()
INFLUENCE_STATE = default_influence(base=BASE_INFLUENCE_MIN)
ENCOUNTER = default_encounter()

TEST_DB_URL = os.getenv("TEST_DATABASE_URL")
CONVERSATION_STORE = Mock()


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


# TODO: This test was for debugging an issue. This will be adjusted once proper summaries are applied vs trimming message history
@pytest.mark.skip(reason="proper context summaries are required for this to be useful")
async def test_message_history_processor_trims_at_max_limit():
    """Test that the message history processor trims messages when exceeding MAX_MESSAGE_HISTORY."""

    # Template context for rendering Jinja prompt
    template_context = {
        "max_response_length": 30,
        "character": CHARACTER,
        "memories": ALL_MEMORIES,
        "player": PLAYER,
        "encounter": ENCOUNTER,
    }

    rendered_system_prompt = render_prompt(
        "negative_conversation_agent", template_context
    )

    agent = NegativeConvoAgent(
        system_prompt=rendered_system_prompt,
        conversation_store=CONVERSATION_STORE,
        influence_calculator_agent=InfluenceCalculatorAgent(
            system_prompt=render_prompt(
                "influence_scoring_agent",
                {"character": CHARACTER, "player": PLAYER, "encounter": ENCOUNTER},
            ),
            character=CHARACTER,
            player=PLAYER,
        ),
    )

    # Create message history with MAX_MESSAGE_HISTORY - 2 messages (18 messages = 9 pairs)
    # This leaves room for 2 more messages (1 user + 1 assistant) to reach the limit
    initial_message_count = MAX_MESSAGE_HISTORY
    message_pairs = initial_message_count // 2
    initial_messages = create_message_history(message_pairs)

    # Create context and dependencies with the initial message history
    from app.services.context import ConvoContext

    context = ConvoContext(
        encounter=ENCOUNTER,
        influence=INFLUENCE_STATE,
        reveals=[],
        memories=ALL_MEMORIES,
        messages=initial_messages,
    )

    deps = NegativeConvoAgentDeps(
        player=PLAYER,
        character=CHARACTER,
        context=context,
        user_id=1,
        telemetry=lambda: None,
    )

    # Make a chat call - this should add 2 more messages (user + assistant) to reach MAX_MESSAGE_HISTORY
    response, influence = await agent.chat(
        player_transcript="This should bring us to the max limit",
        deps=deps,
    )

    # Verify the response was generated
    assert response is not None
    assert influence is not None

    # Get the messages that were added to the store
    call_args = CONVERSATION_STORE.add_messages.call_args
    new_messages = call_args.kwargs["new_messages"]

    # Should have added exactly 2 messages (user request + assistant response)
    assert len(new_messages) == 2
    assert new_messages[0].content == "This should bring us to the max limit"
