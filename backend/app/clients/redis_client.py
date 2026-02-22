from contextlib import asynccontextmanager
from urllib.parse import urlparse

from redis.asyncio import Redis

from app.utils import get_or_throw

USAGE_KEY_PREFIX = "billing:user:"
USAGE_FLUSH_KEY_PREFIX = "usage:flush:"
REDIS_URL = get_or_throw("REDIS_URL")


def get_redis_client() -> Redis:
    """Create a short-lived Redis client from REDIS_URL."""
    return Redis.from_url(REDIS_URL, decode_responses=True)


def create_usage_key(user_id: int) -> str:
    """Create the Redis hash key for a user's runtime usage state."""
    return f"{USAGE_KEY_PREFIX}{user_id}"


def create_usage_flush_key(user_id: int) -> str:
    """Create the Redis expiry-trigger key that schedules a usage flush."""
    return f"{USAGE_FLUSH_KEY_PREFIX}{user_id}"


def get_redis_db_index() -> int:
    """Parse Redis DB index from REDIS_URL."""
    parsed = urlparse(REDIS_URL)
    try:
        return int(parsed.path.lstrip("/").split("/")[0])
    except ValueError:
        raise RuntimeError(f"Invalid Redis DB index in REDIS_URL path: {parsed.path}")


def create_expired_events_channel() -> str:
    """Build keyevent channel name for expired keys in the configured Redis DB."""
    return f"__keyevent@{get_redis_db_index()}__:expired"


def parse_usage_flush_user_id(expired_key: str) -> int | None:
    """Extract user id from a flush key and ignore unrelated expirations."""
    if not expired_key.startswith(USAGE_FLUSH_KEY_PREFIX):
        return None
    user_id_str = expired_key.removeprefix(USAGE_FLUSH_KEY_PREFIX)
    try:
        return int(user_id_str)
    except ValueError as e:
        raise RuntimeError(f"Invalid usage flush key '{expired_key}': {e}") from e


async def validate_redis_connection() -> None:
    """Fail fast by pinging Redis during startup and letting connection errors bubble up."""
    client = get_redis_client()
    try:
        await client.ping()
    finally:
        await client.aclose()


@asynccontextmanager
async def get_redis_session():
    """Provide an async Redis client context and always close it after use."""
    client = get_redis_client()
    try:
        yield client
    finally:
        await client.aclose()
