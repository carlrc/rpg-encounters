from app.agents.challenges.challenge_agent import ChallengeAgent
from app.agents.challenges.critical_failure_agent import CriticalFailureAgent
from app.agents.challenges.critical_success_agent import CriticalSuccessAgent
from app.agents.challenges.dependencies import ChallengeAgentDeps
from app.agents.prompts.import_prompts import import_system_prompt
from app.models.alignment import Alignment
from app.models.character import Character
from app.models.class_traits import Abilities, Class, Skills
from app.models.encounter import Encounter
from app.models.memory import Memory
from app.models.player import Player
from app.models.race import Gender, Race, Size
from app.models.reveal import DifficultyClass
from tests.utilities import (
    assert_contains_any_keywords,
    assert_does_not_contain_keywords,
)

SECRET_CORRIDOR = "For important customers, a secret suite is available with a secret corridor which connects to all the rooms."
MAYOR_SECRET = "The mayor used to bring foreign diplomats to this secret suite without his wife knowing."

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
    rl_name="Test",
    name="Wondering Bard",
    appearance="A small women with long brown hair with strong cheek bones.",
    race=Race.LIGHTFOOT_HALFLING.value,
    class_name=Class.BARD.value,
    size=Size.SMALL.value,
    alignment=Alignment.NEUTRAL_GOOD.value,
    gender=Gender.FEMALE.value,
    abilities={Abilities.CHARISMA.value: 16},
    skills={
        Skills.PERSUASION.value: 5,
        Skills.DECEPTION.value: 2,
        Skills.INTIMIDATION.value: 3,
        Skills.PERFORMANCE.value: 4,
    },
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

ENCOUNTER = Encounter(
    id=1,
    name="test",
    description="test",
    position_x=0.1,
    position_y=0.2,
    character_ids=[CHARACTER.id],
)

DEPENDENCIES = ChallengeAgentDeps(
    encounter=ENCOUNTER, messages=None, telemetry=lambda: None
)


async def test_challenge_agent_standard():
    """Test that critical success (d20=20) produces enthusiastic response with maximum information"""
    agent = ChallengeAgent(
        character=CHARACTER,
        player=PLAYER,
        system_prompt=import_system_prompt("challenge_agent"),
        memories=ALL_MEMORIES,
        reveals=[MAYOR_SECRET],
    )

    response = await agent.chat(
        player_transcript="I want to know everything about your inn",
        deps=DEPENDENCIES,
    )

    assert_contains_any_keywords(text=response, keywords=["mayor"])


async def test_challenge_agent_critical_success():
    """Test that critical success (d20=20) produces enthusiastic response with maximum information"""
    agent = CriticalSuccessAgent(
        character=CHARACTER,
        player=PLAYER,
        system_prompt=import_system_prompt("challenge_agent_critical_success"),
        memories=ALL_MEMORIES,
        reveals=[SECRET_CORRIDOR, MAYOR_SECRET],
    )

    response = await agent.chat(
        player_transcript="I want to know everything about your inn",
        deps=DEPENDENCIES,
    )

    assert_contains_any_keywords(
        text=response, keywords=["secret", "corridor", "diplomats"]
    )


async def test_challenge_agent_critical_failure():
    """Test that critical success (d20=20) produces enthusiastic response with maximum information"""
    agent = CriticalFailureAgent(
        character=CHARACTER,
        player=PLAYER,
        system_prompt=import_system_prompt("challenge_agent_critical_failure"),
        memories=ALL_MEMORIES,
    )

    response = await agent.chat(
        player_transcript="I want to know everything about your inn",
        deps=DEPENDENCIES,
    )

    # TODO: How to assert against negativity?
    # Assert does not give up memories
    assert_does_not_contain_keywords(response, ["mayor", "oldest"])
