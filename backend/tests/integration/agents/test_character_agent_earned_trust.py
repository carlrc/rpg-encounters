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
from app.models.nugget import NuggetLayer, TrustNugget
from app.services.nugget_service import NuggetService
from app.data.trust_store import trust_state_store
from app.models.trust import BASE_TRUST_MAX, TrustState
from app.services.conversation_manager import ConversationManager
from app.services.trust_calculator import TrustCalculator
from app.agents.trust_scoring_agent import TrustCalculatorAgent

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

ALL_NUGGETS = [
    TrustNugget(
        id=1,  # Static ID since we're not persisting
        title="Inn Secrets",
        character_ids=[CHARACTER.id],
        level_1_content=NUGGET_LEVEL_1,
        level_2_content=NUGGET_LEVEL_2,
        level_3_content=NUGGET_LEVEL_3,
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

    nugget_levels = NuggetService.categorize_nuggets_by_trust(TRUST_STATE, ALL_NUGGETS)

    _, level, _ = await agent.chat(
        "Hi there, I'm wondering if you have any rooms available tonight?",
        nugget_levels,
    )
    # Bias with max base trust and basic inquiry should only result in public level
    assert level == NuggetLayer.PUBLIC


async def test_personality_based_earned_trust_respects_privileged_level():
    agent = CharacterAgent(
        CHARACTER,
        PLAYER,
        CHAR_SYSTEM_PROMPT,
        TRUST_STATE,
        ConversationManager(),
        TrustCalculatorAgent(SCORE_SYSTEM_PROMPT, CHARACTER, PLAYER),
    )

    nugget_levels = NuggetService.categorize_nuggets_by_trust(TRUST_STATE, ALL_NUGGETS)

    _, level, _ = await agent.chat(
        "Hi there, I'm wondering if you have any rooms available tonight?",
        nugget_levels,
    )
    _, level, _ = await agent.chat(
        "What type of room is it? I've just come from a long quest saving a lost princess. Oh what a quest it was. It will be told for millennia!",
        nugget_levels,
    )

    # Bias with max base trust and high alignment story should get privileged (not exclusive)
    assert level == NuggetLayer.PRIVILEGED


async def test_personality_based_earned_trust_respects_exclusive_level():
    agent = CharacterAgent(
        CHARACTER,
        PLAYER,
        CHAR_SYSTEM_PROMPT,
        TRUST_STATE,
        ConversationManager(),
        TrustCalculatorAgent(SCORE_SYSTEM_PROMPT, CHARACTER, PLAYER),
    )

    nugget_levels = NuggetService.categorize_nuggets_by_trust(TRUST_STATE, ALL_NUGGETS)

    await agent.chat(
        "Hi there, I'm wondering if you have any rooms available tonight?",
        nugget_levels,
    )
    await agent.chat(
        "There isn't more? I've just come from a long quest saving a lost princess. Oh what a quest it was. It will be told for millennia!",
        nugget_levels,
    )
    _, level, _ = await agent.chat(
        "My good man, in fact I need a better room because I'm here to help the town on an important quest...",
        nugget_levels,
    )

    # Bias with max base trust and high alignment story with repetition should get exclusive
    assert level == NuggetLayer.EXCLUSIVE


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

    nugget_levels = NuggetService.categorize_nuggets_by_trust(trust_state, ALL_NUGGETS)

    _, _, trust_adjustment = await agent.chat(
        "I need a room for the night you dirty old man!",
        nugget_levels,
    )

    assert trust_adjustment < 0.0

    _, _, trust_adjustment = await agent.chat(
        "That isn't good enough you old man!",
        nugget_levels,
    )

    assert trust_adjustment < 0.0
