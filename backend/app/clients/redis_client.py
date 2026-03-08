from contextlib import asynccontextmanager
from typing import Awaitable, cast

from redis.asyncio import Redis

from app.utils import get_or_throw

USAGE_KEY_PREFIX = "billing:user:"
REDIS_URL = get_or_throw("REDIS_URL")


def get_redis_client() -> Redis:
    """Create a short-lived Redis client from REDIS_URL."""
    return Redis.from_url(REDIS_URL, decode_responses=True)


def create_usage_key(user_id: int) -> str:
    """Create the Redis hash key for a user's runtime usage state."""
    return f"{USAGE_KEY_PREFIX}{user_id}"


def parse_usage_user_id(usage_key: str) -> int | None:
    """Extract user id from a usage key and ignore unrelated keys."""
    # This helper is reused in places that may pass arbitrary Redis keys,
    # so non-billing keys intentionally return None instead of crashing.
    if not usage_key.startswith(USAGE_KEY_PREFIX):
        return None
    user_id_str = usage_key.removeprefix(USAGE_KEY_PREFIX)
    try:
        return int(user_id_str)
    except ValueError as e:
        raise RuntimeError(f"Invalid usage key '{usage_key}': {e}") from e


async def validate_redis_connection() -> None:
    """Fail fast at startup when Redis is not reachable."""
    client = get_redis_client()
    try:
        ping_ok = await cast(Awaitable[bool], client.ping())
        if not ping_ok:
            raise RuntimeError("Redis ping returned false")
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
