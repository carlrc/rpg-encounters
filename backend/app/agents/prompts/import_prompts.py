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


def render_jinja_prompt(template_name: str, context: Dict[str, Any]) -> str:
    """Render a Jinja2 template with the given context variables."""
    current_dir = path.dirname(path.abspath(__file__))

    try:
        # Create Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(current_dir), undefined=StrictUndefined
        )
        template = env.get_template(f"{template_name}.jinja")

        # Render template with context
        rendered_prompt = template.render(**context)

        return rendered_prompt

    except Exception as e:
        logger.error(f"Failed to render Jinja template {template_name}: {e}")
        raise RuntimeError(f"Template rendering failed: {e}")
