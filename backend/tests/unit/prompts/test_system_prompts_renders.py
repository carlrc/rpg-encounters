import pytest

from app.agents.prompts.import_prompts import render_prompt, render_prompt_section
from app.agents.prompts.limits import STANDARD_RESPONSE_WORD_LENGTH
from tests.fixtures.generate import (
    default_character,
    default_encounter,
    default_memories,
    default_player,
    default_reveals,
)
from tests.unit.prompts.utils import assert_template_rendered_completely


def get_base_template_context():
    """Get the base context that most templates need."""
    return {
        "max_response_length": STANDARD_RESPONSE_WORD_LENGTH,
        "character": default_character(),
        "player": default_player(),
        "encounter": default_encounter(),
    }


def test_conversation_agent_template_renders():
    template_context = get_base_template_context()
    template_context["memories"] = default_memories()
    template_context["reveals"] = default_reveals()

    rendered_prompt = render_prompt("conversation_agent", template_context)
    assert_template_rendered_completely(rendered_prompt)


def test_negative_conversation_agent_template_renders():
    template_context = get_base_template_context()
    template_context["memories"] = default_memories()

    rendered_prompt = render_prompt("negative_conversation_agent", template_context)
    assert_template_rendered_completely(rendered_prompt)


def test_challenge_agent_template_renders():
    template_context = get_base_template_context()
    template_context["memories"] = default_memories()
    template_context["filtered_reveals"] = ["A hidden room is available."]

    rendered_prompt = render_prompt("challenge_agent", template_context)
    assert_template_rendered_completely(rendered_prompt)


def test_challenge_agent_critical_success_template_renders():
    template_context = get_base_template_context()
    template_context["memories"] = default_memories()
    template_context["filtered_reveals"] = ["A hidden room is available."]

    rendered_prompt = render_prompt(
        "challenge_agent_critical_success", template_context
    )
    assert_template_rendered_completely(rendered_prompt)


def test_challenge_agent_critical_failure_template_renders():
    template_context = get_base_template_context()
    template_context["memories"] = []
    template_context["filtered_reveals"] = []

    rendered_prompt = render_prompt(
        "challenge_agent_critical_failure", template_context
    )
    assert_template_rendered_completely(rendered_prompt)


def test_influence_scoring_agent_template_renders():
    template_context = {
        "character": default_character(),
        "player": default_player(),
        "encounter": default_encounter(),
    }

    rendered_prompt = render_prompt("influence_scoring_agent", template_context)
    assert_template_rendered_completely(rendered_prompt)


def test_personality_agent_template_renders():
    template_context = {
        "character": default_character(),
    }

    rendered_prompt = render_prompt("personality_agent", template_context)
    assert_template_rendered_completely(rendered_prompt)


def test_communication_style_agent_template_renders():
    template_context = {
        "character": default_character(),
        "max_response_length": STANDARD_RESPONSE_WORD_LENGTH,
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
        "max_response_length": STANDARD_RESPONSE_WORD_LENGTH,
        "player": default_player(),
        "encounter": default_encounter(),
    }

    with pytest.raises(RuntimeError, match="Template rendering failed"):
        render_prompt("conversation_agent", incomplete_context)


def test_memories_section_renders_without_memories():
    rendered_prompt = render_prompt_section("memories", {})
    assert "No memories available" in rendered_prompt


def test_reveals_section_renders_without_reveals():
    rendered_prompt = render_prompt_section("reveals", {})
    assert "No reveals available" in rendered_prompt
