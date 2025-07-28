import pytest
from app.agents.character_agent import CharacterAgent
from app.agents.prompts.import_prompts import import_system_prompt
from app.models.character import (
    Character,
    CharacterRace,
    CharacterSize,
    CharacterAlignment,
    Gender,
)
from app.models.player import Player, PlayerClass
from app.models.nugget import TrustNugget
from app.services.nugget_service import NuggetService
from app.data.trust_store import trust_state_store
from app.services.trust_calculator import TrustCalculator
from app.models.trust import TrustState
from tests.utilities import (
    verify_nugget_content_availability,
    assert_contains_any_keywords,
)

NUGGET_LEVEL_1 = "For normal customers, the Inn has only 1 standard single bed room left for the evening."
NUGGET_LEVEL_2 = "For trusted customers, the Inn has a suite with a balcony available."
NUGGET_LEVEL_3 = "For important customers, a secret suite is available with a secret corridor which connects to all the rooms."

CHARACTER = Character(
    id=100,
    name="Bingo Bracegirdle",
    race=CharacterRace.HALFLING.value,
    size=CharacterSize.SMALL.value,
    alignment=CharacterAlignment.NEUTRAL_GOOD.value,
    gender=Gender.MALE.value,
    profession="Inn Owner",
    background="Friendly Inn keeper. Knows everyone in town and all the local gossip.",
    communication_style="Chatty and welcoming, always ready with a story or bit of news.",
    motivation="To keep the tavern running smoothly, keep customers happy and make money.",
    personality="Appreciates friendly conversation and local gossip sharing.",
    race_preferences={CharacterRace.HALFLING.value: 0.3},
    class_preferences={PlayerClass.BARD.value: 0.3},
    gender_preferences={Gender.FEMALE.value: 0.3},
    size_preferences={CharacterSize.SMALL.value: 0.3},
    appearance_keywords=None,
    storytelling_keywords=None,
)

TEST_NUGGET = TrustNugget(
    id=1,  # Static ID since we're not persisting
    title="Inn Secrets",
    character_ids=[CHARACTER.id],
    level_1_content=NUGGET_LEVEL_1,
    level_2_content=NUGGET_LEVEL_2,
    level_3_content=NUGGET_LEVEL_3,
)


@pytest.fixture(autouse=True)
def clear_trust_store():
    trust_state_store.clear()


async def test_personality_based_earned_trust():
    # Create player that matches ALL of the characters preferences
    player = Player(
        id=100,
        name="Wondering Bard",
        appearance="A small women with long brown hair with strong cheek bones.",
        race=CharacterRace.HALFLING.value,
        class_name=PlayerClass.BARD.value,
        size=CharacterSize.SMALL.value,
        alignment=CharacterAlignment.NEUTRAL_GOOD.value,
        gender=Gender.FEMALE.value,
    )

    all_nuggets = [TEST_NUGGET]

    # Set up agent
    system_prompt = import_system_prompt("character_agent")

    trust_state = trust_state_store.update_trust_state(
        TrustState(
            character_id=CHARACTER.id,
            player_id=player.id,
            base_trust=TrustCalculator.calculate_base_trust(CHARACTER, player),
            earned_trust=0.0,
        )
    )

    agent = CharacterAgent(CHARACTER, player, system_prompt, trust_state)

    nugget_levels = NuggetService.categorize_nuggets_by_trust(trust_state, all_nuggets)

    result = await agent.chat(
        "Hi there, I'm wondering if you have any rooms available tonight?",
        nugget_levels,
    )

    assert result is not None
    message_history = result.all_messages()

    verify_nugget_content_availability(
        message_history[0].instructions,
        expected_available=[NUGGET_LEVEL_1, NUGGET_LEVEL_2],
        expected_conditional=[NUGGET_LEVEL_3],
        expected_unavailable=[],
    )

    result = await agent.chat(
        "What type of room is it? I've just come from a long quest saving a lost princess. Oh what a quest it was. It will be told for millennia!",
        nugget_levels,
    )

    # TODO: This type of test is brittle as the models aren't consistent
    assert_contains_any_keywords(result.output.response, ["secret", "corridor"])
