import logging
from os import path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, StrictUndefined

logger = logging.getLogger(__name__)


def import_system_prompt(prefix: str) -> str:
    """Load the system prompt from the markdown file."""
    current_dir = path.dirname(path.abspath(__file__))
    prompt_path = path.join(current_dir, f"{prefix}_system_prompt.md")
    try:
        with open(prompt_path, "r") as f:
            return f.read()

    except FileNotFoundError:
        logger.error("System prompt file not found.")
        raise RuntimeError()


def _render_template(
    template_dir: str, template_name: str, context: Dict[str, Any]
) -> str:
    """Shared helper function to render a Jinja2 template with the given context variables."""
    try:
        # Create Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(template_dir), undefined=StrictUndefined
        )
        template = env.get_template(f"{template_name}.jinja.md")

        # Render template with context
        rendered_prompt = template.render(**context)

        return rendered_prompt

    except Exception as e:
        logger.error(f"Failed to render Jinja template {template_name}: {e}")
        raise RuntimeError(f"Template rendering failed: {e}")


def render_prompt(template_name: str, context: Dict[str, Any]) -> str:
    """Render a Jinja2 template with the given context variables."""
    current_dir = path.dirname(path.abspath(__file__))
    return _render_template(current_dir, template_name, context)


def render_prompt_section(template_name: str, context: Dict[str, Any]) -> str:
    """Render a Jinja2 template from the sections subdirectory with the given context variables."""
    current_dir = path.dirname(path.abspath(__file__))
    sections_dir = path.join(current_dir, "sections")
    return _render_template(sections_dir, template_name, context)
