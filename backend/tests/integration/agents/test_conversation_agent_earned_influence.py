from app.agents.conversations.conversation_agent import (
    ConversationAgent,
    ConversationAgentDeps,
)
from app.agents.influence_scoring_agent import InfluenceCalculatorAgent
from app.agents.prompts.import_prompts import import_system_prompt
from app.models.alignment import Alignment
from app.models.character import Character
from app.models.class_traits import Abilities, Class, Skills
from app.models.influence import BASE_INFLUENCE_MAX, BASE_INFLUENCE_MIN, Influence
from app.models.memory import Memory
from app.models.player import Player
from app.models.race import Gender, Race, Size
from app.models.reveal import DifficultyClass, Reveal, RevealLayer
from app.services.conversation_manager import ConversationManager
from tests.utilities import assert_does_not_contain_keywords

REVEAL_LEVEL_1 = "For normal customers, the Inn has only 1 standard single bed room left for the evening."
REVEAL_LEVEL_2 = (
    "For influential customers, the Inn has a suite with a balcony available."
)
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

CHAR_SYSTEM_PROMPT = import_system_prompt("conversation_agent")
SCORE_SYSTEM_PROMPT = import_system_prompt("influence_scoring_agent")

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

ALL_MEMORIES = [
    Memory(
        id=1,
        title="Oldest Inn",
        character_ids=[CHARACTER.id],
        content="This inn is the oldest in the city.",
    )
]

INFLUENCE_STATE = Influence(
    character_id=CHARACTER.id,
    player_id=PLAYER.id,
    base=BASE_INFLUENCE_MAX,  # Force max base influence
    earned=0,
)

DEPENDENCIES = ConversationAgentDeps(
    reveals=ALL_REVEALS, encounter_description="", influence=INFLUENCE_STATE, user_id=1
)


async def test_personality_based_earned_influence_respects_standard_level():
    agent = ConversationAgent(
        character=CHARACTER,
        player=PLAYER,
        system_prompt=CHAR_SYSTEM_PROMPT,
        conversation_manager=ConversationManager(
            player_id=PLAYER.id, character_id=CHARACTER.id
        ),
        influence_calculator_agent=InfluenceCalculatorAgent(
            system_prompt=SCORE_SYSTEM_PROMPT, character=CHARACTER, player=PLAYER
        ),
        memories=ALL_MEMORIES,
    )

    _, level, _ = await agent.chat(
        player_transcript="Hi there, I'm wondering if you have any rooms available tonight?",
        deps=DEPENDENCIES,
    )
    # Bias with max base influence and basic inquiry should only result in standard level
    assert level == RevealLayer.STANDARD


async def test_personality_based_earned_influence_respects_privileged_level():
    agent = ConversationAgent(
        character=CHARACTER,
        player=PLAYER,
        system_prompt=CHAR_SYSTEM_PROMPT,
        conversation_manager=ConversationManager(
            player_id=PLAYER.id, character_id=CHARACTER.id
        ),
        influence_calculator_agent=InfluenceCalculatorAgent(
            system_prompt=SCORE_SYSTEM_PROMPT, character=CHARACTER, player=PLAYER
        ),
        memories=ALL_MEMORIES,
    )

    _, level, _ = await agent.chat(
        player_transcript="Hi there, I'm wondering if you have any rooms available tonight?",
        deps=DEPENDENCIES,
    )
    # A heroic deed that aligns morally and touches on their motivation (e.g., make money) should unlock PRIVILEGED
    _, level, _ = await agent.chat(
        player_transcript="What type of room is it? I've just come from a long quest saving a lost princess. Oh what a quest it was. It will be told for millennia! And my fame will drive customers to you...",
        deps=DEPENDENCIES,
    )

    # Bias with max base influence and high alignment story should get privileged (not exclusive)
    assert level == RevealLayer.PRIVILEGED


async def test_personality_based_earned_influence_respects_exclusive_level():
    influence = Influence(
        character_id=CHARACTER.id,
        player_id=PLAYER.id,
        base=BASE_INFLUENCE_MAX,  # Force max base influence
        earned=5,  # Start above PRIVILEGED when combined with base
    )

    agent = ConversationAgent(
        character=CHARACTER,
        player=PLAYER,
        system_prompt=CHAR_SYSTEM_PROMPT,
        conversation_manager=ConversationManager(
            player_id=PLAYER.id, character_id=CHARACTER.id
        ),
        influence_calculator_agent=InfluenceCalculatorAgent(
            system_prompt=SCORE_SYSTEM_PROMPT, character=CHARACTER, player=PLAYER
        ),
        memories=ALL_MEMORIES,
    )

    _, level, _ = await agent.chat(
        player_transcript="My good man, in fact I need the best room because I'm here to help the town on an important quest...",
        deps=ConversationAgentDeps(
            reveals=ALL_REVEALS,
            encounter_description="",
            influence=influence,
            user_id=1,
        ),
    )

    # Bias with max base influence and high alignment story with repetition should get exclusive
    assert level == RevealLayer.EXCLUSIVE


async def test_personality_based_earned_influence_can_be_negative():
    # Make player not to the characters preferences
    opposing_player = Player(
        id=101,
        name="Wondering Barbarian",
        appearance="A large man with a big black beard.",
        race=Race.HUMAN.value,
        class_name=Class.BARBARIAN.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.NEUTRAL_EVIL.value,
        gender=Gender.MALE.value,
        abilities={Abilities.CHARISMA.value: 16},
        skills={Skills.PERSUASION.value: 5},
    )

    influence = Influence(
        character_id=CHARACTER.id,
        player_id=opposing_player.id,
        base=BASE_INFLUENCE_MIN,
        earned=0,
    )

    agent = ConversationAgent(
        character=CHARACTER,
        player=opposing_player,
        system_prompt=CHAR_SYSTEM_PROMPT,
        conversation_manager=ConversationManager(
            player_id=opposing_player.id, character_id=CHARACTER.id
        ),
        influence_calculator_agent=InfluenceCalculatorAgent(
            system_prompt=SCORE_SYSTEM_PROMPT,
            character=CHARACTER,
            player=opposing_player,
        ),
        memories=ALL_MEMORIES,
    )

    _, level, influence = await agent.chat(
        player_transcript="I need a room for the night you dirty old man!",
        deps=ConversationAgentDeps(
            reveals=ALL_REVEALS,
            encounter_description="",
            influence=influence,
            user_id=1,
        ),
    )

    assert influence.earned < 0
    assert level == RevealLayer.NEGATIVE

    _, level, influence = await agent.chat(
        player_transcript="That isn't good enough you old man!",
        deps=ConversationAgentDeps(
            reveals=ALL_REVEALS,
            encounter_description="",
            influence=influence,
            user_id=1,
        ),
    )

    assert influence.earned < 0
    assert level == RevealLayer.NEGATIVE


async def test_conversation_agent_handles_multiple_reveals():
    agent = ConversationAgent(
        character=CHARACTER,
        player=PLAYER,
        system_prompt=CHAR_SYSTEM_PROMPT,
        memories=ALL_MEMORIES,
        conversation_manager=ConversationManager(
            player_id=PLAYER.id, character_id=CHARACTER.id
        ),
        influence_calculator_agent=InfluenceCalculatorAgent(
            SCORE_SYSTEM_PROMPT, CHARACTER, PLAYER
        ),
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
        player_transcript="I need a room",
        deps=ConversationAgentDeps(
            reveals=reveals,
            encounter_description="",
            influence=INFLUENCE_STATE,
            user_id=1,
        ),
    )

    assert_does_not_contain_keywords(result, garden_keywords)

    result, _, _ = await agent.chat(
        player_transcript="I want a better one with a view",
        deps=ConversationAgentDeps(
            reveals=reveals,
            encounter_description="",
            influence=INFLUENCE_STATE,
            user_id=1,
        ),
    )

    assert_does_not_contain_keywords(result, garden_keywords)

    result, _, _ = await agent.chat(
        player_transcript="Alright, also i want to know about this garden vandal. What gossip do you have?",
        deps=ConversationAgentDeps(
            reveals=reveals,
            encounter_description="",
            influence=INFLUENCE_STATE,
            user_id=1,
        ),
    )

    assert_does_not_contain_keywords(result, room_keywords)
