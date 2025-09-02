from unittest.mock import AsyncMock

from app.agents.conversations.conversation_agent import (
    ConversationAgent,
    ConversationAgentDeps,
)
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.agents.prompts.import_prompts import render_jinja_prompt
from app.models.influence import BASE_INFLUENCE_MAX, BASE_INFLUENCE_MIN, Influence
from app.models.reveal import Reveal, RevealLayer
from app.services.context import ConvoContext
from tests.fixtures.generate import (
    create_opposing_barbarian_player,
    default_character,
    default_encounter,
    default_influence,
    default_memories,
    default_player,
    default_reveals,
)
from tests.utilities import assert_does_not_contain_keywords

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
)

DEPENDENCIES = ConversationAgentDeps(
    context=CONTEXT,
    telemetry=lambda: None,
)

CONVERSATION_STORE = AsyncMock()

BASE_TEMPLATE_CONTEXT = {
    "max_response_length": 30,
    "character": CHARACTER,
    "character_memories": ALL_MEMORIES,
    "character_reveals": ALL_REVEALS,
    "player": PLAYER,
    "encounter": CONTEXT.encounter,
}

RENDERED_SYSTEM_PROMPT = render_jinja_prompt(
    "conversation_agent", BASE_TEMPLATE_CONTEXT
)
RENDERED_INSTRUCTIONS = render_jinja_prompt(
    "conversation_agent_instructions", BASE_TEMPLATE_CONTEXT
)

INFLUENCE_CALCULATOR_AGENT = InfluenceCalculatorAgent(
    system_prompt=render_jinja_prompt(
        "influence_scoring_agent", {"character": CHARACTER, "player": PLAYER}
    )
)


async def test_personality_based_earned_influence_respects_standard_level():
    agent = ConversationAgent(
        system_prompt=RENDERED_SYSTEM_PROMPT,
        instructions=RENDERED_INSTRUCTIONS,
        conversation_store=CONVERSATION_STORE,
        influence_calculator_agent=INFLUENCE_CALCULATOR_AGENT,
    )

    _, level, _ = await agent.chat(
        player_transcript="Hi there, I'm wondering if you have any rooms available tonight?",
        deps=DEPENDENCIES.model_copy(),
    )
    # Bias with max base influence and basic inquiry should only result in standard level
    assert level == RevealLayer.STANDARD


async def test_personality_based_earned_influence_respects_privileged_level():
    agent = ConversationAgent(
        system_prompt=RENDERED_SYSTEM_PROMPT,
        instructions=RENDERED_INSTRUCTIONS,
        conversation_store=CONVERSATION_STORE,
        influence_calculator_agent=INFLUENCE_CALCULATOR_AGENT,
    )

    # A heroic deed that aligns morally and touches on their motivation (e.g., make money) should unlock PRIVILEGED
    _, level, _ = await agent.chat(
        player_transcript="Hello good man! I've just come from a long quest saving a lost princess. Oh what a quest it was. It will be told for millennia! I need the best room that you have.",
        deps=DEPENDENCIES.model_copy(),
    )

    # Bias with max base influence and high alignment story should get privileged (not exclusive)
    assert level == RevealLayer.PRIVILEGED


async def test_personality_based_earned_influence_respects_exclusive_level():
    # Start above PRIVILEGED when combined with base. Aiming at 3 point influence score for exclusive
    influence = Influence(
        character_id=CHARACTER.id,
        player_id=PLAYER.id,
        base=BASE_INFLUENCE_MAX,  # Force max base influence
        earned=2,
    )

    agent = ConversationAgent(
        system_prompt=RENDERED_SYSTEM_PROMPT,
        instructions=RENDERED_INSTRUCTIONS,
        conversation_store=CONVERSATION_STORE,
        influence_calculator_agent=INFLUENCE_CALCULATOR_AGENT,
    )

    updated_context = CONTEXT.model_copy(update={"influence": influence})
    updated_deps = DEPENDENCIES.model_copy(update={"context": updated_context})

    # Being presumptuous doesn't match characters motivation
    _, level, _ = await agent.chat(
        player_transcript="My good man, I've just come from slaying a monster and am in need a good drink and banter!",
        deps=updated_deps,
    )

    # Bias with max base influence and high alignment story should get exclusive
    assert level == RevealLayer.EXCLUSIVE


async def test_personality_based_earned_influence_can_be_negative():
    # Make player not to the characters preferences
    opposing_player = create_opposing_barbarian_player(1001)

    influence = Influence(
        character_id=CHARACTER.id,
        player_id=opposing_player.id,
        base=BASE_INFLUENCE_MIN,
        earned=0,
    )

    # Create custom template context for opposing player
    template_context = BASE_TEMPLATE_CONTEXT.copy()
    template_context["player"] = opposing_player

    rendered_system_prompt = render_jinja_prompt("conversation_agent", template_context)
    rendered_instructions = render_jinja_prompt(
        "conversation_agent_instructions", template_context
    )

    agent = ConversationAgent(
        system_prompt=rendered_system_prompt,
        instructions=rendered_instructions,
        conversation_store=CONVERSATION_STORE,
        influence_calculator_agent=InfluenceCalculatorAgent(
            system_prompt=render_jinja_prompt(
                "influence_scoring_agent",
                {"character": CHARACTER, "player": opposing_player},
            )
        ),
    )

    updated_context = CONTEXT.model_copy(update={"influence": influence})
    updated_deps = DEPENDENCIES.model_copy(
        update={
            "context": updated_context,
            "character": CHARACTER,
            "player": opposing_player,
        }
    )

    _, level, influence = await agent.chat(
        player_transcript="I need a room for the night you dirty old man!",
        deps=updated_deps,
    )

    assert influence.earned < 0
    assert level == RevealLayer.NEGATIVE

    # Update the context again with the new influence
    updated_context = updated_context.model_copy(update={"influence": influence})
    updated_deps = updated_deps.model_copy(update={"context": updated_context})

    _, level, influence = await agent.chat(
        player_transcript="That isn't good enough you old man!",
        deps=updated_deps,
    )

    assert influence.earned < 0
    assert level == RevealLayer.NEGATIVE


async def test_conversation_agent_handles_multiple_reveals():
    reveals = [
        *ALL_REVEALS,
        Reveal(
            id=2,
            title="The Garden Vandal",
            character_ids=[1, 3, 4],
            level_1_content="There is someone vandalizing the towns gardens",
            level_2_content="It's a local. Not a foreigner as everyone expects.",
            level_3_content="It's Merry Greenhill vandalizing the gardens",
        ),
    ]

    # Create custom template context for different reveals
    template_context = BASE_TEMPLATE_CONTEXT.copy()
    template_context["character_reveals"] = reveals

    rendered_system_prompt = render_jinja_prompt("conversation_agent", template_context)
    rendered_instructions = render_jinja_prompt(
        "conversation_agent_instructions", template_context
    )

    agent = ConversationAgent(
        system_prompt=rendered_system_prompt,
        instructions=rendered_instructions,
        conversation_store=CONVERSATION_STORE,
        influence_calculator_agent=INFLUENCE_CALCULATOR_AGENT,
    )

    garden_keywords = ["vandalizing", "garden", "foreigner", "Merry"]
    room_keywords = ["room", "standard", "balcony", "corridor"]

    updated_context = CONTEXT.model_copy(update={"reveals": reveals})
    dependencies = DEPENDENCIES.model_copy(update={"context": updated_context})

    # Start asking about the first reveal (available rooms) and switch mid conversation to the garden vandal
    result, _, _ = await agent.chat(
        player_transcript="I need a room",
        deps=dependencies,
    )

    assert_does_not_contain_keywords(result, garden_keywords)

    result, _, _ = await agent.chat(
        player_transcript="I want a better one with a view",
        deps=dependencies,
    )

    assert_does_not_contain_keywords(result, garden_keywords)

    result, _, _ = await agent.chat(
        player_transcript="Alright, also i want to know about this garden vandal. What gossip do you have?",
        deps=dependencies,
    )

    assert_does_not_contain_keywords(result, room_keywords)
