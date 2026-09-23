"""
In-memory embedding cache to avoid redundant API calls.
Significantly reduces latency for repeated queries.
"""

import hashlib
from functools import lru_cache
from typing import Dict, List, Optional, Tuple
import time


class EmbeddingCache:
    """
    Cache for text embeddings to avoid redundant API calls.
    Uses content-based hashing for deduplication.
    """
    
    def __init__(self, max_size: int = 10000, ttl_seconds: int = 3600):
        """
        Initialize embedding cache.
        
        Args:
            max_size: Maximum number of cached embeddings
            ttl_seconds: Time-to-live in seconds (default 1 hour)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Tuple[List[float], float]] = {}
        self._access_order: list[str] = []
        self._hits = 0
        self._misses = 0
    
    def _make_key(self, text: str) -> str:
        """Generate cache key from text content."""
        # Normalize text: lowercase, strip whitespace
        normalized = text.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def get(self, text: str) -> Optional[List[float]]:
        """
        Get cached embedding if available and not expired.
        
        Args:
            text: Input text
            
        Returns:
            Cached embedding vector or None
        """
        key = self._make_key(text)
        
        if key not in self._cache:
            self._misses += 1
            return None
        
        embedding, timestamp = self._cache[key]
        
        # Check expiration
        if time.time() - timestamp > self.ttl_seconds:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
            self._misses += 1
            return None
        
        # Update access order
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
        
        self._hits += 1
        return embedding
    
    def set(self, text: str, embedding: List[float]) -> None:
        """
        Cache an embedding.
        
        Args:
            text: Input text
            embedding: Embedding vector
        """
        key = self._make_key(text)
        
        # Evict oldest if at capacity
        if len(self._cache) >= self.max_size and key not in self._cache:
            if self._access_order:
                oldest_key = self._access_order.pop(0)
                if oldest_key in self._cache:
                    del self._cache[oldest_key]
        
        self._cache[key] = (embedding, time.time())
        
        # Update access order
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    def get_many(self, texts: List[str]) -> Tuple[List[Optional[List[float]]], List[str]]:
        """
        Get multiple embeddings, returning cached results and texts needing embedding.
        
        Args:
            texts: List of input texts
            
        Returns:
            Tuple of (cached embeddings with None for misses, texts that need embedding)
        """
        results: List[Optional[List[float]]] = []
        texts_to_embed: List[str] = []
        
        for text in texts:
            cached = self.get(text)
            results.append(cached)
            if cached is None:
                texts_to_embed.append(text)
        
        return results, texts_to_embed
    
    def set_many(self, texts: List[str], embeddings: List[List[float]]) -> None:
        """
        Cache multiple embeddings.
        
        Args:
            texts: List of input texts
            embeddings: List of embedding vectors
        """
        for text, embedding in zip(texts, embeddings):
            self.set(text, embedding)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._access_order.clear()
        self._hits = 0
        self._misses = 0
    
    def get_stats(self) -> Dict[str, any]:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate * 100, 2),
            "utilization": len(self._cache) / self.max_size if self.max_size > 0 else 0,
        }


# Global cache instance
_embedding_cache: Optional[EmbeddingCache] = None


def get_embedding_cache() -> EmbeddingCache:
    """Get or create the global embedding cache instance."""
    global _embedding_cache
    if _embedding_cache is None:
        _embedding_cache = EmbeddingCache(max_size=10000, ttl_seconds=3600)
    return _embedding_cache


@lru_cache(maxsize=128)
def normalize_text_for_cache(text: str) -> str:
    """Normalize text for consistent caching."""
    return text.lower().strip()
