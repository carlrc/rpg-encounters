from unittest.mock import AsyncMock

from app.agents.conversations.conversation_agent import (
    ConversationAgent,
    ConversationAgentDeps,
)
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.agents.prompts.import_prompts import render_prompt
from app.agents.prompts.limits import STANDARD_RESPONSE_WORD_LENGTH
from app.models.character import Character
from app.models.encounter import Encounter
from app.models.influence import BASE_INFLUENCE_MAX, BASE_INFLUENCE_MIN, Influence
from app.models.player import Player
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
    elevenlabs_token=None,
)

DEPENDENCIES = ConversationAgentDeps(
    context=CONTEXT,
    telemetry=lambda: None,
)

BASE_TEMPLATE_CONTEXT = {
    "max_response_length": STANDARD_RESPONSE_WORD_LENGTH,
    "character": CHARACTER,
    "memories": ALL_MEMORIES,
    "reveals": ALL_REVEALS,
    "player": PLAYER,
    "encounter": CONTEXT.encounter,
}

RENDERED_INSTRUCTIONS = render_prompt("conversation_agent", BASE_TEMPLATE_CONTEXT)


def create_influence_calculator_agent(
    character: Character, player: Player, encounter: Encounter
):
    """Create a new InfluenceCalculatorAgent instance for each test."""
    return InfluenceCalculatorAgent(
        system_prompt=render_prompt(
            "influence_scoring_agent",
            {
                "character": character,
                "player": player,
                "encounter": encounter,
            },
        )
    )


async def test_personality_based_earned_influence_respects_standard_level():
    agent = ConversationAgent(
        instructions=RENDERED_INSTRUCTIONS,
        conversation_store=AsyncMock(),
        influence_calculator_agent=create_influence_calculator_agent(
            character=CHARACTER.model_copy(deep=True),
            player=PLAYER.model_copy(deep=True),
            encounter=CONTEXT.encounter.model_copy(deep=True),
        ),
    )

    _, level, _ = await agent.chat(
        player_transcript="Hi there, I'm wondering if you have any rooms available tonight?",
        deps=DEPENDENCIES.model_copy(deep=True),
    )
    # Bias with max base influence and basic inquiry should only result in standard level
    assert level == RevealLayer.STANDARD


async def test_personality_based_earned_influence_respects_privileged_ceiling():
    agent = ConversationAgent(
        instructions=RENDERED_INSTRUCTIONS,
        conversation_store=AsyncMock(),
        influence_calculator_agent=create_influence_calculator_agent(
            character=CHARACTER.model_copy(deep=True),
            player=PLAYER.model_copy(deep=True),
            encounter=CONTEXT.encounter.model_copy(deep=True),
        ),
    )

    # A heroic deed plus a direct request for a better room should unlock PRIVILEGED
    _, level, _ = await agent.chat(
        player_transcript="Hello good man! I've just come from a long quest saving a lost princess. Oh what a quest it was. I'd like your finest suite for the night.",
        deps=DEPENDENCIES.model_copy(deep=True),
    )

    # Bias with max base influence and high alignment story should not exceed privileged
    assert level in {RevealLayer.STANDARD, RevealLayer.PRIVILEGED}


async def test_personality_based_earned_influence_respects_exclusive_level():
    # Start above PRIVILEGED when combined with base. Aiming at 3 point influence score for exclusive
    influence = Influence(
        character_id=CHARACTER.id,
        player_id=PLAYER.id,
        base=BASE_INFLUENCE_MAX,  # Force max base influence
        earned=2,
    )

    agent = ConversationAgent(
        instructions=RENDERED_INSTRUCTIONS,
        conversation_store=AsyncMock(),
        influence_calculator_agent=create_influence_calculator_agent(
            character=CHARACTER.model_copy(deep=True),
            player=PLAYER.model_copy(deep=True),
            encounter=CONTEXT.encounter.model_copy(deep=True),
        ),
    )

    updated_context = CONTEXT.model_copy(update={"influence": influence}, deep=True)
    updated_deps = DEPENDENCIES.model_copy(
        update={"context": updated_context}, deep=True
    )

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

    rendered_instructions = render_prompt("conversation_agent", template_context)

    agent = ConversationAgent(
        instructions=rendered_instructions,
        conversation_store=AsyncMock(),
        influence_calculator_agent=create_influence_calculator_agent(
            character=CHARACTER, player=opposing_player, encounter=CONTEXT.encounter
        ),
    )

    updated_context = CONTEXT.model_copy(update={"influence": influence}, deep=True)
    updated_deps = DEPENDENCIES.model_copy(
        update={
            "context": updated_context,
            "character": CHARACTER,
            "player": opposing_player,
        },
        deep=True,
    )

    _, level, influence = await agent.chat(
        player_transcript="I need a room for the night you dirty old man!",
        deps=updated_deps,
    )

    assert influence.earned < 0
    assert level == RevealLayer.NEGATIVE

    # Update the context again with the new influence
    updated_context = updated_context.model_copy(
        update={"influence": influence}, deep=True
    )
    updated_deps = updated_deps.model_copy(
        update={"context": updated_context}, deep=True
    )

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
    template_context["reveals"] = reveals

    rendered_instructions = render_prompt("conversation_agent", template_context)

    agent = ConversationAgent(
        instructions=rendered_instructions,
        conversation_store=AsyncMock(),
        influence_calculator_agent=create_influence_calculator_agent(
            character=CHARACTER.model_copy(deep=True),
            player=PLAYER.model_copy(deep=True),
            encounter=CONTEXT.encounter.model_copy(deep=True),
        ),
    )

    garden_keywords = ["vandalizing", "garden", "foreigner", "Merry"]
    room_keywords = ["room", "standard", "balcony", "corridor"]

    updated_context = CONTEXT.model_copy(update={"reveals": reveals}, deep=True)
    dependencies = DEPENDENCIES.model_copy(
        update={"context": updated_context}, deep=True
    )

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
