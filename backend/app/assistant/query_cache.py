"""
In-memory query result caching for ShikshaSetu AI Assistant.
Caches deterministic responses and frequent RAG queries to reduce latency.
"""

import hashlib
import time
from typing import Any, Dict, Optional, Tuple
from functools import lru_cache


class QueryResultCache:
    """
    Simple in-memory cache for assistant query results.
    Uses LRU eviction and TTL expiration.
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        """
        Initialize query cache.
        
        Args:
            max_size: Maximum number of cached entries
            ttl_seconds: Time-to-live for cache entries (default 5 minutes)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._access_order: list[str] = []
    
    def _make_key(self, user_id: str, message: str, competency_code: Optional[str] = None) -> str:
        """Generate cache key from query parameters."""
        key_parts = [user_id, message.lower().strip()]
        if competency_code:
            key_parts.append(competency_code)
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(
        self, 
        user_id: str, 
        message: str, 
        competency_code: Optional[str] = None
    ) -> Optional[Any]:
        """
        Get cached result if available and not expired.
        
        Returns:
            Cached result or None if not found/expired
        """
        key = self._make_key(user_id, message, competency_code)
        
        if key not in self._cache:
            return None
        
        result, timestamp = self._cache[key]
        
        # Check if expired
        if time.time() - timestamp > self.ttl_seconds:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
            return None
        
        # Update access order (move to end = most recent)
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
        
        return result
    
    def set(
        self,
        user_id: str,
        message: str,
        result: Any,
        competency_code: Optional[str] = None
    ) -> None:
        """
        Cache a query result.
        
        Args:
            user_id: User ID
            message: Query message
            result: Result to cache
            competency_code: Optional competency context
        """
        key = self._make_key(user_id, message, competency_code)
        
        # Evict oldest if at capacity
        if len(self._cache) >= self.max_size and key not in self._cache:
            if self._access_order:
                oldest_key = self._access_order.pop(0)
                if oldest_key in self._cache:
                    del self._cache[oldest_key]
        
        self._cache[key] = (result, time.time())
        
        # Update access order
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    def invalidate_user(self, user_id: str) -> None:
        """Invalidate all cache entries for a specific user."""
        keys_to_remove = []
        for key in list(self._cache.keys()):
            # Check if key belongs to this user (first part of key_string)
            if key in self._cache:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
            "utilization": len(self._cache) / self.max_size if self.max_size > 0 else 0,
        }


# Global cache instance
_query_cache: Optional[QueryResultCache] = None


def get_query_cache() -> QueryResultCache:
    """Get or create the global query cache instance."""
    global _query_cache
    if _query_cache is None:
        _query_cache = QueryResultCache(max_size=1000, ttl_seconds=300)
    return _query_cache


@lru_cache(maxsize=256)
def is_cacheable_query(message: str) -> bool:
    """
    Determine if a query is cacheable.
    Deterministic queries (skill gaps, recommendations) are highly cacheable.
    """
    message_lower = message.lower()
    
    # Highly cacheable patterns
    cacheable_patterns = [
        "my gap", "my skill", "my score", "priority gap",
        "recommend", "courses for me", "suggest courses",
        "what is", "define", "explain", "how to",
        "difference between", "compare",
    ]
    
    return any(pattern in message_lower for pattern in cacheable_patterns)
