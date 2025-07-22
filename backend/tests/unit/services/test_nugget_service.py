import pytest
from app.services.nugget_service import NuggetService
from app.models.nugget import (
    NuggetLayer,
    TrustNugget,
    NUGGET_THRESHOLDS,
)
from app.models.trust import (
    BASE_TRUST_MAX,
    EARNED_TRUST_MAX,
    TOTAL_TRUST_MAX,
    TrustState,
)
from tests.fixtures.characters import characters_db


# Test content constants
PUBLIC_CONTENT = "I run the best tavern in town."
PRIVILEGED_CONTENT = "The mayor owes me gambling money."
EXCLUSIVE_CONTENT = "There's a secret tunnel behind my wine cellar."


@pytest.fixture
def static_character():
    """Use Bingo Bracegirdle as static character for all tests"""
    return characters_db[1]


@pytest.fixture
def test_nugget(static_character):
    """Create a single nugget with all three content levels for testing"""
    return TrustNugget(
        id=1,
        title="Tavern Secrets",
        character_ids=[static_character.id],
        level_1_content=PUBLIC_CONTENT,
        level_2_content=PRIVILEGED_CONTENT,
        level_3_content=EXCLUSIVE_CONTENT,
    )


def create_trust_state(static_character, total_trust: float):
    """Helper to create TrustState with specific total trust level"""
    # Calculate base_trust and earned_trust to achieve desired total_trust
    # Keep it simple: use base_trust primarily, earned_trust as adjustment
    base_trust = min(BASE_TRUST_MAX, total_trust)
    earned_trust = max(
        -BASE_TRUST_MAX, min(EARNED_TRUST_MAX, total_trust - base_trust)
    )  # Clamp earned trust

    return TrustState(
        character_id=static_character.id,
        player_id=999,  # Dynamic player ID
        base_trust=base_trust,
        earned_trust=earned_trust,
    )


def test_categorize_nuggets_below_privileged_threshold(static_character, test_nugget):
    """Test categorization just below PRIVILEGED threshold"""
    privileged_threshold = NUGGET_THRESHOLDS[NuggetLayer.PRIVILEGED.name]
    trust_state = create_trust_state(static_character, privileged_threshold - 0.01)

    nugget_levels = NuggetService.categorize_nuggets_by_trust(
        trust_state, [test_nugget]
    )

    # Should have 3 levels total
    assert len(nugget_levels) == 3

    # Check availability: only PUBLIC should be available
    available_content = [level.content for level in nugget_levels if level.available]
    unavailable_content = [
        level.content for level in nugget_levels if not level.available
    ]

    assert available_content == [PUBLIC_CONTENT]
    assert set(unavailable_content) == {PRIVILEGED_CONTENT, EXCLUSIVE_CONTENT}


def test_categorize_nuggets_at_privileged_threshold(static_character, test_nugget):
    """Test categorization exactly at PRIVILEGED threshold"""
    privileged_threshold = NUGGET_THRESHOLDS[NuggetLayer.PRIVILEGED.name]
    trust_state = create_trust_state(static_character, privileged_threshold)

    nugget_levels = NuggetService.categorize_nuggets_by_trust(
        trust_state, [test_nugget]
    )

    # Check availability: PUBLIC + PRIVILEGED should be available
    available_content = [level.content for level in nugget_levels if level.available]
    unavailable_content = [
        level.content for level in nugget_levels if not level.available
    ]

    assert set(available_content) == {PUBLIC_CONTENT, PRIVILEGED_CONTENT}
    assert unavailable_content == [EXCLUSIVE_CONTENT]


def test_categorize_nuggets_below_exclusive_threshold(static_character, test_nugget):
    """Test categorization just below EXCLUSIVE threshold"""
    exclusive_threshold = NUGGET_THRESHOLDS[NuggetLayer.EXCLUSIVE.name]
    trust_state = create_trust_state(static_character, exclusive_threshold - 0.01)

    nugget_levels = NuggetService.categorize_nuggets_by_trust(
        trust_state, [test_nugget]
    )

    # Check availability: PUBLIC + PRIVILEGED should be available
    available_content = [level.content for level in nugget_levels if level.available]
    unavailable_content = [
        level.content for level in nugget_levels if not level.available
    ]

    assert set(available_content) == {PUBLIC_CONTENT, PRIVILEGED_CONTENT}
    assert unavailable_content == [EXCLUSIVE_CONTENT]


def test_categorize_nuggets_at_exclusive_threshold(static_character, test_nugget):
    """Test categorization exactly at EXCLUSIVE threshold"""
    exclusive_threshold = NUGGET_THRESHOLDS[NuggetLayer.EXCLUSIVE.name]
    trust_state = create_trust_state(static_character, exclusive_threshold)

    nugget_levels = NuggetService.categorize_nuggets_by_trust(
        trust_state, [test_nugget]
    )

    # Check availability: all content should be available
    available_content = [level.content for level in nugget_levels if level.available]
    unavailable_content = [
        level.content for level in nugget_levels if not level.available
    ]

    assert set(available_content) == {
        PUBLIC_CONTENT,
        PRIVILEGED_CONTENT,
        EXCLUSIVE_CONTENT,
    }
    assert unavailable_content == []


def test_categorize_nuggets_minimum_trust(static_character, test_nugget):
    """Test categorization with minimum trust"""
    public_threshold = NUGGET_THRESHOLDS[NuggetLayer.PUBLIC.name]
    trust_state = create_trust_state(static_character, public_threshold)

    nugget_levels = NuggetService.categorize_nuggets_by_trust(
        trust_state, [test_nugget]
    )

    # Check availability: only PUBLIC should be available
    available_content = [level.content for level in nugget_levels if level.available]
    unavailable_content = [
        level.content for level in nugget_levels if not level.available
    ]

    assert available_content == [PUBLIC_CONTENT]
    assert set(unavailable_content) == {PRIVILEGED_CONTENT, EXCLUSIVE_CONTENT}


def test_categorize_nuggets_maximum_trust(static_character, test_nugget):
    """Test categorization with maximum trust (1.0)"""
    trust_state = create_trust_state(static_character, TOTAL_TRUST_MAX)

    nugget_levels = NuggetService.categorize_nuggets_by_trust(
        trust_state, [test_nugget]
    )

    # Check availability: all content should be available
    available_content = [level.content for level in nugget_levels if level.available]
    unavailable_content = [
        level.content for level in nugget_levels if not level.available
    ]

    assert set(available_content) == {
        PUBLIC_CONTENT,
        PRIVILEGED_CONTENT,
        EXCLUSIVE_CONTENT,
    }
    assert unavailable_content == []


def test_categorize_nuggets_empty_list(static_character):
    """Test categorization with empty nugget list"""
    trust_state = create_trust_state(static_character, 0.5)

    nugget_levels = NuggetService.categorize_nuggets_by_trust(trust_state, [])

    assert nugget_levels == []
