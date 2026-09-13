import pytest
from app.core.limiter import limiter


@pytest.fixture(autouse=True)
def disable_limiter_by_default_in_unit_tests():
    """
    Disable slowapi limiter by default for general test suite runs to avoid
    hitting burst limits on rapid in-memory test clients.
    Tests specifically asserting rate limiting behavior can set limiter.enabled = True.
    """
    prev_state = getattr(limiter, "enabled", True)
    limiter.enabled = False
    yield
    limiter.enabled = prev_state
