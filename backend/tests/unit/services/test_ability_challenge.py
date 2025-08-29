import pytest

from app.models.class_traits import Abilities, Skills
from app.services.ability_challenge import calculate_skill_check
from tests.fixtures.generate import create_default_bard_player


def test_calculate_skill_check_happy_path():
    """Test successful skill check calculation with charisma modifier and skill modifier."""
    player = create_default_bard_player(player_id=1)
    player.abilities[Abilities.CHARISMA.value] = 3
    player.skills[Skills.INTIMIDATION.value] = 5

    result = calculate_skill_check(Skills.INTIMIDATION.value, player, 15)

    assert result == 23


def test_calculate_skill_check_missing_charisma():
    """Test error handling when player is missing charisma modifier."""
    player = create_default_bard_player(player_id=2)
    player.abilities = {}  # Remove charisma
    player.skills[Skills.PERSUASION.value] = 3

    with pytest.raises(ValueError, match="Player 2 missing charisma modifier"):
        calculate_skill_check(Skills.PERSUASION.value, player, 15)
