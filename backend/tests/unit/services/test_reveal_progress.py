from app.models.reveal import REVEAL_DEFAULT_THRESHOLDS, Reveal, RevealLayer
from app.services.reveal_progress import calculate_reveal_progress
from tests.fixtures.generate import create_inn_secrets_reveal

# Test constants
TEST_CHARACTER_ID = 1
TEST_REVEAL_ID = 1


def test_calculate_reveal_progress_no_layers_unlocked():
    """Test calculate_reveal_progress when influence is below all thresholds."""
    reveal = create_inn_secrets_reveal(TEST_CHARACTER_ID, TEST_REVEAL_ID)
    influence_score = (
        REVEAL_DEFAULT_THRESHOLDS[RevealLayer.STANDARD] - 1
    )  # Below standard threshold

    result = calculate_reveal_progress(reveal, influence_score)

    assert result["id"] == TEST_REVEAL_ID
    assert result["title"] == "Inn Secrets"
    assert result["progress"] == "0/3"
    assert result["unlocked_layers"] == 0
    assert result["total_layers"] == 3


def test_calculate_reveal_progress_one_layer_unlocked():
    """Test calculate_reveal_progress when influence meets standard threshold only."""
    reveal = create_inn_secrets_reveal(TEST_CHARACTER_ID, TEST_REVEAL_ID)
    influence_score = (
        REVEAL_DEFAULT_THRESHOLDS[RevealLayer.PRIVILEGED] - 1
    )  # Above standard, below privileged

    result = calculate_reveal_progress(reveal, influence_score)

    assert result["id"] == TEST_REVEAL_ID
    assert result["title"] == "Inn Secrets"
    assert result["progress"] == "1/3"
    assert result["unlocked_layers"] == 1
    assert result["total_layers"] == 3


def test_calculate_reveal_progress_two_layers_unlocked():
    """Test calculate_reveal_progress when influence meets privileged threshold."""
    reveal = create_inn_secrets_reveal(TEST_CHARACTER_ID, TEST_REVEAL_ID)
    influence_score = (
        REVEAL_DEFAULT_THRESHOLDS[RevealLayer.EXCLUSIVE] - 1
    )  # Above privileged, below exclusive

    result = calculate_reveal_progress(reveal, influence_score)

    assert result["id"] == TEST_REVEAL_ID
    assert result["title"] == "Inn Secrets"
    assert result["progress"] == "2/3"
    assert result["unlocked_layers"] == 2
    assert result["total_layers"] == 3


def test_calculate_reveal_progress_all_layers_unlocked():
    """Test calculate_reveal_progress when influence meets exclusive threshold."""
    reveal = create_inn_secrets_reveal(TEST_CHARACTER_ID, TEST_REVEAL_ID)
    influence_score = (
        REVEAL_DEFAULT_THRESHOLDS[RevealLayer.EXCLUSIVE] + 5
    )  # Above all thresholds

    result = calculate_reveal_progress(reveal, influence_score)

    assert result["id"] == TEST_REVEAL_ID
    assert result["title"] == "Inn Secrets"
    assert result["progress"] == "3/3"
    assert result["unlocked_layers"] == 3
    assert result["total_layers"] == 3


def test_calculate_reveal_progress_missing_level_2():
    """Test calculate_reveal_progress when level_2_content is None."""
    reveal = Reveal(
        id=TEST_REVEAL_ID,
        title="Test Reveal",
        character_ids=[TEST_CHARACTER_ID],
        level_1_content="Standard content",
        level_2_content=None,  # Missing level 2
        level_3_content="Exclusive content",
    )

    influence_score = (
        REVEAL_DEFAULT_THRESHOLDS[RevealLayer.EXCLUSIVE] - 1
    )  # Above privileged threshold

    result = calculate_reveal_progress(reveal, influence_score)

    assert result["id"] == TEST_REVEAL_ID
    assert result["title"] == "Test Reveal"
    assert result["progress"] == "2/2"  # Only 2 layers exist
    assert result["unlocked_layers"] == 2  # Standard + exclusive unlocked
    assert result["total_layers"] == 2


def test_calculate_reveal_progress_only_level_1():
    """Test calculate_reveal_progress when only level_1_content exists."""
    reveal = Reveal(
        id=TEST_REVEAL_ID,
        title="Test Reveal",
        character_ids=[TEST_CHARACTER_ID],
        level_1_content="Standard content",
        level_2_content=None,
        level_3_content=None,
    )

    influence_score = (
        REVEAL_DEFAULT_THRESHOLDS[RevealLayer.EXCLUSIVE] + 5
    )  # Above all thresholds

    result = calculate_reveal_progress(reveal, influence_score)

    assert result["id"] == TEST_REVEAL_ID
    assert result["title"] == "Test Reveal"
    assert result["progress"] == "3/1"  # All thresholds met but only 1 layer exists
    assert result["unlocked_layers"] == 3  # All thresholds unlocked
    assert result["total_layers"] == 1


def test_calculate_reveal_progress_exact_threshold():
    """Test calculate_reveal_progress when influence exactly equals thresholds."""
    reveal = create_inn_secrets_reveal(TEST_CHARACTER_ID, TEST_REVEAL_ID)
    influence_score = REVEAL_DEFAULT_THRESHOLDS[
        RevealLayer.PRIVILEGED
    ]  # Exactly equals privileged threshold

    result = calculate_reveal_progress(reveal, influence_score)

    assert result["id"] == TEST_REVEAL_ID
    assert result["title"] == "Inn Secrets"
    assert result["progress"] == "2/3"
    assert result["unlocked_layers"] == 2
    assert result["total_layers"] == 3
