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
from app.models.nugget import TruthLayer, Truth
from app.data.trust_store import trust_state_store
from app.models.trust import BASE_TRUST_MAX, TrustState
from app.services.conversation_manager import ConversationManager
from app.services.trust_calculator import TrustCalculator
from app.agents.trust_scoring_agent import TrustCalculatorAgent
from tests.utilities import assert_does_not_contain_keywords

TRUTH_LEVEL_1 = "For normal customers, the Inn has only 1 standard single bed room left for the evening."
TRUTH_LEVEL_2 = "For trusted customers, the Inn has a suite with a balcony available."
TRUTH_LEVEL_3 = "For important customers, a secret suite is available with a secret corridor which connects to all the rooms."

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

PLAYER = Player(
    id=100,
    name="Wondering Bard",
    appearance="A small women with long brown hair with strong cheek bones.",
    race=CharacterRace.HALFLING.value,
    class_name=PlayerClass.BARD.value,
    size=CharacterSize.SMALL.value,
    alignment=CharacterAlignment.NEUTRAL_GOOD.value,
    gender=Gender.FEMALE.value,
)

CHAR_SYSTEM_PROMPT = import_system_prompt("character_agent")
SCORE_SYSTEM_PROMPT = import_system_prompt("trust_scoring_agent")

ALL_TRUTHS = [
    Truth(
        id=1,  # Static ID since we're not persisting
        title="Inn Secrets",
        character_ids=[CHARACTER.id],
        level_1_content=TRUTH_LEVEL_1,
        level_2_content=TRUTH_LEVEL_2,
        level_3_content=TRUTH_LEVEL_3,
    )
]

TRUST_STATE = trust_state_store.update_trust_state(
    TrustState(
        character_id=CHARACTER.id,
        player_id=PLAYER.id,
        base_trust=BASE_TRUST_MAX,  # Force max base trust
        earned_trust=0.0,
    )
)


@pytest.fixture(autouse=True)
def clear_trust_store():
    trust_state_store.clear()


async def test_personality_based_earned_trust_respects_public_level():
    agent = CharacterAgent(
        CHARACTER,
        PLAYER,
        CHAR_SYSTEM_PROMPT,
        TRUST_STATE,
        ConversationManager(),
        TrustCalculatorAgent(SCORE_SYSTEM_PROMPT, CHARACTER, PLAYER),
    )

    _, level, _ = await agent.chat(
        "Hi there, I'm wondering if you have any rooms available tonight?",
        ALL_TRUTHS,
    )
    # Bias with max base trust and basic inquiry should only result in public level
    assert level == TruthLayer.PUBLIC


async def test_personality_based_earned_trust_respects_privileged_level():
    agent = CharacterAgent(
        CHARACTER,
        PLAYER,
        CHAR_SYSTEM_PROMPT,
        TRUST_STATE,
        ConversationManager(),
        TrustCalculatorAgent(SCORE_SYSTEM_PROMPT, CHARACTER, PLAYER),
    )

    _, level, _ = await agent.chat(
        "Hi there, I'm wondering if you have any rooms available tonight?",
        ALL_TRUTHS,
    )
    _, level, _ = await agent.chat(
        "What type of room is it? I've just come from a long quest saving a lost princess. Oh what a quest it was. It will be told for millennia!",
        ALL_TRUTHS,
    )

    # Bias with max base trust and high alignment story should get privileged (not exclusive)
    assert level == TruthLayer.PRIVILEGED


async def test_personality_based_earned_trust_respects_exclusive_level():
    agent = CharacterAgent(
        CHARACTER,
        PLAYER,
        CHAR_SYSTEM_PROMPT,
        TRUST_STATE,
        ConversationManager(),
        TrustCalculatorAgent(SCORE_SYSTEM_PROMPT, CHARACTER, PLAYER),
    )

    await agent.chat(
        "Hi there, I'm wondering if you have any rooms available tonight?",
        ALL_TRUTHS,
    )
    await agent.chat(
        "There isn't more? I've just come from a long quest saving a lost princess. Oh what a quest it was. It will be told for millennia!",
        ALL_TRUTHS,
    )
    _, level, _ = await agent.chat(
        "My good man, in fact I need a better room because I'm here to help the town on an important quest...",
        ALL_TRUTHS,
    )

    # Bias with max base trust and high alignment story with repetition should get exclusive
    assert level == TruthLayer.EXCLUSIVE


async def test_personality_based_earned_trust_can_be_negative():
    # Make player not to the characters preferences
    opposing_player = Player(
        id=101,
        name="Wondering Barbarian",
        appearance="A large man with a big black beard.",
        race=CharacterRace.HUMAN.value,
        class_name=PlayerClass.BARBARIAN.value,
        size=CharacterSize.MEDIUM.value,
        alignment=CharacterAlignment.NEUTRAL_EVIL.value,
        gender=Gender.MALE.value,
    )

    trust_state = trust_state_store.update_trust_state(
        TrustState(
            character_id=CHARACTER.id,
            player_id=opposing_player.id,
            base_trust=TrustCalculator.calculate_base_trust(CHARACTER, opposing_player),
            earned_trust=0.0,
        )
    )
    agent = CharacterAgent(
        CHARACTER,
        opposing_player,
        CHAR_SYSTEM_PROMPT,
        trust_state,
        ConversationManager(),
        TrustCalculatorAgent(SCORE_SYSTEM_PROMPT, CHARACTER, opposing_player),
    )

    _, _, trust_adjustment = await agent.chat(
        "I need a room for the night you dirty old man!",
        ALL_TRUTHS,
    )

    assert trust_adjustment < 0.0

    _, _, trust_adjustment = await agent.chat(
        "That isn't good enough you old man!",
        ALL_TRUTHS,
    )

    assert trust_adjustment < 0.0


async def test_character_agent_handles_multiple_truths():
    agent = CharacterAgent(
        CHARACTER,
        PLAYER,
        CHAR_SYSTEM_PROMPT,
        TRUST_STATE,
        ConversationManager(),
        TrustCalculatorAgent(SCORE_SYSTEM_PROMPT, CHARACTER, PLAYER),
    )

    truths = [
        *ALL_TRUTHS,
        Truth(
            id=2,
            title="The Garden Vandal",
            character_ids=[1, 3, 4],
            level_1_content="There is someone vandalizing the towns gardens",
            level_2_content="It's a local. Not a foreigner as everyone expects.",
            level_3_content="It's Merry Greenhill vandalizing the gardens",
        ),
    ]

    garden_keywords = ["vandalizing", "garden", "foreigner", "Merry"]
    room_keywords = ["room", "standard", "balcony", "corridor"]

    # Start asking about the first truth (available rooms) and switch mid conversation to the garden vandal
    result, _, _ = await agent.chat(
        "I need a room",
        truths,
    )

    assert_does_not_contain_keywords(result, garden_keywords)

    result, _, _ = await agent.chat(
        "I want a better one with a view",
        truths,
    )

    assert_does_not_contain_keywords(result, garden_keywords)

    result, _, _ = await agent.chat(
        "Alright, also i want to know about this garden vandal. What gossip do you have?",
        truths,
    )

    assert_does_not_contain_keywords(result, room_keywords)
