"""In-memory user-isolated capability context cache for Karmayogi AI Co-Pilot."""

import time
from typing import Any, Dict, Optional

# Key format: f"{user_id}:{active_competency_code}:{include_recommendations}" -> (timestamp, context_dict)
_COPILOT_CONTEXT_CACHE: Dict[str, tuple[float, Dict[str, Any]]] = {}
COPILOT_CACHE_TTL_SECONDS = 180.0  # 3-minute TTL safety boundary


def _make_key(
    user_id: str,
    active_competency_code: Optional[str] = None,
    include_recommendations: bool = True,
) -> str:
    return f"{user_id}:{active_competency_code or 'none'}:{int(include_recommendations)}"


def get_cached_copilot_context(
    user_id: str,
    active_competency_code: Optional[str] = None,
    include_recommendations: bool = True,
) -> Optional[Dict[str, Any]]:
    """Retrieve cached capability context if valid and unexpired."""
    key = _make_key(user_id, active_competency_code, include_recommendations)
    entry = _COPILOT_CONTEXT_CACHE.get(key)
    if not entry:
        return None
    timestamp, data = entry
    if time.time() - timestamp > COPILOT_CACHE_TTL_SECONDS:
        _COPILOT_CONTEXT_CACHE.pop(key, None)
        return None
    return data


def set_cached_copilot_context(
    user_id: str,
    data: Dict[str, Any],
    active_competency_code: Optional[str] = None,
    include_recommendations: bool = True,
) -> None:
    """Store capability context in cache."""
    key = _make_key(user_id, active_competency_code, include_recommendations)
    _COPILOT_CONTEXT_CACHE[key] = (time.time(), data)


def invalidate_copilot_cache(user_id: Optional[str] = None) -> None:
    """
    Invalidate copilot capability context cache.
    Must be called whenever competency state changes (assessments, role change, evidence).
    """
    if user_id is None:
        _COPILOT_CONTEXT_CACHE.clear()
        return

    uid_str = str(user_id)
    keys_to_del = [k for k in _COPILOT_CONTEXT_CACHE if k.startswith(f"{uid_str}:") or k == uid_str]
    for k in keys_to_del:
        _COPILOT_CONTEXT_CACHE.pop(k, None)
