import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.limiter import limiter
from app.main import create_app
from tests.test_auth import FakeDatabase, FakeCollection


def test_rate_limiting_triggers_429_on_login_burst():
    """Verify that rapid requests beyond 10/min return HTTP 429 Too Many Requests."""
    database = FakeDatabase()
    application = create_app(Settings(
        mongodb_uri="mongodb://test",
        mongodb_database="test",
        jwt_secret="test-secret-with-at-least-32-bytes",
    ))
    application.state.database = database
    client = TestClient(application)

    limiter.enabled = True
    try:
        # Reset storage if supported
        if hasattr(limiter, "reset"):
            limiter.reset()

        responses = []
        for i in range(12):
            resp = client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "wrongpassword123",
            })
            responses.append(resp.status_code)

        # First 10 should hit the login endpoint (returning 401 for bad creds)
        # 11th and 12th should be rate-limited with 429
        assert 429 in responses, f"Expected 429 in responses, got: {responses}"
        status_429_idx = responses.index(429)
        assert status_429_idx <= 10, f"Rate limiting should engage by request 11, engaged at {status_429_idx + 1}"
    finally:
        limiter.enabled = False
