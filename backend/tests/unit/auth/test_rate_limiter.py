from app.auth.rate_limiter import check_email_rate_limit


async def test_rate_limiter_happy_path():
    """Test that rate limiter allows 2 requests then blocks the 3rd."""
    test_email = "test@example.com"

    # First two attempts succeed
    assert await check_email_rate_limit(test_email)
    assert await check_email_rate_limit(test_email)
    assert not await check_email_rate_limit(test_email)
