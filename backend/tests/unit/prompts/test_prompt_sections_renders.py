from app.agents.prompts.import_prompts import render_prompt_section
from tests.fixtures.generate import (
    default_character,
    default_encounter,
    default_memories,
    default_player,
)
from tests.unit.prompts.utils import assert_template_rendered_completely


def test_mechanics_section_renders_without_jinja_elements():
    rendered_section = render_prompt_section("mechanics", {})
    assert_template_rendered_completely(rendered_section)


def test_character_base_section_renders_without_jinja_elements():
    context = {
        "character": default_character(),
    }

    rendered_section = render_prompt_section("character_base", context)
    assert_template_rendered_completely(rendered_section)


def test_current_task_section_renders_without_jinja_elements():
    context = {
        "player": default_player(),
        "encounter": default_encounter(),
    }

    rendered_section = render_prompt_section("current_task", context)
    assert_template_rendered_completely(rendered_section)


def test_absolute_rules_section_renders_without_jinja_elements():
    context = {
        "max_response_length": 30,
    }

    rendered_section = render_prompt_section("absolute_rules", context)
    assert_template_rendered_completely(rendered_section)


def test_communication_style_section_renders_without_jinja_elements():
    context = {
        "character": default_character(),
    }

    rendered_section = render_prompt_section("communication_style", context)
    assert_template_rendered_completely(rendered_section)


def test_memories_section_renders_without_jinja_elements():
    context = {
        "memories": default_memories(),
    }

    rendered_section = render_prompt_section("memories", context)
    assert_template_rendered_completely(rendered_section)


def test_memories_section_renders_empty_when_no_memories():
    context = {
        "memories": [],
    }

    rendered_section = render_prompt_section("memories", context)
    assert_template_rendered_completely(rendered_section)
    # Should render but be mostly empty due to conditional logic
    assert "No memories available for this character" in rendered_section
