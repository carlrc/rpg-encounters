import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class RateLimitEntry(BaseModel):
    count: int
    first_request_time: datetime


_EMAIL_REQUESTS: Dict[str, RateLimitEntry] = {}
_LOCK = asyncio.Lock()
_CLEANUP_COUNTER = 0
_CLEANUP_INTERVAL = 100
_EMAIL_COUNT_MAX = 2


def _cleanup_expired_entries() -> None:
    """Remove expired entries from the rate limit dictionary."""
    current_time = datetime.now()
    expired_emails = []

    for email, entry in _EMAIL_REQUESTS.items():
        time_since_first = current_time - entry.first_request_time
        if time_since_first >= timedelta(minutes=10):
            expired_emails.append(email)

    for email in expired_emails:
        del _EMAIL_REQUESTS[email]


async def check_email_rate_limit(email: str) -> bool:
    """Check if email is rate limited. Raises HTTPException if rate limit exceeded."""

    async with _LOCK:
        global _CLEANUP_COUNTER
        current_time = datetime.now()

        # Periodic cleanup to prevent unbounded memory growth
        _CLEANUP_COUNTER += 1
        if _CLEANUP_COUNTER % _CLEANUP_INTERVAL == 0:
            logger.info("Cleaning up email cache...")
            _cleanup_expired_entries()

        email_limit = _EMAIL_REQUESTS.get(email)

        # Doesn't exist - create entry
        if not email_limit:
            _EMAIL_REQUESTS[email] = RateLimitEntry(
                count=1, first_request_time=current_time
            )
            return True

        # Calculate window
        time_since_first = current_time - email_limit.first_request_time

        # Window expired, reset counter
        if time_since_first >= timedelta(minutes=10):
            _EMAIL_REQUESTS[email] = RateLimitEntry(
                count=1, first_request_time=current_time
            )
            return True

        # Within window, check count
        if email_limit.count >= _EMAIL_COUNT_MAX:
            return False
        else:
            email_limit.count += 1
            return True
