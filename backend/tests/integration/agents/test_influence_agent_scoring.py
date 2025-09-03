from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.agents.prompts.import_prompts import render_prompt
from tests.fixtures.generate import (
    create_default_evil_character,
    create_default_innkeeper_character,
    default_encounter,
    default_player,
)

# Use default fixtures
CHARACTER = create_default_innkeeper_character(character_id=100)
EVIL_CHARACTER = create_default_evil_character(character_id=1001)
PLAYER = default_player()
ENCOUNTER = default_encounter()

INFLUENCE_CALCULATOR_AGENT = InfluenceCalculatorAgent(
    system_prompt=render_prompt(
        "influence_scoring_agent",
        {"character": CHARACTER, "player": PLAYER, "encounter": ENCOUNTER},
    )
)


async def test_service_question_neutral():
    response = await INFLUENCE_CALCULATOR_AGENT.process(
        msg="Can you tell me about your services?"
    )

    assert response.score == 0


async def test_high_moral_alignment_message():
    # Heroic deeds and banter
    response = await INFLUENCE_CALCULATOR_AGENT.process(
        msg="My good man, I've just come from slaying a monster and am in need a good drink and banter!"
    )

    assert response.score == 10


async def test_high_personality_alignment_message():
    # Gossip
    response = await INFLUENCE_CALCULATOR_AGENT.process(
        msg="Did you hear about what Jose did? So funny..."
    )

    assert response.score == 10


async def test_low_personality_alignment_message():
    # Counter to the tavern running smoothly
    response = await INFLUENCE_CALCULATOR_AGENT.process(
        msg="I broke a table dancing on it"
    )

    assert response.score <= -2


async def test_low_moral_alignment_message():
    # Gossip
    response = await INFLUENCE_CALCULATOR_AGENT.process(
        msg="Stealing from that old lady was too easy."
    )

    assert response.score == -10


async def test_evil_high_moral_alignment():
    agent = InfluenceCalculatorAgent(
        system_prompt=render_prompt(
            "influence_scoring_agent",
            {"character": EVIL_CHARACTER, "player": PLAYER, "encounter": ENCOUNTER},
        )
    )
    response = await agent.process(msg="Stealing from that old lady was too easy.")

    assert response.score == 10


async def test_evil_low_moral_alignment():
    agent = InfluenceCalculatorAgent(
        system_prompt=render_prompt(
            "influence_scoring_agent",
            {"character": EVIL_CHARACTER, "player": PLAYER, "encounter": ENCOUNTER},
        )
    )
    response = await agent.process(
        msg="My good man, I've just come from slaying a monster to protect someone"
    )

    assert response.score <= -5
