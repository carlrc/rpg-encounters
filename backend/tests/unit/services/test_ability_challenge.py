from app.models.class_traits import Abilities, Skills
from app.services.ability_challenge import calculate_skill_check
from tests.fixtures.generate import create_default_bard_player, create_default_influence


def test_calculate_skill_check_happy_path():
    """Test successful skill check calculation with charisma modifier and skill modifier."""
    player = create_default_bard_player(player_id=1)
    influence = create_default_influence(
        character_id=1, player_id=player.id, base=0, earned=-1
    )
    player.abilities[Abilities.CHARISMA.value] = 3
    player.skills[Skills.INTIMIDATION.value] = 5

    result = calculate_skill_check(
        skill=Skills.INTIMIDATION.value, player=player, d20_roll=15, influence=influence
    )

    assert result == 22
