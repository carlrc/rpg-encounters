import pytest

from app.agents.conversation_agent import ConversationAgent
from app.agents.prompts.import_prompts import import_system_prompt
from app.agents.trust_scoring_agent import TrustCalculatorAgent
from app.data.trust_store import trust_state_store
from app.models.alignment import Alignment
from app.models.character import Character
from app.models.class_traits import Abilities, Class, Skills
from app.models.player import Player
from app.models.race import Gender, Race, Size
from app.models.reveal import DifficultyClass, RevealLayer
from app.models.trust import BASE_TRUST_MAX, TrustState
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
    abilities={Abilities.CHARISMA: +1},
    skills={Skills.PERSUASION: +1},
)

TRUST_STATE = trust_state_store.update_trust_state(
    TrustState(
        character_id=CHARACTER.id,
        player_id=PLAYER.id,
        base_trust=BASE_TRUST_MAX,
        earned_trust=0,
    )
)

CHAR_SYSTEM_PROMPT = import_system_prompt("conversation_agent")
SCORE_SYSTEM_PROMPT = import_system_prompt("trust_scoring_agent")


@pytest.fixture(autouse=True)
def clear_trust_store():
    trust_state_store.clear()


async def test_agent_handles_no_reveals():
    agent = ConversationAgent(
        character=CHARACTER,
        player=PLAYER,
        system_prompt=CHAR_SYSTEM_PROMPT,
        trust_state=TRUST_STATE,
        conversation_manager=ConversationManager(),
        trust_calculator_agent=TrustCalculatorAgent(
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
