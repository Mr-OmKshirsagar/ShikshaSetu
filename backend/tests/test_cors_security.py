import pytest
from app.core.config import Settings
from app.main import create_app


def test_cors_production_disallows_wildcard_regex():
    # Production settings
    prod_settings = Settings(
        app_env="production",
        jwt_secret="a-very-long-secure-production-secret-key",
        cors_allowed_origins=["https://shikshasetu.gov.in"],
    )
    prod_app = create_app(prod_settings)

    # Find CORSMiddleware
    cors_middlewares = [m for m in prod_app.user_middleware if "CORSMiddleware" in str(m)]
    assert cors_middlewares, "CORSMiddleware should be installed"
    kwargs = cors_middlewares[0].kwargs

    # In production, allow_origins should be explicit and allow_origin_regex must NOT be set
    assert kwargs.get("allow_origins") == ["https://shikshasetu.gov.in"]
    assert "allow_origin_regex" not in kwargs or kwargs.get("allow_origin_regex") is None


def test_cors_development_allows_local_origins():
    dev_settings = Settings(
        app_env="development",
        jwt_secret="test-secret-with-at-least-32-bytes",
    )
    dev_app = create_app(dev_settings)
    cors_middlewares = [m for m in dev_app.user_middleware if "CORSMiddleware" in str(m)]
    assert cors_middlewares
    kwargs = cors_middlewares[0].kwargs

    assert "http://localhost:3000" in kwargs.get("allow_origins", [])
