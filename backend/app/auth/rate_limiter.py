import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class RateLimitEntry(BaseModel):
    count: int
    first_request_time: datetime


_RATE_LIMIT_REQUESTS: Dict[str, RateLimitEntry] = {}
_LOCK = asyncio.Lock()
_CLEANUP_COUNTER = 0
_CLEANUP_INTERVAL = 100


def _cleanup_expired_entries(window_minutes: int) -> None:
    """Remove expired entries from the rate limit dictionary."""
    current_time = datetime.now()
    expired_keys = []

    for key, entry in _RATE_LIMIT_REQUESTS.items():
        time_since_first = current_time - entry.first_request_time
        if time_since_first >= timedelta(minutes=window_minutes):
            expired_keys.append(key)

    for key in expired_keys:
        del _RATE_LIMIT_REQUESTS[key]


async def check_rate_limit(key: str, max_count: int, window_minutes: int) -> bool:
    """Check if key is rate limited. Returns False if rate limit exceeded."""

    async with _LOCK:
        global _CLEANUP_COUNTER
        current_time = datetime.now()

        # Periodic cleanup to prevent unbounded memory growth
        _CLEANUP_COUNTER += 1
        if _CLEANUP_COUNTER % _CLEANUP_INTERVAL == 0:
            logger.info("Cleaning up rate limit cache...")
            _cleanup_expired_entries(window_minutes)

        key_limit = _RATE_LIMIT_REQUESTS.get(key)

        # Doesn't exist - create entry
        if not key_limit:
            _RATE_LIMIT_REQUESTS[key] = RateLimitEntry(
                count=1, first_request_time=current_time
            )
            return True

        # Calculate window
        time_since_first = current_time - key_limit.first_request_time

        # Window expired, reset counter
        if time_since_first >= timedelta(minutes=window_minutes):
            _RATE_LIMIT_REQUESTS[key] = RateLimitEntry(
                count=1, first_request_time=current_time
            )
            return True

        # Within window, check count
        if key_limit.count >= max_count:
            return False
        else:
            key_limit.count += 1
            return True
