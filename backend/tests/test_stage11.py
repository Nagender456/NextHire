import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import Settings
from app.rate_limit import RateLimiter
from app.main import app


def test_api_responses_include_security_headers() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert response.headers["permissions-policy"] == (
        "camera=(), microphone=(), geolocation=()"
    )
    assert response.cookies.get("nexthire_csrf")


def test_production_settings_reject_insecure_defaults() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="production")


def test_production_settings_reject_wildcard_origins() -> None:
    with pytest.raises(ValidationError):
        Settings(
            app_env="production",
            session_secret="a-production-only-secret",
            session_cookie_secure=True,
            cors_allowed_origins="*",
        )


def test_production_settings_parse_explicit_origins() -> None:
    settings = Settings(
        app_env="production",
        session_secret="a-production-only-secret",
        session_cookie_secure=True,
        cors_allowed_origins="https://app.example.com, https://admin.example.com",
    )

    assert settings.allowed_origins == [
        "https://app.example.com",
        "https://admin.example.com",
    ]


def test_rate_limiter_rejects_only_after_the_configured_limit() -> None:
    limiter = RateLimiter()

    assert limiter.allow("client", "login", 2, 60)
    assert limiter.allow("client", "login", 2, 60)
    assert not limiter.allow("client", "login", 2, 60)
    assert limiter.allow("other-client", "login", 2, 60)


def test_response_has_request_id_and_metrics_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health", headers={"X-Request-ID": "test-request"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "test-request"
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "nexthire_requests_total" in metrics.text


def test_settings_validate_distributed_rate_limit_backend() -> None:
    settings = Settings(rate_limit_backend="redis")

    assert settings.rate_limit_backend == "redis"
