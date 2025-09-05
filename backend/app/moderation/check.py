import logging
import os
import random
import re
from functools import lru_cache
from pathlib import Path

from langfuse import observe

from app.clients.openai_moderation import (
    ModerationResponse,
    OpenAIModerationClient,
    openai_flag,
    openai_scores,
    openai_scores_minors,
)

logger = logging.getLogger(__name__)

# Environment variable to skip moderation checks entirely
SKIP_MODERATION = os.getenv("SKIP_MODERATION", "false").lower() == "true"
OPEN_AI_MODERATION_THRESHOLD = float(os.getenv("OPEN_AI_MODERATION_THRESHOLD", 0.4))


@lru_cache(maxsize=2)
def load_word_list(filepath: str) -> set[str]:
    """Load words/phrases from a text file with LRU caching. Each line becomes a set item."""
    path = Path(filepath)
    if not path.exists():
        return set()

    with open(path, "r", encoding="utf-8") as f:
        return {line.strip().lower() for line in f.readlines() if line.strip()}


def compile_bad_content_regex(content_set: set[str]) -> re.Pattern:
    """Compile a regex pattern for a set of bad content."""
    # Escape special regex chars and join with OR
    escaped_content = [re.escape(content) for content in content_set]
    pattern = r"\b(?:" + "|".join(escaped_content) + r")\b"
    return re.compile(pattern, re.IGNORECASE)


# Load word lists from moderation directory
_moderation_dir = Path(__file__).parent
LUIS_WORDS = load_word_list(str(_moderation_dir / "luis_von_ahn_bad_words.txt"))
LDNOOBW_WORDS = load_word_list(str(_moderation_dir / "ldnoobw_words.text"))
BAD_CONTENT = LUIS_WORDS | LDNOOBW_WORDS
MODERATION_REGEX = compile_bad_content_regex(BAD_CONTENT)


@observe()
async def moderation_pipe(user_id: int, text: str) -> ModerationResponse | None:
    try:
        if MODERATION_REGEX.search(text):
            logger.warning(
                f"Moderation flag triggered for {user_id}. Checking with OpenAI..."
            )
            response = await OpenAIModerationClient().check(text=text)
            if not response.results:
                return None
            results = response.results[0]
            must_block = openai_flag(
                categories=results.categories
            ) or openai_scores_minors(results.category_scores.sexual_minors)
            should_block = openai_scores(
                scores=results.category_scores,
                breach_threshold=OPEN_AI_MODERATION_THRESHOLD,
            )

            return response if (must_block or should_block) else None
        else:
            return None
    except Exception as e:
        logger.error(f"Moderation pipeline failed: {e}")
        # Fail open
        return None


def get_random_moderation_response() -> str:
    """
    Return a random response message for when content is flagged by moderation.

    Returns:
        A randomly selected inappropriate content response message
    """
    responses = [
        "Whoa there! Let's keep things appropriate.",
        "That escalated quickly! How about we talk about literally anything else?",
        "I'm going to pretend I didn't hear that and give you a chance to try again.",
        "I think you might have me confused with someone who has bad taste",
        "I don't think that's quite appropriate.",
        "Did you really just say that?",
        "My mother always said if you can't say something nice, don't say anything at all. So...",
    ]

    return random.choice(responses)
