from httpx import AsyncClient, HTTPStatusError
from pydantic_ai import UnexpectedModelBehavior
from pydantic_ai.retries import AsyncTenacityTransport, wait_retry_after
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# HTTP Error Messages
ENTITY_NOT_FOUND = "Entity not found"
INTERNAL_SERVER_ERROR = "Internal Server Error"


# https://ai.pydantic.dev/retries/#usage-example
def create_retrying_client() -> AsyncClient:
    """Create a client with smart retry handling for multiple error types."""

    def should_retry_status(response):
        """Raise exceptions for retryable HTTP status codes."""
        if response.status_code in (429, 502, 503, 504):
            response.raise_for_status()  # This will raise HTTPStatusError

    # TODO: Logging on retries should be added here
    transport = AsyncTenacityTransport(
        controller=AsyncRetrying(
            # Retry on HTTP errors and connection issues
            retry=retry_if_exception_type(
                (HTTPStatusError, ConnectionError, UnexpectedModelBehavior)
            ),
            # Smart waiting: respects Retry-After headers, falls back to exponential backoff
            wait=wait_retry_after(
                fallback_strategy=wait_exponential(multiplier=1, max=60), max_wait=300
            ),
            stop=stop_after_attempt(2),
            # Re-raise the last exception if all retries fail
            reraise=True,
        ),
        validate_response=should_retry_status,
    )
    return AsyncClient(transport=transport)
