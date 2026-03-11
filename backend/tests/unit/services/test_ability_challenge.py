import pytest

from app.models.class_traits import Abilities, Skills
from app.models.reveal import Reveal
from app.services.ability_challenge import (
    calculate_skill_check,
    filter_reveals_by_roll,
)
from tests.fixtures.generate import (
    create_default_bard_player,
    create_default_influence,
    create_inn_secrets_reveal,
)


def test_calculate_skill_check():
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


@pytest.mark.parametrize(
    ("total_roll", "expected"),
    [
        (0, "level_1_content"),
        (15, "level_2_content"),
        (20, "level_3_content"),
    ],
)
def test_filter_reveals_by_roll_inclusive_thresholds(total_roll, expected):
    reveal = create_inn_secrets_reveal(character_id=1, reveal_id=1)

    results = filter_reveals_by_roll([reveal], total_roll)

    assert results == [getattr(reveal, expected)]


def test_filter_reveals_by_roll_fallback_missing_exclusive():
    reveal = Reveal(
        id=1,
        title="Missing Exclusive",
        character_ids=[1],
        level_1_content="standard",
        level_2_content="privileged",
        level_3_content=None,
        standard_threshold=5,
        privileged_threshold=10,
        exclusive_threshold=15,
    )

    results = filter_reveals_by_roll([reveal], total_roll=20)

    assert results == ["privileged"]


def test_filter_reveals_by_roll_fallback_missing_privileged():
    reveal = Reveal(
        id=1,
        title="Missing Privileged",
        character_ids=[1],
        level_1_content="standard",
        level_2_content=None,
        level_3_content="exclusive",
        standard_threshold=5,
        privileged_threshold=10,
        exclusive_threshold=15,
    )

    results = filter_reveals_by_roll([reveal], total_roll=12)

    assert results == ["standard"]


def test_filter_reveals_by_roll_below_standard_threshold():
    reveal = Reveal(
        id=1,
        title="Above Standard",
        character_ids=[1],
        level_1_content="standard",
        level_2_content="privileged",
        level_3_content="exclusive",
        standard_threshold=10,
        privileged_threshold=15,
        exclusive_threshold=20,
    )

    results = filter_reveals_by_roll([reveal], total_roll=5)

    assert results == []


def test_filter_reveals_by_roll_preserves_input_order():
    first = Reveal(
        id=1,
        title="First",
        character_ids=[1],
        level_1_content="first_standard",
        level_2_content="first_privileged",
        level_3_content="first_exclusive",
        standard_threshold=0,
        privileged_threshold=10,
        exclusive_threshold=20,
    )
    second = Reveal(
        id=2,
        title="Second",
        character_ids=[1],
        level_1_content="second_standard",
        level_2_content="second_privileged",
        level_3_content="second_exclusive",
        standard_threshold=0,
        privileged_threshold=5,
        exclusive_threshold=15,
    )

    results = filter_reveals_by_roll([first, second], total_roll=12)

    assert results == ["first_privileged", "second_privileged"]
