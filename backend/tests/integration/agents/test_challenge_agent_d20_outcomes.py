from app.agents.challenge_agent import ChallengeAgent, ChallengeAgentDeps
from app.agents.prompts.import_prompts import render_prompt, render_prompt_section
from app.agents.prompts.limits import (
    MAX_RESPONSE_WORD_LENGTH,
    STANDARD_RESPONSE_WORD_LENGTH,
)
from app.models.memory import Memory
from tests.fixtures.generate import (
    REVEAL_LEVEL_3,
    default_character,
    default_encounter,
    default_memories,
    default_player,
)
from tests.utilities import (
    assert_contains_any_keywords,
    assert_does_not_contain_keywords,
)

SECRET_CORRIDOR = REVEAL_LEVEL_3
MAYOR_SECRET = "The mayor used to bring foreign diplomats to this secret suite without his wife knowing."

# Use default fixtures
CHARACTER = default_character()
PLAYER = default_player()

ALL_MEMORIES = [
    *default_memories(),
    Memory(
        id=2,
        title="Old Mayors favourite room",
        character_ids=[CHARACTER.id],
        content="The old mayor used to love staying in the inn.",
    ),
]

ENCOUNTER = default_encounter()

DEPENDENCIES = ChallengeAgentDeps(
    encounter=ENCOUNTER, messages=None, telemetry=lambda: None
)

BASE_TEMPLATE_CONTEXT = {
    "character": CHARACTER,
    "player": PLAYER,
    "memories": ALL_MEMORIES,
    "encounter": ENCOUNTER,
}


async def test_challenge_agent_standard():
    """Test that standard challenge response"""
    template_context = {
        **BASE_TEMPLATE_CONTEXT,
        "filtered_reveals": [MAYOR_SECRET],
        "max_response_length": STANDARD_RESPONSE_WORD_LENGTH,
        "d20_roll": 15,
    }
    rendered_prompt = render_prompt("challenge_agent", template_context)
    rendered_instructions = render_prompt_section(
        "memories_filtered_reveals", template_context
    )
    agent = ChallengeAgent(
        system_prompt=rendered_prompt, instructions=rendered_instructions
    )

    response = await agent.chat(
        player_transcript="I want to know everything about your inn",
        deps=DEPENDENCIES,
    )

    assert_contains_any_keywords(text=response, keywords=["mayor", "oldest"])


async def test_challenge_agent_critical_success():
    """Test that critical success (d20=20) produces enthusiastic response with maximum information"""
    template_context = {
        **BASE_TEMPLATE_CONTEXT,
        "filtered_reveals": [SECRET_CORRIDOR, MAYOR_SECRET],
        "max_response_length": MAX_RESPONSE_WORD_LENGTH,
    }
    rendered_prompt = render_prompt(
        "challenge_agent_critical_success", template_context
    )
    rendered_instructions = render_prompt_section(
        "memories_filtered_reveals", template_context
    )
    agent = ChallengeAgent(
        system_prompt=rendered_prompt, instructions=rendered_instructions
    )

    response = await agent.chat(
        player_transcript="I want to know everything about your inn",
        deps=DEPENDENCIES,
    )

    assert_contains_any_keywords(
        text=response, keywords=["secret", "corridor", "diplomats"]
    )


async def test_challenge_agent_critical_failure():
    """Test that critical failure (d20=1) produces hostile response with no information"""
    rendered_prompt = render_prompt(
        "challenge_agent_critical_failure",
        {**BASE_TEMPLATE_CONTEXT, "max_response_length": 40},
    )
    agent = ChallengeAgent(system_prompt=rendered_prompt)

    response = await agent.chat(
        player_transcript="I want to know everything about your inn",
        deps=DEPENDENCIES,
    )

    # TODO: How to assert against negativity?
    # Assert does not give up memories
    assert_does_not_contain_keywords(response, ["mayor", "oldest"])
