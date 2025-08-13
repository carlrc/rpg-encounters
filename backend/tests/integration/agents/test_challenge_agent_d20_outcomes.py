from app.agents.challenge_agent import ChallengeAgent
from app.agents.prompts.import_prompts import import_system_prompt
from app.models.character import Character
from app.models.race import Race, Size, Gender
from app.models.alignment import Alignment
from app.models.player import Player
from app.models.reveal import DifficultyClass
from app.models.memory import Memory
from app.models.class_traits import Abilities, Skills, Class
from app.services.ability_challenge import D20Outcomes
from tests.utilities import (
    assert_does_not_contain_keywords,
    assert_contains_any_keywords,
)

REVEAL_LEVEL_1 = "For normal customers, the Inn has only 1 standard single bed room left for the evening."
REVEAL_LEVEL_2 = "For trusted customers, the Inn has a suite with a balcony available."
REVEAL_LEVEL_3 = "For important customers, a secret suite is available with a secret corridor which connects to all the rooms."

CHARACTER = Character(
    id=100,
    name="Bingo Bracegirdle",
    race=Race.LIGHTFOOT_HALFLING.value,
    size=Size.SMALL.value,
    alignment=Alignment.NEUTRAL_GOOD.value,
    gender=Gender.MALE.value,
    profession="Inn Owner",
    background="Friendly Inn keeper. Knows everyone in town and all the local gossip.",
    communication_style="Chatty and welcoming, always ready with a story or bit of news.",
    motivation="To keep the tavern running smoothly, keep customers happy and make money.",
    personality="Appreciates friendly conversation and local gossip sharing.",
    race_preferences={Race.LIGHTFOOT_HALFLING.value: DifficultyClass.VERY_EASY.value},
    class_preferences={Class.BARD.value: DifficultyClass.VERY_EASY.value},
    gender_preferences={Gender.FEMALE.value: DifficultyClass.VERY_EASY.value},
    size_preferences={Size.SMALL.value: DifficultyClass.VERY_EASY.value},
    appearance_keywords=None,
    storytelling_keywords=None,
)

PLAYER = Player(
    id=100,
    name="Wondering Bard",
    appearance="A small women with long brown hair with strong cheek bones.",
    race=Race.LIGHTFOOT_HALFLING.value,
    class_name=Class.BARD.value,
    size=Size.SMALL.value,
    alignment=Alignment.NEUTRAL_GOOD.value,
    gender=Gender.FEMALE.value,
    abilities={Abilities.CHARISMA: +1},
    skills={Skills.PERSUASION: +1},
)

CHALLENGE_SYSTEM_PROMPT = import_system_prompt("challenge_agent")

ALL_MEMORIES = [
    Memory(
        id=1,
        title="Oldest Inn",
        character_ids=[CHARACTER.id],
        content="This inn is the oldest in the city.",
    ),
    Memory(
        id=2,
        title="Old Mayors favourite room",
        character_ids=[CHARACTER.id],
        content="The old mayor used to love staying in the inn.",
    ),
]


async def test_challenge_agent_critical_success():
    """Test that critical success (d20=20) produces enthusiastic response with maximum information"""
    agent = ChallengeAgent(
        character=CHARACTER,
        player=PLAYER,
        system_prompt=CHALLENGE_SYSTEM_PROMPT,
        memories=ALL_MEMORIES,
        reveals=[REVEAL_LEVEL_3],
        d20_value=D20Outcomes.CRITICAL_SUCCESS.value,
    )

    response = await agent.chat(
        player_transcript="I want to know everything about your inn"
    )

    assert_contains_any_keywords(text=response, keywords=["secret", "corridor"])


async def test_challenge_agent_critical_failure():
    """Test that critical success (d20=20) produces enthusiastic response with maximum information"""
    agent = ChallengeAgent(
        character=CHARACTER,
        player=PLAYER,
        system_prompt=CHALLENGE_SYSTEM_PROMPT,
        memories=ALL_MEMORIES,
        reveals=[REVEAL_LEVEL_1],
        d20_value=D20Outcomes.CRITICAL_FAILURE.value,
    )

    response = await agent.chat(
        player_transcript="I want to know everything about your inn"
    )

    # TODO: This isn't a real test
    assert_does_not_contain_keywords(text=response, keywords=["secret", "corridor"])
