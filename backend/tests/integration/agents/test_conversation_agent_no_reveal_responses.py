import pytest

from app.agents.conversation_agent import ConversationAgent
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.agents.prompts.import_prompts import import_system_prompt
from app.data.influence_store import influence_store
from app.models.alignment import Alignment
from app.models.character import Character
from app.models.class_traits import Abilities, Class, Skills
from app.models.influence import BASE_INFLUENCE_MAX, Influence
from app.models.player import Player
from app.models.race import Gender, Race, Size
from app.models.reveal import DifficultyClass, RevealLayer
from app.services.conversation_manager import ConversationManager

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
    abilities={Abilities.CHARISMA.value: 16},
    skills={
        Skills.PERSUASION.value: 5,
        Skills.DECEPTION.value: 2,
        Skills.INTIMIDATION.value: 3,
        Skills.PERFORMANCE.value: 4,
    },
)

INFLUENCE_STATE = influence_store.update_influence(
    Influence(
        character_id=CHARACTER.id,
        player_id=PLAYER.id,
        base=BASE_INFLUENCE_MAX,
        earned=0,
    )
)

CHAR_SYSTEM_PROMPT = import_system_prompt("conversation_agent")
SCORE_SYSTEM_PROMPT = import_system_prompt("influence_scoring_agent")


@pytest.fixture(autouse=True)
def clear_influence_store():
    influence_store.clear()


async def test_agent_handles_no_reveals():
    agent = ConversationAgent(
        character=CHARACTER,
        player=PLAYER,
        system_prompt=CHAR_SYSTEM_PROMPT,
        influence=INFLUENCE_STATE,
        conversation_manager=ConversationManager(),
        influence_calculator_agent=InfluenceCalculatorAgent(
            SCORE_SYSTEM_PROMPT, CHARACTER, PLAYER
        ),
        memories=[],
    )

    _, level, _ = await agent.chat(
        "Hi there, I'm wondering if you have any rooms available tonight?",
        [],
    )
    # No reveals linked to character should result in standard response
    assert level == RevealLayer.STANDARD
