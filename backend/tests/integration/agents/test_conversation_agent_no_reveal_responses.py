import os
from unittest.mock import Mock

from app.agents.conversations.conversation_agent import (
    ConversationAgent,
    ConversationAgentDeps,
)
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.agents.prompts.import_prompts import render_jinja_prompt
from app.models.alignment import Alignment
from app.models.character import Character
from app.models.class_traits import Abilities, Class, Skills
from app.models.encounter import Encounter
from app.models.influence import BASE_INFLUENCE_MAX, Influence
from app.models.player import Player
from app.models.race import Gender, Race, Size
from app.models.reveal import DifficultyClass, RevealLayer
from app.services.context import ConvoContext

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

INFLUENCE_STATE = Influence(
    character_id=CHARACTER.id,
    player_id=PLAYER.id,
    base=BASE_INFLUENCE_MAX,
    earned=0,
)


TEST_DB_URL = os.getenv("TEST_DATABASE_URL")
CONVERSATION_STORE = Mock()


CONTEXT = ConvoContext(
    encounter=Encounter(
        id=1,
        name="test",
        description="test",
        position_x=0.1,
        position_y=0.2,
        character_ids=[CHARACTER.id],
    ),
    influence=INFLUENCE_STATE,
    reveals=[],
    memories=[],
    messages=None,
)

DEPENDENCIES = ConversationAgentDeps(
    player=PLAYER,
    character=CHARACTER,
    context=CONTEXT,
    user_id=1,
    telemetry=lambda: None,
)

BASE_TEMPLATE_CONTEXT = {
    "max_response_length": 30,
    "character": CHARACTER,
    "character_memories": [],
    "character_reveals": [],
    "player": PLAYER,
    "encounter": CONTEXT.encounter,
}

RENDERED_SYSTEM_PROMPT = render_jinja_prompt(
    "conversation_agent", BASE_TEMPLATE_CONTEXT
)


async def test_agent_handles_no_reveals():
    agent = ConversationAgent(
        system_prompt=RENDERED_SYSTEM_PROMPT,
        conversation_store=CONVERSATION_STORE,
        influence_calculator_agent=InfluenceCalculatorAgent(
            system_prompt=render_jinja_prompt(
                "influence_scoring_agent", {"character": CHARACTER, "player": PLAYER}
            ),
            character=CHARACTER,
            player=PLAYER,
        ),
    )

    _, level, _ = await agent.chat(
        player_transcript="Hi there, I'm wondering if you have any rooms available tonight?",
        deps=DEPENDENCIES,
    )
    # No reveals linked to character should result in standard response
    assert level == RevealLayer.STANDARD
