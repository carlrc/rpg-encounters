from app.services.ability_challenge import D20Outcomes
from app.services.challenge import render_challenge_prompts
from app.services.context import ConvoContext
from tests.fixtures.generate import (
    REVEAL_LEVEL_1,
    default_character,
    default_encounter,
    default_influence,
    default_memories,
    default_player,
    default_reveals,
)

# Use default fixtures
CHARACTER = default_character()
PLAYER = default_player()
ALL_REVEALS = default_reveals()
ALL_MEMORIES = default_memories()
INFLUENCE_STATE = default_influence()

CONTEXT = ConvoContext(
    encounter=default_encounter(),
    influence=INFLUENCE_STATE,
    reveals=ALL_REVEALS,
    memories=ALL_MEMORIES,
    messages=None,
    player=PLAYER,
    character=CHARACTER,
    elevenlabs_token=None,
)


def test_render_challenge_prompts_standard():
    rendered = render_challenge_prompts(
        ctx=CONTEXT,
        d20_roll=10,
        filtered_reveals=[REVEAL_LEVEL_1],
        total_roll=10,
    )

    assert "# Ability Check Agent" in rendered
    assert "# Ability Check Critical Success Agent" not in rendered
    assert "# Ability Check Critical Failure Agent" not in rendered
    assert "### Memories" in rendered
    assert "### Reveals" in rendered
    assert ALL_MEMORIES[0].content in rendered
    assert REVEAL_LEVEL_1 in rendered


def test_render_challenge_prompts_critical_success():
    rendered = render_challenge_prompts(
        ctx=CONTEXT,
        d20_roll=D20Outcomes.CRITICAL_SUCCESS.value,
        filtered_reveals=[REVEAL_LEVEL_1],
        total_roll=25,
    )

    assert "# Ability Check Critical Success Agent" in rendered
    assert "# Ability Check Agent" not in rendered
    assert "# Ability Check Critical Failure Agent" not in rendered
    assert "### Memories" in rendered
    assert "### Reveals" in rendered
    assert ALL_MEMORIES[0].content in rendered
    assert REVEAL_LEVEL_1 in rendered


def test_render_challenge_prompts_critical_failure():
    rendered = render_challenge_prompts(
        ctx=CONTEXT,
        d20_roll=D20Outcomes.CRITICAL_FAILURE.value,
        filtered_reveals=[REVEAL_LEVEL_1],
        total_roll=1,
    )

    assert "# Ability Check Critical Failure Agent" in rendered
    assert "# Ability Check Agent" not in rendered
    assert "# Ability Check Critical Success Agent" not in rendered
    assert "### Memories" not in rendered
    assert "### Reveals" not in rendered
    assert ALL_MEMORIES[0].content not in rendered
    assert REVEAL_LEVEL_1 not in rendered


def test_render_challenge_prompts_negative_total_roll():
    rendered = render_challenge_prompts(
        ctx=CONTEXT,
        d20_roll=10,
        filtered_reveals=[REVEAL_LEVEL_1],
        total_roll=-1,
    )

    assert "# Ability Check Critical Failure Agent" in rendered
    assert "# Ability Check Agent" not in rendered
    assert "# Ability Check Critical Success Agent" not in rendered
    assert "### Memories" not in rendered
    assert "### Reveals" not in rendered
    assert ALL_MEMORIES[0].content not in rendered
    assert REVEAL_LEVEL_1 not in rendered
