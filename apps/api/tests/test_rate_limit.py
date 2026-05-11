from unittest.mock import MagicMock


def test_redis_rate_limiter_allows_within_limit():
    """Test that requests within limit are allowed."""
    mock_redis = MagicMock()
    mock_pipeline = MagicMock()
    mock_pipeline.execute.return_value = [0, 0]  # zrem, zcard
    mock_redis.pipeline.return_value = mock_pipeline

    from src.middleware.rate_limit import RedisRateLimiter

    limiter = RedisRateLimiter(redis_client=mock_redis)
    allowed, remaining, _ = limiter.allow("team:test", max_requests=10)

    assert allowed is True
    assert remaining == 9


def test_redis_rate_limiter_blocks_after_limit():
    """Test that requests exceeding limit are blocked."""
    mock_redis = MagicMock()
    mock_pipeline = MagicMock()
    # Simulate being at the limit
    mock_pipeline.execute.return_value = [0, 10]  # zrem, zcard at limit
    mock_redis.pipeline.return_value = mock_pipeline

    from src.middleware.rate_limit import RedisRateLimiter

    limiter = RedisRateLimiter(redis_client=mock_redis)
    allowed, remaining, _ = limiter.allow("team:test", max_requests=10)

    assert allowed is False
    assert remaining == 0


def test_plan_rate_limits_config():
    """Test that plan rate limits are configured correctly."""
    from src.middleware.rate_limit import PLAN_RATE_LIMITS

    assert PLAN_RATE_LIMITS["FREE"] == 30
    assert PLAN_RATE_LIMITS["STANDARD"] == 60
    assert PLAN_RATE_LIMITS["PRO"] == 120


def test_rate_limit_headers_added_to_response():
    """Test that rate limit headers are added to successful responses."""
    from starlette.applications import Starlette
    from starlette.responses import PlainTextResponse
    from starlette.testclient import TestClient

    from src.middleware.rate_limit import RateLimitMiddleware, RedisRateLimiter

    mock_redis = MagicMock()
    mock_pipeline = MagicMock()
    mock_pipeline.execute.return_value = [0, 0]
    mock_redis.pipeline.return_value = mock_pipeline

    limiter = RedisRateLimiter(redis_client=mock_redis)

    app = Starlette()
    app.add_middleware(RateLimitMiddleware, limiter=limiter)

    @app.route("/v1/test")
    async def test_endpoint(request):
        return PlainTextResponse("OK")

    client = TestClient(app)
    response = client.get("/v1/test", headers={"X-Team-Id": "test-team"})

    assert response.status_code == 200
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers


def test_rate_limit_429_response():
    """Test that 429 response includes proper headers and Retry-After."""
    from starlette.applications import Starlette
    from starlette.responses import PlainTextResponse
    from starlette.testclient import TestClient

    from src.middleware.rate_limit import RateLimitMiddleware, RedisRateLimiter

    mock_redis = MagicMock()
    mock_pipeline = MagicMock()
    # Simulate exceeding the limit
    mock_pipeline.execute.return_value = [0, 10]  # zcard at limit
    mock_redis.pipeline.return_value = mock_pipeline

    # Mock zrange to return a timestamp for reset calculation
    mock_redis.zrange.return_value = [("1234567890.0", 1234567890.0)]
    mock_redis.zrem.return_value = 1

    limiter = RedisRateLimiter(redis_client=mock_redis)

    app = Starlette()
    app.add_middleware(RateLimitMiddleware, limiter=limiter)

    @app.route("/v1/test")
    async def test_endpoint(request):
        return PlainTextResponse("OK")

    client = TestClient(app)
    response = client.get("/v1/test", headers={"X-Team-Id": "test-team"})

    assert response.status_code == 429
    assert "X-RateLimit-Limit" in response.headers
    assert response.headers["X-RateLimit-Remaining"] == "0"
    assert "Retry-After" in response.headers
    assert "rate_limited" in response.json()["error"]["code"]
