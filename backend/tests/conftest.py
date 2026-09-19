import pytest
from app.core.limiter import limiter
from app.core import analytics_cache


@pytest.fixture(autouse=True)
def disable_limiter_and_reset_cache_in_unit_tests():
    """
    Disable slowapi limiter and in-memory analytics cache by default for test suite
    runs to guarantee strict isolation on rapid in-memory test clients.
    """
    prev_limiter = getattr(limiter, "enabled", True)
    prev_cache = analytics_cache.CACHE_ENABLED
    limiter.enabled = False
    analytics_cache.CACHE_ENABLED = False
    analytics_cache.clear_all_analytics_cache()
    yield
    limiter.enabled = prev_limiter
    analytics_cache.CACHE_ENABLED = prev_cache
    analytics_cache.clear_all_analytics_cache()

