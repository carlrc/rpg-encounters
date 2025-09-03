"""Common test fixtures for conversation agent tests."""
from app.models.alignment import Alignment
from app.models.character import Character
from app.models.class_traits import Abilities, Class, Skills
from app.models.encounter import Encounter
from app.models.influence import BASE_INFLUENCE_MAX, Influence
from app.models.memory import Memory
from app.models.player import Player
from app.models.race import Gender, Race, Size
from app.models.reveal import DifficultyClass, Reveal

# Reveal content constants for easy access
REVEAL_LEVEL_1 = "For normal customers, the Inn has only 1 standard single bed room left for the evening."
REVEAL_LEVEL_2 = "For influential customers, the Inn has a suite with a balcony available."
REVEAL_LEVEL_3 = "For important customers, a secret suite is available with a secret corridor which connects to all the rooms."

def create_default_innkeeper_character(character_id: int) -> Character:
    """Create the default Bingo Bracegirdle innkeeper character for tests."""
    return Character(
        id=character_id,
        name="Bingo Bracegirdle",
        race=Race.LIGHTFOOT_HALFLING.value,
        size=Size.SMALL.value,
        alignment=Alignment.NEUTRAL_GOOD.value,
        gender=Gender.MALE.value,
        profession="Inn Owner",
        background="Friendly Inn keeper. Knows everyone in town and all the local gossip.",
        communication_style="Chatty and welcoming, always ready with a story or bit of news.",
        communication_style_type="Custom",
        motivation="To keep the tavern running smoothly, attract more customers and make more money.",
        personality="Appreciates friendly conversation and local gossip sharing.",
        race_preferences={Race.LIGHTFOOT_HALFLING.value: DifficultyClass.VERY_EASY.value},
        class_preferences={Class.BARD.value: DifficultyClass.VERY_EASY.value},
        gender_preferences={Gender.FEMALE.value: DifficultyClass.VERY_EASY.value},
        size_preferences={Size.SMALL.value: DifficultyClass.VERY_EASY.value},
        voice_name="Manual",
        voice_id="en-AU-Chirp3-HD-Achird",
        tts_provider="google"
    )

def create_default_evil_character(character_id: int) -> Character:
    """Create an evil character with malicious motivations for tests."""
    character = create_default_innkeeper_character(character_id=character_id)
    character.alignment = Alignment.CHAOTIC_EVIL.value
    character.profession = "Merchant"
    character.background = "A corrupted trader who thinks poorly of the world and its people. Uses his establishment as a front for illegal activities and information brokering."
    character.communication_style = "Smooth-talking and manipulative, with a sinister undertone. Often speaks in veiled threats and double meanings."
    character.motivation = "To gain power and wealth through any means necessary. Seeks to manipulate others for personal gain and enjoys watching them suffer. Plots to expand his criminal network and eliminate rivals."
    character.personality = "Cruel, calculating, and utterly selfish. Takes pleasure in others' misfortune and has no qualms about betraying anyone for profit."

    return character


def create_default_bard_player(player_id: int) -> Player:
    """Create the default Wondering Bard player for tests."""
    return Player(
        id=player_id,
        rl_name="Test",
        name="Wondering Bard",
        appearance="A small women with long brown hair with strong cheek bones.",
        race=Race.LIGHTFOOT_HALFLING.value,
        class_name=Class.BARD.value,
        size=Size.SMALL.value,
        alignment=Alignment.NEUTRAL_GOOD.value,
        gender=Gender.FEMALE.value,
        abilities={Abilities.CHARISMA.value: 3},
        skills={
            Skills.PERSUASION.value: 5,
            Skills.DECEPTION.value: 2,
            Skills.INTIMIDATION.value: 3,
            Skills.PERFORMANCE.value: 4,
        },
    )


def create_opposing_barbarian_player(player_id: int) -> Player:
    """Create an opposing barbarian player for negative test scenarios."""
    return Player(
        id=player_id,
        rl_name="Test",
        name="Wondering Barbarian",
        appearance="A large man with a big black beard.",
        race=Race.HUMAN.value,
        class_name=Class.BARBARIAN.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.NEUTRAL_EVIL.value,
        gender=Gender.MALE.value,
        abilities={Abilities.CHARISMA.value: 3},
        skills={Skills.PERSUASION.value: 5},
    )


def create_inn_secrets_reveal(character_id: int, reveal_id: int = 1) -> Reveal:
    """Create the default inn secrets reveal for tests."""
    return Reveal(
        id=reveal_id,
        title="Inn Secrets",
        character_ids=[character_id],
        level_1_content=REVEAL_LEVEL_1,
        level_2_content=REVEAL_LEVEL_2,
        level_3_content=REVEAL_LEVEL_3,
    )


def create_inn_memory(character_id: int, memory_id: int = 1) -> Memory:
    """Create the default inn memory for tests."""
    return Memory(
        id=memory_id,
        title="Oldest Inn",
        character_ids=[character_id],
        content="This inn is the oldest in the city.",
    )


def create_default_influence(
    character_id: int,
    player_id: int,
    # Just below max base
    base: int,
    earned: int
) -> Influence:
    """Create default influence state for tests."""
    return Influence(
        character_id=character_id,
        player_id=player_id,
        base=base,
        earned=earned,
    )


def create_test_encounter(encounter_id: int, character_id: int) -> Encounter:
    """Create a basic test encounter."""
    return Encounter(
        id=encounter_id,
        name="test",
        description="test",
        position_x=0.1,
        position_y=0.2,
        character_ids=[character_id],
    )

# Lambda factories for creating default instances with custom IDs
default_character = lambda character_id=100: create_default_innkeeper_character(character_id=character_id)
default_player = lambda player_id=100: create_default_bard_player(player_id=player_id)
default_reveals = lambda character_id=100: [create_inn_secrets_reveal(character_id=character_id)]
default_memories = lambda character_id=100: [create_inn_memory(character_id=character_id)]
default_influence = lambda character_id=100, player_id=100, base=BASE_INFLUENCE_MAX - 2, earned=0: create_default_influence(character_id=character_id, player_id=player_id, base=base, earned=earned)
default_encounter = lambda encounter_id=1, character_id=100: create_test_encounter(encounter_id=encounter_id, character_id=character_id)

# Pre-created default instances
DEFAULT_CHARACTER = default_character()
DEFAULT_PLAYER = default_player()
DEFAULT_REVEALS = default_reveals()
DEFAULT_MEMORIES = default_memories()
DEFAULT_INFLUENCE = default_influence()
DEFAULT_ENCOUNTER = default_encounter()

