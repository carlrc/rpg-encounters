from app.clients.openai_moderation import Categories, openai_flag

# Base safe categories - all False
# Using a dict with proper field names/aliases to create the model
SAFE_CATEGORIES = Categories.model_validate(
    {
        "sexual": False,
        "hate": False,
        "harassment": False,
        "violence": False,
        "self-harm": False,
        "sexual/minors": False,
        "hate/threatening": False,
        "violence/graphic": False,
        "self-harm/intent": False,
        "self-harm/instructions": False,
        "harassment/threatening": False,
        "illicit": False,
        "illicit/violent": False,
    }
)


def test_flag_blocks_sexual_minors():
    """Test that sexual_minors content is blocked"""
    categories = SAFE_CATEGORIES.model_copy()
    categories.sexual_minors = True

    assert openai_flag(categories) is True


def test_flag_blocks_self_harm():
    """Test that self_harm content is blocked"""
    categories = SAFE_CATEGORIES.model_copy()
    categories.self_harm = True

    assert openai_flag(categories) is True


def test_flag_blocks_self_harm_intent():
    """Test that self_harm_intent content is blocked"""
    categories = SAFE_CATEGORIES.model_copy()
    categories.self_harm_intent = True

    assert openai_flag(categories) is True


def test_flag_blocks_self_harm_instructions():
    """Test that self_harm_instructions content is blocked"""
    categories = SAFE_CATEGORIES.model_copy()
    categories.self_harm_instructions = True

    assert openai_flag(categories) is True


def test_flag_blocks_hate_threatening():
    """Test that hate_threatening content is blocked"""
    categories = SAFE_CATEGORIES.model_copy()
    categories.hate_threatening = True

    assert openai_flag(categories) is True


def test_flag_allows_safe_content():
    """Test that safe content is not blocked"""
    categories = SAFE_CATEGORIES.model_copy()

    assert openai_flag(categories) is False


def test_flag_allows_rpg_violence():
    """Test that regular violence (RPG context) is not blocked"""
    categories = SAFE_CATEGORIES.model_copy()
    categories.violence = True

    assert openai_flag(categories) is False


def test_flag_allows_graphic_violence():
    """Test that graphic violence alone is not blocked"""
    categories = SAFE_CATEGORIES.model_copy()
    categories.violence_graphic = True

    assert openai_flag(categories) is False


def test_flag_allows_sexual_content():
    """Test that adult sexual content (not minors) is not blocked"""
    categories = SAFE_CATEGORIES.model_copy()
    categories.sexual = True

    assert openai_flag(categories) is False


def test_flag_allows_mild_harassment():
    """Test that non-threatening harassment is not blocked"""
    categories = SAFE_CATEGORIES.model_copy()
    categories.harassment = True

    assert openai_flag(categories) is False


def test_flag_allows_harassment_threatening():
    """Test that harassment_threatening alone is not blocked"""
    categories = SAFE_CATEGORIES.model_copy()
    categories.harassment_threatening = True

    assert openai_flag(categories) is False


def test_flag_allows_non_threatening_hate():
    """Test that non-threatening hate speech is not blocked"""
    categories = SAFE_CATEGORIES.model_copy()
    categories.hate = True

    assert openai_flag(categories) is False


def test_flag_blocks_multiple_violations():
    """Test that multiple violations still result in block"""
    categories = SAFE_CATEGORIES.model_copy()
    categories.self_harm = True
    categories.sexual_minors = True
    categories.hate_threatening = True

    assert openai_flag(categories) is True
