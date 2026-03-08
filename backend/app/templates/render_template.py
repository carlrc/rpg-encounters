import logging
from os import path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, StrictUndefined

logger = logging.getLogger(__name__)


def render_email_template(template_name: str, context: Dict[str, Any]) -> str:
    """Render an email template using Jinja2 with the given context variables."""
    try:
        current_dir = path.dirname(path.abspath(__file__))

        env = Environment(
            loader=FileSystemLoader(current_dir), undefined=StrictUndefined
        )

        # Load and render the template
        template = env.get_template(template_name)
        rendered_html = template.render(**context)

        return rendered_html

    except Exception as e:
        logger.error(f"Failed to render email template {template_name}: {e}")
        raise
