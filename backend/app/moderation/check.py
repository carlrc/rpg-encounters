import logging
import random
import re
from functools import lru_cache
from pathlib import Path
from typing import Union

from langfuse import observe

from app.clients.openai_moderation import (
    ModerationResponse,
    OpenAIModerationClient,
    openai_illegal_flag,
    openai_minors_score,
    openai_score,
)
from app.models.character import CharacterCreate, CharacterUpdate
from app.utils import get_or_throw

logger = logging.getLogger(__name__)

# Environment variable to skip moderation checks entirely
SKIP_MODERATION = get_or_throw("SKIP_MODERATION").lower() == "true"
INAPPROPRIATE_CONTENT_DEFAULT = "INAPPROPRIATE_CONTENT"


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


@observe(capture_input=False, capture_output=False)
async def moderation_pipe(user_id: int, text: str) -> ModerationResponse | None:
    if SKIP_MODERATION:
        return None

    # Do not fail open (e.g., default to None)
    failover = ModerationResponse(id="failover", model="OpenAI")
    try:
        # Check text against bad word lists
        if MODERATION_REGEX.search(text):
            logger.warning(
                f"Moderation flag triggered for user {user_id}. Checking moderation service..."
            )
            response = await OpenAIModerationClient().check(text=text)
            if not response.results:
                return failover
            results = response.results[0]
            # Check against illegal material
            must_block = openai_illegal_flag(
                categories=results.categories
            ) or openai_minors_score(results.category_scores.sexual_minors)
            # Check against custom moderation threshold
            should_block = openai_score(results.category_scores.sexual)

            return response if (must_block or should_block) else None
        else:
            return None
    except Exception as e:
        logger.error(f"Moderation pipeline failed: {e}")
        return failover


def get_random_moderation_response() -> str:
    """Return a random response message for when content is flagged by moderation."""

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


async def moderate_text(user_id: int, text: str) -> str:
    """Check text content and return either the original text or inappropriate content message."""

    if not text or not text.strip():
        return text

    moderation_result = await moderation_pipe(user_id=user_id, text=text)

    if moderation_result:
        logger.warning(f"User {user_id} text flagged. Using default content...")
        return INAPPROPRIATE_CONTENT_DEFAULT

    return text


async def moderate_character(
    user_id: int, character_data: Union[CharacterCreate, CharacterUpdate]
) -> Union[CharacterCreate, CharacterUpdate]:
    # TODO: This should use asyncio.gather in case someone makes an entire inappropriate character
    if character_data.name:
        character_data.name = await moderate_text(
            user_id=user_id, text=character_data.name
        )
    if character_data.background:
        character_data.background = await moderate_text(
            user_id=user_id, text=character_data.background
        )
    if character_data.motivation:
        character_data.motivation = await moderate_text(
            user_id=user_id, text=character_data.motivation
        )
    if character_data.communication_style:
        character_data.communication_style = await moderate_text(
            user_id=user_id, text=character_data.communication_style
        )

    return character_data
