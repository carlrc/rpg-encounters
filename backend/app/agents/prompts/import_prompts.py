import logging
from os import path

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
