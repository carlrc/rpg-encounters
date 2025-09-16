from unittest.mock import AsyncMock

from app.agents.conversations.negative_conversation_agent import (
    NegativeConvoAgent,
    NegativeConvoAgentDeps,
)
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.agents.prompts.import_prompts import render_prompt
from app.agents.prompts.limits import MAX_RESPONSE_WORD_LENGTH
from app.models.influence import BASE_INFLUENCE_MIN
from app.services.context import ConvoContext
from app.utils import get_or_throw
from tests.fixtures.generate import (
    default_character,
    default_encounter,
    default_influence,
    default_memories,
    default_player,
)

# Use default fixtures with modifications for negative test scenario
CHARACTER = default_character()
PLAYER = default_player()
ALL_MEMORIES = default_memories()
INFLUENCE_STATE = default_influence(base=BASE_INFLUENCE_MIN)

CONTEXT = ConvoContext(
    encounter=default_encounter(),
    influence=INFLUENCE_STATE,
    reveals=[],  # No reveals for this test
    memories=ALL_MEMORIES,
    messages=None,
    player=PLAYER,
    character=CHARACTER,
    elevenlabs_token=None,
)

DEPENDENCIES = NegativeConvoAgentDeps(
    context=CONTEXT,
    user_id=1,
    telemetry=lambda: None,
)

BASE_TEMPLATE_CONTEXT = {
    "max_response_length": MAX_RESPONSE_WORD_LENGTH,
    "character": CHARACTER,
    "memories": ALL_MEMORIES,
    "player": PLAYER,
    "encounter": CONTEXT.encounter,
}

RENDERED_SYSTEM_PROMPT = render_prompt(
    "negative_conversation_agent", BASE_TEMPLATE_CONTEXT
)

TEST_DB_URL = get_or_throw("TEST_DATABASE_URL")
CONVERSATION_STORE = AsyncMock()


async def test_negative_agent_is_negative():
    agent = NegativeConvoAgent(
        system_prompt=RENDERED_SYSTEM_PROMPT,
        conversation_store=CONVERSATION_STORE,
        influence_calculator_agent=InfluenceCalculatorAgent(
            system_prompt=render_prompt(
                "influence_scoring_agent",
                {
                    "character": CHARACTER,
                    "player": PLAYER,
                    "encounter": CONTEXT.encounter,
                },
            ),
        ),
    )

    response, influence = await agent.chat(
        player_transcript="Hello, how are you?",
        deps=DEPENDENCIES,
    )
    # Bias with max base influence and basic inquiry should only result in standard level
    assert response is not None
    assert influence.score < 0
