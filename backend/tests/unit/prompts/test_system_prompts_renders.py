import pytest

from app.agents.prompts.import_prompts import render_prompt
from tests.fixtures.generate import (
    default_character,
    default_encounter,
    default_memories,
    default_player,
)
from tests.unit.prompts.utils import assert_template_rendered_completely


def get_base_template_context():
    """Get the base context that most templates need."""
    return {
        "max_response_length": 30,
        "character": default_character(),
        "player": default_player(),
        "encounter": default_encounter(),
    }


def test_conversation_agent_template_renders_without_jinja_elements():
    template_context = get_base_template_context()

    rendered_prompt = render_prompt("conversation_agent", template_context)
    assert_template_rendered_completely(rendered_prompt)


def test_negative_conversation_agent_template_renders_without_jinja_elements():
    template_context = get_base_template_context()
    template_context["memories"] = default_memories()

    rendered_prompt = render_prompt("negative_conversation_agent", template_context)
    assert_template_rendered_completely(rendered_prompt)


def test_challenge_agent_template_renders_without_jinja_elements():
    template_context = get_base_template_context()

    rendered_prompt = render_prompt("challenge_agent", template_context)
    assert_template_rendered_completely(rendered_prompt)


def test_challenge_agent_critical_success_template_renders_without_jinja_elements():
    template_context = get_base_template_context()

    rendered_prompt = render_prompt(
        "challenge_agent_critical_success", template_context
    )
    assert_template_rendered_completely(rendered_prompt)


def test_challenge_agent_critical_failure_template_renders_without_jinja_elements():
    template_context = get_base_template_context()

    rendered_prompt = render_prompt(
        "challenge_agent_critical_failure", template_context
    )
    assert_template_rendered_completely(rendered_prompt)


def test_influence_scoring_agent_template_renders_without_jinja_elements():
    template_context = {
        "character": default_character(),
        "player": default_player(),
        "encounter": default_encounter(),
    }

    rendered_prompt = render_prompt("influence_scoring_agent", template_context)
    assert_template_rendered_completely(rendered_prompt)


def test_personality_agent_template_renders_without_jinja_elements():
    template_context = {
        "character": default_character(),
    }

    rendered_prompt = render_prompt("personality_agent", template_context)
    assert_template_rendered_completely(rendered_prompt)


def test_communication_style_agent_template_renders_without_jinja_elements():
    template_context = {
        "character": default_character(),
        "max_response_length": 200,
        "style_profile": {
            "style": "Friendly",
            "style_summary": "Warm and welcoming conversationalist",
            "examples": ["Welcome friend!", "How may I help you?", "Stay a while!"],
        },
    }

    rendered_prompt = render_prompt("communication_style_agent", template_context)
    assert_template_rendered_completely(rendered_prompt)


def test_template_raises_exception_for_missing_required_field():
    """Test that templates raise exceptions when required fields are missing."""
    # Missing 'character' field which is required by most templates
    incomplete_context = {
        "max_response_length": 30,
        "player": default_player(),
        "encounter": default_encounter(),
    }

    with pytest.raises(RuntimeError, match="Template rendering failed"):
        render_prompt("conversation_agent", incomplete_context)
