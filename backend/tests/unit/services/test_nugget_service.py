import pytest
from app.services.nugget_service import NuggetService
from app.models.nugget import NuggetLayer, TrustNugget, NUGGET_THRESHOLDS
from app.models.trust import BASE_TRUST_MAX, EARNED_TRUST_MAX, TOTAL_TRUST_MAX, TrustState
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
        level_3_content=EXCLUSIVE_CONTENT
    )


def create_trust_state(static_character, total_trust: float):
    """Helper to create TrustState with specific total trust level"""
    # Calculate base_trust and earned_trust to achieve desired total_trust
    # Keep it simple: use base_trust primarily, earned_trust as adjustment
    base_trust = min(BASE_TRUST_MAX, total_trust)
    earned_trust = max(-BASE_TRUST_MAX, min(EARNED_TRUST_MAX, total_trust - base_trust))  # Clamp earned trust
    
    return TrustState(
        character_id=static_character.id,
        player_id=999,  # Dynamic player ID
        base_trust=base_trust,
        earned_trust=earned_trust
    )


def test_get_trust_threshold_public():
    """Test PUBLIC layer threshold"""
    threshold = NuggetService.get_trust_threshold(NuggetLayer.PUBLIC)
    expected = NUGGET_THRESHOLDS[NuggetLayer.PUBLIC.name]
    assert threshold == expected


def test_get_trust_threshold_privileged():
    """Test PRIVILEGED layer threshold"""
    threshold = NuggetService.get_trust_threshold(NuggetLayer.PRIVILEGED)
    expected = NUGGET_THRESHOLDS[NuggetLayer.PRIVILEGED.name]
    assert threshold == expected


def test_get_trust_threshold_exclusive():
    """Test EXCLUSIVE layer threshold"""
    threshold = NuggetService.get_trust_threshold(NuggetLayer.EXCLUSIVE)
    expected = NUGGET_THRESHOLDS[NuggetLayer.EXCLUSIVE.name]
    assert threshold == expected


def test_can_always_access_nugget_public_layer():
    """Test access to PUBLIC layer with various trust levels"""
    # PUBLIC should always be accessible
    public_threshold = NUGGET_THRESHOLDS[NuggetLayer.PUBLIC.name]
    assert NuggetService.can_access_nugget(public_threshold, NuggetLayer.PUBLIC) == True
    assert NuggetService.can_access_nugget(0.3, NuggetLayer.PUBLIC) == True
    assert NuggetService.can_access_nugget(NUGGET_THRESHOLDS[NuggetLayer.PRIVILEGED.name], NuggetLayer.PUBLIC) == True
    assert NuggetService.can_access_nugget(NUGGET_THRESHOLDS[NuggetLayer.EXCLUSIVE.name], NuggetLayer.PUBLIC) == True
    assert NuggetService.can_access_nugget(TOTAL_TRUST_MAX, NuggetLayer.PUBLIC) == True


def test_can_access_nugget_privileged_layer():
    """Test successful access to PRIVILEGED layer at and above threshold"""
    privileged_threshold = NUGGET_THRESHOLDS[NuggetLayer.PRIVILEGED.name]
    
    # At and above threshold
    assert NuggetService.can_access_nugget(privileged_threshold, NuggetLayer.PRIVILEGED) == True
    assert NuggetService.can_access_nugget(BASE_TRUST_MAX, NuggetLayer.PRIVILEGED) == True
    assert NuggetService.can_access_nugget(NUGGET_THRESHOLDS[NuggetLayer.EXCLUSIVE.name], NuggetLayer.PRIVILEGED) == True
    assert NuggetService.can_access_nugget(TOTAL_TRUST_MAX, NuggetLayer.PRIVILEGED) == True


def test_cannot_access_nugget_privileged_layer():
    """Test denied access to PRIVILEGED layer below threshold"""
    privileged_threshold = NUGGET_THRESHOLDS[NuggetLayer.PRIVILEGED.name]
    
    # Below threshold
    assert NuggetService.can_access_nugget(NUGGET_THRESHOLDS[NuggetLayer.PUBLIC.name], NuggetLayer.PRIVILEGED) == False
    assert NuggetService.can_access_nugget(privileged_threshold - 0.01, NuggetLayer.PRIVILEGED) == False


def test_can_access_nugget_exclusive_layer():
    """Test successful access to EXCLUSIVE layer at and above threshold"""
    exclusive_threshold = NUGGET_THRESHOLDS[NuggetLayer.EXCLUSIVE.name]
    
    # At and above threshold
    assert NuggetService.can_access_nugget(exclusive_threshold, NuggetLayer.EXCLUSIVE) == True
    assert NuggetService.can_access_nugget(TOTAL_TRUST_MAX - 0.1, NuggetLayer.EXCLUSIVE) == True
    assert NuggetService.can_access_nugget(TOTAL_TRUST_MAX, NuggetLayer.EXCLUSIVE) == True


def test_cannot_access_nugget_exclusive_layer():
    """Test denied access to EXCLUSIVE layer below threshold"""
    exclusive_threshold = NUGGET_THRESHOLDS[NuggetLayer.EXCLUSIVE.name]
    
    # Below threshold
    assert NuggetService.can_access_nugget(NUGGET_THRESHOLDS[NuggetLayer.PUBLIC.name], NuggetLayer.EXCLUSIVE) == False
    assert NuggetService.can_access_nugget(NUGGET_THRESHOLDS[NuggetLayer.PRIVILEGED.name], NuggetLayer.EXCLUSIVE) == False
    assert NuggetService.can_access_nugget(exclusive_threshold - 0.01, NuggetLayer.EXCLUSIVE) == False


def test_categorize_nuggets_below_privileged_threshold(static_character, test_nugget):
    """Test categorization just below PRIVILEGED threshold"""
    privileged_threshold = NUGGET_THRESHOLDS[NuggetLayer.PRIVILEGED.name]
    trust_state = create_trust_state(static_character, privileged_threshold - 0.01)
    
    available, unavailable = NuggetService.categorize_nuggets_by_trust(
        trust_state, [test_nugget]
    )
    
    # Should only have PUBLIC content
    assert available == [PUBLIC_CONTENT]
    assert set(unavailable) == {PRIVILEGED_CONTENT, EXCLUSIVE_CONTENT}


def test_categorize_nuggets_at_privileged_threshold(static_character, test_nugget):
    """Test categorization exactly at PRIVILEGED threshold"""
    privileged_threshold = NUGGET_THRESHOLDS[NuggetLayer.PRIVILEGED.name]
    trust_state = create_trust_state(static_character, privileged_threshold)
    
    available, unavailable = NuggetService.categorize_nuggets_by_trust(
        trust_state, [test_nugget]
    )
    
    # Should have PUBLIC + PRIVILEGED content
    assert set(available) == {PUBLIC_CONTENT, PRIVILEGED_CONTENT}
    assert unavailable == [EXCLUSIVE_CONTENT]


def test_categorize_nuggets_below_exclusive_threshold(static_character, test_nugget):
    """Test categorization just below EXCLUSIVE threshold"""
    exclusive_threshold = NUGGET_THRESHOLDS[NuggetLayer.EXCLUSIVE.name]
    trust_state = create_trust_state(static_character, exclusive_threshold - 0.01)
    
    available, unavailable = NuggetService.categorize_nuggets_by_trust(
        trust_state, [test_nugget]
    )
    
    # Should have PUBLIC + PRIVILEGED content
    assert set(available) == {PUBLIC_CONTENT, PRIVILEGED_CONTENT}
    assert unavailable == [EXCLUSIVE_CONTENT]


def test_categorize_nuggets_at_exclusive_threshold(static_character, test_nugget):
    """Test categorization exactly at EXCLUSIVE threshold"""
    exclusive_threshold = NUGGET_THRESHOLDS[NuggetLayer.EXCLUSIVE.name]
    trust_state = create_trust_state(static_character, exclusive_threshold)
    
    available, unavailable = NuggetService.categorize_nuggets_by_trust(
        trust_state, [test_nugget]
    )
    
    # Should have all content
    assert set(available) == {PUBLIC_CONTENT, PRIVILEGED_CONTENT, EXCLUSIVE_CONTENT}
    assert unavailable == []


def test_categorize_nuggets_minimum_trust(static_character, test_nugget):
    """Test categorization with minimum trust"""
    public_threshold = NUGGET_THRESHOLDS[NuggetLayer.PUBLIC.name]
    trust_state = create_trust_state(static_character, public_threshold)
    
    available, unavailable = NuggetService.categorize_nuggets_by_trust(
        trust_state, [test_nugget]
    )
    
    # Should only have PUBLIC content
    assert available == [PUBLIC_CONTENT]
    assert set(unavailable) == {PRIVILEGED_CONTENT, EXCLUSIVE_CONTENT}


def test_categorize_nuggets_maximum_trust(static_character, test_nugget):
    """Test categorization with maximum trust (1.0)"""
    trust_state = create_trust_state(static_character, TOTAL_TRUST_MAX)
    
    available, unavailable = NuggetService.categorize_nuggets_by_trust(
        trust_state, [test_nugget]
    )
    
    # Should have all content
    assert set(available) == {PUBLIC_CONTENT, PRIVILEGED_CONTENT, EXCLUSIVE_CONTENT}
    assert unavailable == []


def test_categorize_nuggets_empty_list(static_character):
    """Test categorization with empty nugget list"""
    trust_state = create_trust_state(static_character, 0.5)
    
    available, unavailable = NuggetService.categorize_nuggets_by_trust(
        trust_state, []
    )
    
    assert available == []
    assert unavailable == []
