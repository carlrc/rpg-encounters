import os
from unittest.mock import AsyncMock

from app.agents.conversations.conversation_agent import (
    ConversationAgent,
    ConversationAgentDeps,
)
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.agents.prompts.import_prompts import render_prompt, render_prompt_section
from app.models.influence import BASE_INFLUENCE_MAX
from app.models.reveal import RevealLayer
from app.services.context import ConvoContext
from tests.fixtures.generate import (
    default_character,
    default_encounter,
    default_influence,
    default_player,
)

# Use default fixtures with modifications for this test scenario
CHARACTER = default_character()
PLAYER = default_player()
INFLUENCE_STATE = default_influence(base=BASE_INFLUENCE_MAX)

TEST_DB_URL = os.getenv("TEST_DATABASE_URL")
CONVERSATION_STORE = AsyncMock()

CONTEXT = ConvoContext(
    encounter=default_encounter(),
    influence=INFLUENCE_STATE,
    reveals=[],  # No reveals for this test
    memories=[],  # No memories for this test
    messages=None,
    player=PLAYER,
    character=CHARACTER,
)

DEPENDENCIES = ConversationAgentDeps(
    player=PLAYER,
    character=CHARACTER,
    context=CONTEXT,
    user_id=1,
    telemetry=lambda: None,
)

BASE_TEMPLATE_CONTEXT = {
    "max_response_length": 30,
    "character": CHARACTER,
    "memories": [],
    "reveals": [],
    "player": PLAYER,
    "encounter": CONTEXT.encounter,
}

RENDERED_SYSTEM_PROMPT = render_prompt("conversation_agent", BASE_TEMPLATE_CONTEXT)
RENDERED_INSTRUCTIONS = render_prompt_section("memories_reveals", BASE_TEMPLATE_CONTEXT)


async def test_agent_handles_no_reveals():
    agent = ConversationAgent(
        system_prompt=RENDERED_SYSTEM_PROMPT,
        instructions=RENDERED_INSTRUCTIONS,
        conversation_store=CONVERSATION_STORE,
        influence_calculator_agent=InfluenceCalculatorAgent(
            system_prompt=render_prompt(
                "influence_scoring_agent",
                {
                    "character": CHARACTER,
                    "player": PLAYER,
                    "encounter": CONTEXT.encounter,
                },
            )
        ),
    )

    _, level, _ = await agent.chat(
        player_transcript="Hi there, I'm wondering if you have any rooms available tonight?",
        deps=DEPENDENCIES,
    )
    # No reveals linked to character should result in standard response
    assert level == RevealLayer.STANDARD
