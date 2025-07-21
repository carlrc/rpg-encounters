import pytest
from app.agents.character_agent import CharacterAgent
from app.agents.prompts.import_prompts import import_system_prompt
from app.models.character import Character, CharacterRace, CharacterSize, CharacterAlignment, Gender
from app.models.player import Player, PlayerClass
from app.models.nugget import TrustNugget
from app.services.nugget_service import NuggetService
from app.data.trust_store import trust_state_store
from app.services.trust_calculator import TrustCalculator
from app.models.trust import TrustState

NUGGET_LEVEL_1 = "For normal customers, the Inn has only 1 standard single bed room left for the evening."
NUGGET_LEVEL_2 = "For trusted customers, the Inn has a suite with a balcony available."
NUGGET_LEVEL_3 = "For important customers, a secret suite is available with a secret corridor which connects to all the rooms."

@pytest.fixture(autouse=True)
def clear_trust_store():
    trust_state_store.clear()

def create_character():
    return Character(
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
        storytelling_keywords=None
    )

def create_test_nugget(character_id: int, title: str, level_1: str, level_2: str, level_3: str):
    return TrustNugget(
        id=1,  # Static ID since we're not persisting
        title=title,
        character_ids=[character_id],
        level_1_content=level_1,
        level_2_content=level_2,
        level_3_content=level_3
    )

def verify_nugget_content_availability(instructions, expected_available=None, expected_unavailable=None):
    if expected_available is None:
        expected_available = []
    if expected_unavailable is None:
        expected_unavailable = []
    
    for content in expected_available:
        assert content in instructions, f"Expected '{content}' to be available in instructions"

    for content in expected_unavailable:
        assert content not in instructions, f"Expected '{content}' to be unavailable in instructions"

async def test_personality_based_earned_trust():    
    character = create_character()
    
    # Create player that matches ALL of the characters preferences
    player = Player(
        id=100,
        name="Wondering Bard",
        appearance="A small women with long brown hair with strong cheek bones.",
        race=CharacterRace.HALFLING.value,
        class_name=PlayerClass.BARD.value,
        size=CharacterSize.SMALL.value, 
        alignment=CharacterAlignment.NEUTRAL_GOOD.value,
        gender=Gender.FEMALE.value
    )

    # Create test nugget directly
    test_nugget = create_test_nugget(character.id, "Inn Secrets", NUGGET_LEVEL_1, NUGGET_LEVEL_2, NUGGET_LEVEL_3)
    all_nuggets = [test_nugget]
    
    # Set up agent
    system_prompt = import_system_prompt()
    agent = CharacterAgent(character, player, system_prompt)

    trust_state = trust_state_store.update_trust_state(TrustState(
        character_id=character.id,
        player_id=player.id,
        base_trust=TrustCalculator.calculate_base_trust(character, player),
        earned_trust=0.0
    ))
    
    available_nuggets, unavailable_nuggets = NuggetService.categorize_nuggets_by_trust(trust_state, all_nuggets)

    result = await agent.chat("Hi there, I'm wondering if you have any rooms available tonight?", available_nuggets, unavailable_nuggets)
    
    assert result is not None
    message_history = result.all_messages()
    
    verify_nugget_content_availability(
        message_history[0].instructions,
        expected_available=[NUGGET_LEVEL_1, NUGGET_LEVEL_2],
        expected_unavailable=[NUGGET_LEVEL_3]
    )
    
    # Make all information available now
    result = await agent.chat("What type of room is it? I've just come from a long quest saving a lost princess...", [*available_nuggets, *unavailable_nuggets], [])
    
    assert result is not None
    message_history = result.all_messages()
    
    verify_nugget_content_availability(
        message_history[2].instructions,
        expected_available=[NUGGET_LEVEL_1, NUGGET_LEVEL_2, NUGGET_LEVEL_3],
        expected_unavailable=[]
    )