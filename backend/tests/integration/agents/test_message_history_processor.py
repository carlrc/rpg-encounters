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
from app.agents.prompts.import_prompts import import_system_prompt
from app.models.alignment import Alignment
from app.models.character import Character
from app.models.class_traits import Abilities, Class, Skills
from app.models.encounter import Encounter
from app.models.influence import BASE_INFLUENCE_MIN, Influence
from app.models.memory import Memory
from app.models.player import Player
from app.models.race import Gender, Race, Size
from app.models.reveal import DifficultyClass

CHARACTER = Character(
    id=100,
    name="Bingo Bracegirdle",
    race=Race.LIGHTFOOT_HALFLING.value,
    size=Size.SMALL.value,
    alignment=Alignment.NEUTRAL_GOOD.value,
    gender=Gender.MALE.value,
    profession="Inn Owner",
    background="Friendly Inn keeper. Knows everyone in town and all the local gossip.",
    communication_style="Chatty and welcoming, always ready with a story or bit of news.",
    motivation="To keep the tavern running smoothly, keep customers happy and make money.",
    personality="Appreciates friendly conversation and local gossip sharing.",
    race_preferences={Race.LIGHTFOOT_HALFLING.value: DifficultyClass.VERY_EASY.value},
    class_preferences={Class.BARD.value: DifficultyClass.VERY_EASY.value},
    gender_preferences={Gender.FEMALE.value: DifficultyClass.VERY_EASY.value},
    size_preferences={Size.SMALL.value: DifficultyClass.VERY_EASY.value},
)

PLAYER = Player(
    id=100,
    name="Wondering Bard",
    appearance="A small women with long brown hair with strong cheek bones.",
    race=Race.LIGHTFOOT_HALFLING.value,
    class_name=Class.BARD.value,
    size=Size.SMALL.value,
    alignment=Alignment.NEUTRAL_GOOD.value,
    gender=Gender.FEMALE.value,
    abilities={Abilities.CHARISMA.value: 16},
    skills={
        Skills.PERSUASION.value: 5,
        Skills.DECEPTION.value: 2,
        Skills.INTIMIDATION.value: 3,
        Skills.PERFORMANCE.value: 4,
    },
)

CHAR_SYSTEM_PROMPT = import_system_prompt("negative_conversation_agent")
SCORE_SYSTEM_PROMPT = import_system_prompt("influence_scoring_agent")

ALL_MEMORIES = [
    Memory(
        id=1,
        title="Oldest Inn",
        character_ids=[CHARACTER.id],
        content="This inn is the oldest in the city.",
    )
]

INFLUENCE_STATE = Influence(
    character_id=CHARACTER.id,
    player_id=PLAYER.id,
    base=BASE_INFLUENCE_MIN,
    earned=0,
)

ENCOUNTER = Encounter(
    id=1,
    name="test",
    description="test",
    position_x=0.1,
    position_y=0.2,
    character_ids=[CHARACTER.id],
)

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
    agent = NegativeConvoAgent(
        character=CHARACTER,
        player=PLAYER,
        system_prompt=CHAR_SYSTEM_PROMPT,
        conversation_store=CONVERSATION_STORE,
        influence_calculator_agent=InfluenceCalculatorAgent(
            system_prompt=SCORE_SYSTEM_PROMPT, character=CHARACTER, player=PLAYER
        ),
        memories=ALL_MEMORIES,
    )

    # Create message history with MAX_MESSAGE_HISTORY - 2 messages (18 messages = 9 pairs)
    # This leaves room for 2 more messages (1 user + 1 assistant) to reach the limit
    initial_message_count = MAX_MESSAGE_HISTORY
    message_pairs = initial_message_count // 2
    initial_messages = create_message_history(message_pairs)

    # Create dependencies with the initial message history
    deps = NegativeConvoAgentDeps(
        encounter=ENCOUNTER,
        influence=INFLUENCE_STATE,
        message_history=initial_messages,
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
