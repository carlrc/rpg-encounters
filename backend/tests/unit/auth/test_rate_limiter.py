from app.auth.rate_limiter import check_rate_limit


async def test_rate_limiter_happy_path(monkeypatch):
    """Test that rate limiter allows 2 requests then blocks the 3rd."""
    test_email = "test@example.com"
    monkeypatch.setattr("app.auth.rate_limiter.DISABLE_RATE_LIMITING", False)

    # First two attempts succeed
    assert await check_rate_limit(key=test_email, max_count=2, window_minutes=10)
    assert await check_rate_limit(key=test_email, max_count=2, window_minutes=10)
    assert not await check_rate_limit(key=test_email, max_count=2, window_minutes=10)
