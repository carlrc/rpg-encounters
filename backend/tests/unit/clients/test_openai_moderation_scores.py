from app.clients.openai_moderation import CategoryScores, openai_scores

# Base safe scores - all very low
SAFE_SCORES = CategoryScores.model_validate(
    {
        "sexual": 0.000001,
        "hate": 0.000001,
        "harassment": 0.000001,
        "violence": 0.000001,
        "self-harm": 0.000001,
        "sexual/minors": 0.000001,
        "hate/threatening": 0.000001,
        "violence/graphic": 0.000001,
        "self-harm/intent": 0.000001,
        "self-harm/instructions": 0.000001,
        "harassment/threatening": 0.000001,
        "illicit": 0.000001,
        "illicit/violent": 0.000001,
    }
)

DEFAULT_THRESHOLD = 0.4


def test_scores_blocks_violence_and_hate():
    """Test that violence + hate above threshold triggers block"""
    scores = SAFE_SCORES.model_copy()
    scores.violence = 0.5
    scores.hate = 0.5

    assert openai_scores(scores, DEFAULT_THRESHOLD) is True


def test_scores_blocks_violence_and_harassment_threatening():
    """Test that violence + harassment_threatening above threshold triggers block"""
    scores = SAFE_SCORES.model_copy()
    scores.violence = 0.5
    scores.harassment_threatening = 0.5

    assert openai_scores(scores, DEFAULT_THRESHOLD) is True


def test_scores_blocks_violence_and_self_harm():
    """Test that violence + self_harm above threshold triggers block"""
    scores = SAFE_SCORES.model_copy()
    scores.violence = 0.5
    scores.self_harm = 0.5

    assert openai_scores(scores, DEFAULT_THRESHOLD) is True


def test_scores_blocks_violence_and_self_harm_intent():
    """Test that violence + self_harm_intent above threshold triggers block"""
    scores = SAFE_SCORES.model_copy()
    scores.violence = 0.5
    scores.self_harm_intent = 0.5

    assert openai_scores(scores, DEFAULT_THRESHOLD) is True


def test_scores_blocks_violence_and_self_harm_instructions():
    """Test that violence + self_harm_instructions above threshold triggers block"""
    scores = SAFE_SCORES.model_copy()
    scores.violence = 0.5
    scores.self_harm_instructions = 0.5

    assert openai_scores(scores, DEFAULT_THRESHOLD) is True


def test_scores_allows_violence_only():
    """Test that violence alone (without other categories) doesn't block"""
    scores = SAFE_SCORES.model_copy()
    scores.violence = 0.5

    assert openai_scores(scores, DEFAULT_THRESHOLD) is False


def test_scores_allows_other_categories_only():
    """Test that other categories without violence don't block"""
    scores = SAFE_SCORES.model_copy()
    scores.hate = 0.5
    scores.harassment_threatening = 0.5
    scores.self_harm = 0.5

    assert openai_scores(scores, DEFAULT_THRESHOLD) is False


def test_scores_respects_threshold():
    """Test that scores below threshold don't trigger block"""
    scores = SAFE_SCORES.model_copy()
    scores.violence = 0.3
    scores.hate = 0.3

    assert openai_scores(scores, DEFAULT_THRESHOLD) is False


def test_scores_with_different_thresholds():
    """Test that function works with different breach thresholds"""
    scores = SAFE_SCORES.model_copy()
    scores.violence = 0.5
    scores.hate = 0.5

    # Should block with low threshold
    assert openai_scores(scores, 0.1) is True

    # Should not block with high threshold
    assert openai_scores(scores, 0.8) is False


def test_scores_allows_safe_content():
    """Test that all safe scores don't trigger block"""
    scores = SAFE_SCORES.model_copy()

    assert openai_scores(scores, DEFAULT_THRESHOLD) is False


def test_scores_blocks_multiple_combinations():
    """Test that violence + multiple other categories still blocks"""
    scores = SAFE_SCORES.model_copy()
    scores.violence = 0.5
    scores.hate = 0.5
    scores.self_harm = 0.5
    scores.harassment_threatening = 0.5

    assert openai_scores(scores, DEFAULT_THRESHOLD) is True


def test_scores_with_scientific_notation():
    """Test that function handles scientific notation properly"""
    scores = SAFE_SCORES.model_copy()
    scores.violence = 5e-1  # 0.5
    scores.hate = 6e-1  # 0.6

    # Should block when both above threshold
    assert openai_scores(scores, DEFAULT_THRESHOLD) is True

    # Should not block when below threshold
    scores.violence = 3e-1  # 0.3
    scores.hate = 2e-1  # 0.2
    assert openai_scores(scores, DEFAULT_THRESHOLD) is False
