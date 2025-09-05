from app.agents.agent_output import ConversationAgentOutput
from app.models.reveal import REVEAL_DEFAULT_THRESHOLDS, RevealLayer
from app.services.conversation_manager import select_response
from tests.fixtures.generate import create_inn_secrets_reveal

# Test constants
TEST_CHARACTER_ID = 1
TEST_REVEAL_ID = 1

# Response constants
NEGATIVE_RESPONSE = "Go away!"
STANDARD_RESPONSE = "Hello there."
PRIVILEGED_RESPONSE = "Welcome, friend."
EXCLUSIVE_RESPONSE = "Welcome, honored guest."


def create_test_agent_output(
    reveal_id: int = TEST_REVEAL_ID,
) -> ConversationAgentOutput:
    """Create a test agent output with standard responses."""
    return ConversationAgentOutput(
        reveal_id=reveal_id,
        negative_response=NEGATIVE_RESPONSE,
        standard_response=STANDARD_RESPONSE,
        privileged_response=PRIVILEGED_RESPONSE,
        exclusive_response=EXCLUSIVE_RESPONSE,
    )


def test_select_response_negative_attitude():
    """Test select_response returns negative response when influence is below standard threshold."""
    reveals = [create_inn_secrets_reveal(TEST_CHARACTER_ID, TEST_REVEAL_ID)]
    agent_result = create_test_agent_output()
    influence_score = (
        REVEAL_DEFAULT_THRESHOLDS[RevealLayer.STANDARD] - 1
    )  # Below standard threshold

    response, layer = select_response(reveals, agent_result, influence_score)

    assert response == NEGATIVE_RESPONSE
    assert layer == RevealLayer.NEGATIVE


def test_select_response_standard():
    """Test select_response returns standard response when influence meets standard threshold."""
    reveals = [create_inn_secrets_reveal(TEST_CHARACTER_ID, TEST_REVEAL_ID)]
    agent_result = create_test_agent_output()
    influence_score = (
        REVEAL_DEFAULT_THRESHOLDS[RevealLayer.PRIVILEGED] - 1
    )  # Above standard, below privileged

    response, layer = select_response(reveals, agent_result, influence_score)

    assert response == STANDARD_RESPONSE
    assert layer == RevealLayer.STANDARD


def test_select_response_privileged():
    """Test select_response returns privileged response when influence meets privileged threshold."""
    reveals = [create_inn_secrets_reveal(TEST_CHARACTER_ID, TEST_REVEAL_ID)]
    agent_result = create_test_agent_output()
    influence_score = (
        REVEAL_DEFAULT_THRESHOLDS[RevealLayer.EXCLUSIVE] - 1
    )  # Above privileged, below exclusive

    response, layer = select_response(reveals, agent_result, influence_score)

    assert response == PRIVILEGED_RESPONSE
    assert layer == RevealLayer.PRIVILEGED


def test_select_response_exclusive():
    """Test select_response returns exclusive response when influence meets exclusive threshold."""
    reveals = [create_inn_secrets_reveal(TEST_CHARACTER_ID, TEST_REVEAL_ID)]
    agent_result = create_test_agent_output()
    influence_score = (
        REVEAL_DEFAULT_THRESHOLDS[RevealLayer.EXCLUSIVE] + 2
    )  # Above exclusive

    response, layer = select_response(reveals, agent_result, influence_score)

    assert response == EXCLUSIVE_RESPONSE
    assert layer == RevealLayer.EXCLUSIVE


def test_select_response_no_reveals():
    """Test select_response returns standard response when no reveals provided."""
    reveals = []
    agent_result = create_test_agent_output(reveal_id=None)
    influence_score = 15

    response, layer = select_response(reveals, agent_result, influence_score)

    assert response == STANDARD_RESPONSE
    assert layer == RevealLayer.STANDARD


def test_select_response_no_reveals_negative_attitude():
    """Test select_response returns negative response when no reveals and low influence."""
    reveals = []
    agent_result = create_test_agent_output(reveal_id=None)
    influence_score = (
        REVEAL_DEFAULT_THRESHOLDS[RevealLayer.STANDARD] - 1
    )  # Below standard threshold

    response, layer = select_response(reveals, agent_result, influence_score)

    assert response == NEGATIVE_RESPONSE
    assert layer == RevealLayer.NEGATIVE


def test_select_response_invalid_reveal_id():
    """Test select_response defaults to standard when agent returns invalid reveal_id."""
    reveals = [create_inn_secrets_reveal(TEST_CHARACTER_ID, TEST_REVEAL_ID)]
    agent_result = create_test_agent_output(
        reveal_id=999
    )  # Invalid ID not in reveals list
    influence_score = 15

    response, layer = select_response(reveals, agent_result, influence_score)

    assert response == STANDARD_RESPONSE
    assert layer == RevealLayer.STANDARD


def test_select_response_missing_privileged_response():
    """Test select_response falls back to standard when privileged response is None."""
    reveals = [create_inn_secrets_reveal(TEST_CHARACTER_ID, TEST_REVEAL_ID)]
    agent_result = ConversationAgentOutput(
        reveal_id=TEST_REVEAL_ID,
        negative_response=NEGATIVE_RESPONSE,
        standard_response=STANDARD_RESPONSE,
        privileged_response=None,  # Missing privileged response
        exclusive_response=EXCLUSIVE_RESPONSE,
    )
    influence_score = 17  # Above privileged threshold

    response, layer = select_response(reveals, agent_result, influence_score)

    assert response == STANDARD_RESPONSE
    assert layer == RevealLayer.STANDARD
