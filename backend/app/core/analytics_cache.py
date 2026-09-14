"""In-memory TTL cache for read-heavy dashboard and analytics endpoints.

Follows the existing ShikshaSetu in-memory caching pattern (see app.learning_resources.cache).
Provides user-isolated, role-isolated, and department-partitioned caching to eliminate
repeated synchronous database round-trips over WAN during concurrent access.
"""

import time
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Primary storage: key -> (timestamp, data)
_ANALYTICS_CACHE: Dict[str, tuple[float, Any]] = {}

DEFAULT_TTL_SECONDS = 60.0  # 60-second TTL safety boundary


def get_cached_item(key: str, ttl_seconds: float = DEFAULT_TTL_SECONDS) -> Optional[Any]:
    """Retrieve an item from the cache if present and not expired."""
    entry = _ANALYTICS_CACHE.get(key)
    if not entry:
        return None
    timestamp, data = entry
    if time.time() - timestamp > ttl_seconds:
        _ANALYTICS_CACHE.pop(key, None)
        return None
    return data


def set_cached_item(key: str, data: Any) -> None:
    """Store an item in the cache with current timestamp."""
    _ANALYTICS_CACHE[key] = (time.time(), data)


# =============================================================================
# Trainer Scoped Helpers
# =============================================================================

def get_trainer_dashboard_cache(trainer_id: str) -> Optional[dict]:
    return get_cached_item(f"trainer:dashboard:{trainer_id}")


def set_trainer_dashboard_cache(trainer_id: str, data: dict) -> None:
    set_cached_item(f"trainer:dashboard:{trainer_id}", data)


def get_trainer_materials_cache(trainer_id: str) -> Optional[list]:
    return get_cached_item(f"trainer:materials:{trainer_id}")


def set_trainer_materials_cache(trainer_id: str, data: list) -> None:
    set_cached_item(f"trainer:materials:{trainer_id}", data)


def get_trainer_learners_cache(trainer_id: str) -> Optional[list]:
    return get_cached_item(f"trainer:learners:{trainer_id}")


def set_trainer_learners_cache(trainer_id: str, data: list) -> None:
    set_cached_item(f"trainer:learners:{trainer_id}", data)


def invalidate_trainer_cache(trainer_id: Optional[str] = None) -> None:
    """Invalidate cache entries for a specific trainer or all trainers."""
    if trainer_id is None:
        keys_to_del = [k for k in _ANALYTICS_CACHE if k.startswith("trainer:")]
    else:
        prefix = f"trainer:"
        sub = f":{trainer_id}"
        keys_to_del = [k for k in _ANALYTICS_CACHE if k.startswith(prefix) and sub in k]
    for k in keys_to_del:
        _ANALYTICS_CACHE.pop(k, None)


# =============================================================================
# Admin Scoped Helpers
# =============================================================================

def get_admin_dashboard_cache(department: Optional[str] = None) -> Optional[Any]:
    dept_key = (department or "all").strip().lower()
    return get_cached_item(f"admin:dashboard:{dept_key}")


def set_admin_dashboard_cache(data: Any, department: Optional[str] = None) -> None:
    dept_key = (department or "all").strip().lower()
    set_cached_item(f"admin:dashboard:{dept_key}", data)


def get_admin_workforce_cache(department: Optional[str] = None) -> Optional[Any]:
    dept_key = (department or "all").strip().lower()
    return get_cached_item(f"admin:workforce:{dept_key}")


def set_admin_workforce_cache(data: Any, department: Optional[str] = None) -> None:
    dept_key = (department or "all").strip().lower()
    set_cached_item(f"admin:workforce:{dept_key}", data)


def get_admin_competencies_cache(department: Optional[str] = None) -> Optional[Any]:
    dept_key = (department or "all").strip().lower()
    return get_cached_item(f"admin:competencies:{dept_key}")


def set_admin_competencies_cache(data: Any, department: Optional[str] = None) -> None:
    dept_key = (department or "all").strip().lower()
    set_cached_item(f"admin:competencies:{dept_key}", data)


def get_admin_skill_gaps_cache(department: Optional[str] = None) -> Optional[Any]:
    dept_key = (department or "all").strip().lower()
    return get_cached_item(f"admin:skill_gaps:{dept_key}")


def set_admin_skill_gaps_cache(data: Any, department: Optional[str] = None) -> None:
    dept_key = (department or "all").strip().lower()
    set_cached_item(f"admin:skill_gaps:{dept_key}", data)


def invalidate_admin_cache() -> None:
    """Invalidate all admin organizational analytics cache entries."""
    keys_to_del = [k for k in _ANALYTICS_CACHE if k.startswith("admin:")]
    for k in keys_to_del:
        _ANALYTICS_CACHE.pop(k, None)


# =============================================================================
# Official User Scoped Helpers
# =============================================================================

def get_user_competencies_cache(user_id: str) -> Optional[list]:
    return get_cached_item(f"user:competencies:{user_id}")


def set_user_competencies_cache(user_id: str, data: list) -> None:
    set_cached_item(f"user:competencies:{user_id}", data)


def get_user_skill_gaps_cache(user_id: str) -> Optional[Any]:
    return get_cached_item(f"user:skill_gaps:{user_id}")


def set_user_skill_gaps_cache(user_id: str, data: Any) -> None:
    set_cached_item(f"user:skill_gaps:{user_id}", data)


def invalidate_user_cache(user_id: Optional[str] = None) -> None:
    """Invalidate cached personal data for a specific user or all users."""
    if user_id is None:
        keys_to_del = [k for k in _ANALYTICS_CACHE if k.startswith("user:")]
    else:
        uid_str = str(user_id)
        keys_to_del = [k for k in _ANALYTICS_CACHE if k.startswith(f"user:competencies:{uid_str}") or k.startswith(f"user:skill_gaps:{uid_str}")]
    for k in keys_to_del:
        _ANALYTICS_CACHE.pop(k, None)


def clear_all_analytics_cache() -> None:
    """Clear all analytics and dashboard cache entries."""
    _ANALYTICS_CACHE.clear()
