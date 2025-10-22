"""
Caching utilities for API responses.
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Any, Callable
import functools


class APICache:
    """Simple file-based cache for API responses."""

    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        """
        Initialize cache.

        Args:
            cache_dir: Directory for cache files
            ttl_hours: Time-to-live in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)

    def _get_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = f"{args}_{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get path to cache file."""
        return self.cache_dir / f"{cache_key}.json"

    def get(self, cache_key: str) -> Optional[Any]:
        """Get cached value if valid."""
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        # Check if expired
        mod_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        if datetime.now() - mod_time > self.ttl:
            cache_path.unlink()  # Delete expired cache
            return None

        # Load cached data
        with open(cache_path, 'r') as f:
            return json.load(f)

    def set(self, cache_key: str, value: Any) -> None:
        """Set cache value."""
        cache_path = self._get_cache_path(cache_key)

        with open(cache_path, 'w') as f:
            json.dump(value, f, indent=2)

    def clear(self) -> int:
        """Clear all cache files. Returns number of files deleted."""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        return count

    def cached_call(self, func: Callable) -> Callable:
        """Decorator for caching function calls."""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = self._get_cache_key(func.__name__, *args, **kwargs)

            # Try to get from cache
            cached = self.get(cache_key)
            if cached is not None:
                return cached

            # Call function and cache result
            result = func(*args, **kwargs)
            self.set(cache_key, result)
            return result

        return wrapper
