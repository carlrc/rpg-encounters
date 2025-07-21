import pytest
from app.agents.character_agent import CharacterAgent
from app.agents.prompts.import_prompts import import_system_prompt
from app.models.character import Character, CharacterRace, CharacterSize, CharacterAlignment, Gender
from app.models.player import Player, PlayerClass
from app.models.nugget import TrustNugget, NuggetLayer
from app.services.nugget_service import NuggetService
from app.data.trust_store import trust_state_store
from app.services.trust_calculator import TrustCalculator
from app.models.trust import TrustState

NUGGET_LEVEL_1 = "I've been running this tavern for over twenty years and know everyone in town."
NUGGET_LEVEL_2 = "The mayor has been skimming coins from the town treasury to pay his gambling debts."
NUGGET_LEVEL_3 = "There's a secret passage behind the wine cellar that leads to the old smuggler's tunnels."

@pytest.fixture(autouse=True)
def clear_trust_store():
    """Clear trust store before each test to ensure isolation."""
    trust_state_store.clear()

def create_character():
    return Character(
        id=100,
        name="Bingo Bracegirdle",
        race=CharacterRace.HALFLING.value,
        size=CharacterSize.SMALL.value,
        alignment=CharacterAlignment.NEUTRAL_GOOD.value,
        gender=Gender.MALE.value,
        profession="Tavern Owner",
        background="Friendly tavern keeper who runs the village inn. Knows everyone in town and all the local gossip.",
        communication_style="Chatty and welcoming, always ready with a story or bit of news.",
        motivation="To keep the tavern running smoothly and customers happy.",
        personality="Appreciates friendly conversation and local gossip sharing.",
        race_preferences={CharacterRace.HALFLING.value: 0.3},
        class_preferences={PlayerClass.BARD.value: 0.3},
        gender_preferences={Gender.FEMALE.value: 0.3},
        size_preferences={CharacterSize.SMALL.value: 0.3},
        appearance_keywords=None,
        storytelling_keywords=None
    )

def create_test_nugget(character_id: int, title: str, level_1: str, level_2: str, level_3: str):
    """Helper to create test nuggets with all three trust levels."""
    return TrustNugget(
        id=1,  # Static ID since we're not persisting
        title=title,
        character_ids=[character_id],
        level_1_content=level_1,
        level_2_content=level_2,
        level_3_content=level_3
    )

async def run_trust_test(character: Character, player: Player, earned_trust: float, 
                        nugget_title: str, level_1: str, level_2: str, level_3: str,
                        chat_message: str, expected_available: list, expected_unavailable: list):
    trust_state = trust_state_store.update_trust_state(TrustState(
        character_id=character.id,
        player_id=player.id,
        base_trust=TrustCalculator.calculate_base_trust(character, player),
        earned_trust=earned_trust
    ))
    
    # Create test nugget directly
    test_nugget = create_test_nugget(character.id, nugget_title, level_1, level_2, level_3)
    all_nuggets = [test_nugget]
    
    # Set up agent
    system_prompt = import_system_prompt()
    agent = CharacterAgent(character, player, system_prompt, trust_state)
    
    # Categorize nuggets by trust
    nugget_levels = NuggetService.categorize_nuggets_by_trust(trust_state, all_nuggets)

    # Run chat
    result = await agent.chat(chat_message, nugget_levels)
    
    assert result is not None
    message_history = result.all_messages()
    
    # Verify expected content is available/unavailable
    for content in expected_available:
        assert content in message_history[0].instructions, f"Expected '{content}' to be available"
    
    for content in expected_unavailable:
        assert content not in message_history[0].instructions, f"Expected '{content}' to be unavailable"
    
    # Verify categorization counts
    available_content = [level.content for level in nugget_levels if level.available]
    unavailable_content = [level.content for level in nugget_levels if not level.available]
    assert len(available_content) == len(expected_available)
    assert len(unavailable_content) == len(expected_unavailable)

async def test_low_static_trust_public_only():
    """Test that only public (Layer 1) nuggets are accessible with low trust."""
    
    character = create_character()
    
    # Create player that matches NONE of the character's preferences (0.0 base trust)
    player = Player(
        id=100,
        name="Mismatched Adventurer",
        appearance="A human warrior with no connection to halfling culture",
        race=CharacterRace.HUMAN.value,  # Not Halfling 
        class_name=PlayerClass.FIGHTER.value,  # Not Bard
        size=CharacterSize.MEDIUM.value,  # Not Small
        alignment=CharacterAlignment.NEUTRAL_GOOD.value,
        gender=Gender.MALE.value  # Not female
    )

    await run_trust_test(
        character=character,
        player=player,
        earned_trust=0.0,
        nugget_title="Tavern Secrets",
        level_1=NUGGET_LEVEL_1,
        level_2=NUGGET_LEVEL_2,
        level_3=NUGGET_LEVEL_3,
        chat_message="What's the latest gossip at the tavern?",
        expected_available=[NUGGET_LEVEL_1],
        expected_unavailable=[NUGGET_LEVEL_2, NUGGET_LEVEL_3]
    )


async def test_moderate_static_trust_privileged_access():
    """Test that privileged (Layer 2) nuggets are accessible with moderate-high static trust."""
    
    character = create_character()
    
    # Create player that matches TWO of the character's preferences (0.6 base trust)
    player = Player(
        id=101,
        name="Pippin Greenhill",
        appearance="Cheerful halfling with curly auburn hair and bright brown eyes",
        race=CharacterRace.HALFLING.value,
        class_name=PlayerClass.ROGUE.value,  # Not Bard
        size=CharacterSize.MEDIUM.value,  # Not small
        alignment=CharacterAlignment.CHAOTIC_GOOD.value,
        gender=Gender.FEMALE.value
    )
    
    await run_trust_test(
        character=character,
        player=player,
        earned_trust=0.0,
        nugget_title="Tavern Secrets",
        level_1=NUGGET_LEVEL_1,
        level_2=NUGGET_LEVEL_2,
        level_3=NUGGET_LEVEL_3,
        chat_message="What's the latest gossip at the tavern?",
        expected_available=[NUGGET_LEVEL_1, NUGGET_LEVEL_2],
        expected_unavailable=[NUGGET_LEVEL_3]
    )

async def test_high_static_trust_with_dynamic_max_access():
    """Test that all nugget layers are accessible with maximum trust (base + earned)."""
    
    character = create_character()
    
    # Create player that matches ALL of the character's preferences (1.2 base trust, capped at 0.6)
    player = Player(
        id=102,
        name="Melody Greenhill",
        appearance="A small halfling bard with a warm smile and musical instruments",
        race=CharacterRace.HALFLING.value,  
        class_name=PlayerClass.BARD.value,  
        size=CharacterSize.SMALL.value,
        alignment=CharacterAlignment.CHAOTIC_GOOD.value,
        gender=Gender.FEMALE.value
    )
    
    await run_trust_test(
        character=character,
        player=player,
        earned_trust=0.4,  # Maximum earned trust
        nugget_title="Tavern Secrets",
        level_1=NUGGET_LEVEL_1,
        level_2=NUGGET_LEVEL_2,
        level_3=NUGGET_LEVEL_3,
        chat_message="What's the latest gossip at the tavern?",
        expected_available=[NUGGET_LEVEL_1, NUGGET_LEVEL_2, NUGGET_LEVEL_3],
        expected_unavailable=[]
    )
    
