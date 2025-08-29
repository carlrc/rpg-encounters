#!/usr/bin/env python3
from app.models.alignment import Alignment
from app.models.character import Character, CommunicationStyle
from app.models.class_traits import Abilities, Class, Skills
from app.models.influence import BASE_INFLUENCE_MIN
from app.models.player import Player
from app.models.race import Gender, Race, Size
from app.models.reveal import DifficultyClass
from app.services.influence_calculator import calculate_base_influence


def test_influence_calculation():
    """Test the influence calculation system"""
    character = Character(
        id=1,
        user_id=1,
        world_id=1,
        name="Bingo Bracegirdle",
        race=Race.LIGHTFOOT_HALFLING.value,
        background="test",
        profession="test",
        communication_style="test",
        motivation="test",
        size=Size.SMALL.value,
        alignment=Alignment.NEUTRAL_GOOD.value,
        gender=Gender.MALE.value,
        class_preferences={Class.BARD.value: -DifficultyClass.VERY_EASY.value},
        race_preferences={
            Race.HUMAN.value: -DifficultyClass.VERY_EASY.value,
        },
        gender_preferences={Gender.MALE: -DifficultyClass.VERY_EASY.value},
        voice="test",
        communication_style_type=CommunicationStyle.CUSTOM.value,
    )
    player = Player(
        id=1,
        rl_name="test",
        user_id=1,
        world_id=1,
        name="Sir Alaric Duskbane",
        appearance="Human paladin in chain mail with noble bearing and a resolute gaze.",
        race=Race.HUMAN.value,
        class_name=Class.BARD.value,
        size=Size.MEDIUM.value,
        alignment=Alignment.LAWFUL_GOOD.value,
        gender=Gender.MALE.value,
        abilities={Abilities.CHARISMA.value: 14},
        skills={
            Skills.DECEPTION.value: 2,
            Skills.INTIMIDATION.value: 4,
            Skills.PERFORMANCE.value: 2,
            Skills.PERSUASION.value: 4,
        },
    )

    # Calculate base influence using character directly
    base_influence = calculate_base_influence(character, player)

    # -15 should be clipped to minimum
    assert base_influence == BASE_INFLUENCE_MIN
