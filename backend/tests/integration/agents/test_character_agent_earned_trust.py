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
from app.models.reveal import DifficultyClass
from app.models.reveal import RevealLayer, Reveal
from app.data.trust_store import trust_state_store
from app.models.trust import BASE_TRUST_MAX, TrustState
from app.services.conversation_manager import ConversationManager
from app.services.trust_calculator import TrustCalculator
from app.agents.trust_scoring_agent import TrustCalculatorAgent
from tests.utilities import assert_does_not_contain_keywords

REVEAL_LEVEL_1 = "For normal customers, the Inn has only 1 standard single bed room left for the evening."
REVEAL_LEVEL_2 = "For trusted customers, the Inn has a suite with a balcony available."
REVEAL_LEVEL_3 = "For important customers, a secret suite is available with a secret corridor which connects to all the rooms."

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
    race_preferences={CharacterRace.HALFLING.value: DifficultyClass.VERY_EASY.value},
    class_preferences={PlayerClass.BARD.value: DifficultyClass.VERY_EASY.value},
    gender_preferences={Gender.FEMALE.value: DifficultyClass.VERY_EASY.value},
    size_preferences={CharacterSize.SMALL.value: DifficultyClass.VERY_EASY.value},
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

ALL_REVEALS = [
    Reveal(
        id=1,  # Static ID since we're not persisting
        title="Inn Secrets",
        character_ids=[CHARACTER.id],
        level_1_content=REVEAL_LEVEL_1,
        level_2_content=REVEAL_LEVEL_2,
        level_3_content=REVEAL_LEVEL_3,
    )
]

TRUST_STATE = trust_state_store.update_trust_state(
    TrustState(
        character_id=CHARACTER.id,
        player_id=PLAYER.id,
        base_trust=BASE_TRUST_MAX,  # Force max base trust
        earned_trust=0,
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
        ALL_REVEALS,
    )
    # Bias with max base trust and basic inquiry should only result in public level
    assert level == RevealLayer.PUBLIC


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
        ALL_REVEALS,
    )
    # A heroic deed that aligns morally and touches on their motivation (e.g., make money) should unlock PRIVILEGED
    _, level, _ = await agent.chat(
        "What type of room is it? I've just come from a long quest saving a lost princess. Oh what a quest it was. It will be told for millennia! And my fame will drive customers to you...",
        ALL_REVEALS,
    )

    # Bias with max base trust and high alignment story should get privileged (not exclusive)
    assert level == RevealLayer.PRIVILEGED


async def test_personality_based_earned_trust_respects_exclusive_level():
    trust_state = trust_state_store.update_trust_state(
        TrustState(
            character_id=CHARACTER.id,
            player_id=PLAYER.id,
            base_trust=BASE_TRUST_MAX,  # Force max base trust
            earned_trust=5,  # Start above PRIVILEGED when combined with base
        )
    )

    agent = CharacterAgent(
        CHARACTER,
        PLAYER,
        CHAR_SYSTEM_PROMPT,
        trust_state,
        ConversationManager(),
        TrustCalculatorAgent(SCORE_SYSTEM_PROMPT, CHARACTER, PLAYER),
    )

    _, level, _ = await agent.chat(
        "My good man, in fact I need the best room because I'm here to help the town on an important quest...",
        ALL_REVEALS,
    )

    # Bias with max base trust and high alignment story with repetition should get exclusive
    assert level == RevealLayer.EXCLUSIVE


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
            earned_trust=0,
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
        ALL_REVEALS,
    )

    assert trust_adjustment < 0

    _, _, trust_adjustment = await agent.chat(
        "That isn't good enough you old man!",
        ALL_REVEALS,
    )

    assert trust_adjustment < 0


async def test_character_agent_handles_multiple_reveals():
    agent = CharacterAgent(
        CHARACTER,
        PLAYER,
        CHAR_SYSTEM_PROMPT,
        TRUST_STATE,
        ConversationManager(),
        TrustCalculatorAgent(SCORE_SYSTEM_PROMPT, CHARACTER, PLAYER),
    )

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

    garden_keywords = ["vandalizing", "garden", "foreigner", "Merry"]
    room_keywords = ["room", "standard", "balcony", "corridor"]

    # Start asking about the first reveal (available rooms) and switch mid conversation to the garden vandal
    result, _, _ = await agent.chat(
        "I need a room",
        reveals,
    )

    assert_does_not_contain_keywords(result, garden_keywords)

    result, _, _ = await agent.chat(
        "I want a better one with a view",
        reveals,
    )

    assert_does_not_contain_keywords(result, garden_keywords)

    result, _, _ = await agent.chat(
        "Alright, also i want to know about this garden vandal. What gossip do you have?",
        reveals,
    )

    assert_does_not_contain_keywords(result, room_keywords)
