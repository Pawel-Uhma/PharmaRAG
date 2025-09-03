"""
Cache module for PharmaRAG service.
Handles thread-safe caching with TTL and statistics.
"""

import time
import threading
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
import logging

try:
    from .config import CACHE_TTL_MINUTES, CACHE_MAX_SIZE, ENABLE_CACHE, CHROMA_PATH
except ImportError:
    from config import CACHE_TTL_MINUTES, CACHE_MAX_SIZE, ENABLE_CACHE, CHROMA_PATH

logger = logging.getLogger(__name__)


class ThreadSafeCache:
    """Thread-safe cache with TTL and size limits."""
    
    def __init__(self, ttl_minutes: int = 10, max_size: int = 1000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_minutes * 60
        self.max_size = max_size
        self.lock = threading.RLock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with TTL check"""
        with self.lock:
            self.stats["total_requests"] += 1
            
            if key not in self.cache:
                self.stats["misses"] += 1
                return None
            
            cache_entry = self.cache[key]
            if time.time() > cache_entry["expires_at"]:
                # Expired, remove it
                del self.cache[key]
                self.stats["misses"] += 1
                return None
            
            self.stats["hits"] += 1
            return cache_entry["value"]
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache with TTL"""
        with self.lock:
            # Check if we need to evict entries
            if len(self.cache) >= self.max_size:
                self._evict_expired_and_old()
            
            self.cache[key] = {
                "value": value,
                "expires_at": time.time() + self.ttl_seconds,
                "created_at": time.time()
            }
    
    def _evict_expired_and_old(self) -> None:
        """Evict expired entries and oldest entries if still over limit"""
        current_time = time.time()
        
        # Remove expired entries
        expired_keys = [k for k, v in self.cache.items() if current_time > v["expires_at"]]
        for key in expired_keys:
            del self.cache[key]
        
        # If still over limit, remove oldest entries
        if len(self.cache) >= self.max_size:
            sorted_entries = sorted(self.cache.items(), key=lambda x: x[1]["created_at"])
            entries_to_remove = len(sorted_entries) - self.max_size + 1
            for i in range(entries_to_remove):
                del self.cache[sorted_entries[i][0]]
                self.stats["evictions"] += 1
    
    def invalidate(self, key: str) -> None:
        """Invalidate a specific cache entry"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            hit_rate = (self.stats["hits"] / max(self.stats["total_requests"], 1)) * 100
            return {
                **self.stats,
                "hit_rate_percent": round(hit_rate, 2),
                "current_size": len(self.cache),
                "max_size": self.max_size,
                "ttl_minutes": self.ttl_seconds / 60
            }


def generate_cache_key(func_name: str, *args, **kwargs) -> str:
    """Generate a unique cache key for function calls"""
    # Create a hash of the function name and arguments
    key_data = {
        "func": func_name,
        "args": args,
        "kwargs": kwargs,
        "chroma_path": CHROMA_PATH  # Include database path in cache key
    }
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()


# Initialize global cache
medicine_names_cache = ThreadSafeCache(ttl_minutes=CACHE_TTL_MINUTES, max_size=CACHE_MAX_SIZE)


def get_cache_stats() -> Dict[str, Any]:
    """Get comprehensive cache statistics"""
    try:
        cache_stats = medicine_names_cache.get_stats()
        
        # Add additional performance metrics
        performance_metrics = {
            "cache_enabled": ENABLE_CACHE,
            "cache_ttl_minutes": CACHE_TTL_MINUTES,
            "cache_max_size": CACHE_MAX_SIZE,
            "chroma_path": CHROMA_PATH,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "cache_stats": cache_stats,
            "performance_metrics": performance_metrics
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}", exc_info=True)
        return {"error": f"Failed to get cache stats: {str(e)}"}


def invalidate_medicine_names_cache() -> Dict[str, str]:
    """Invalidate the medicine names cache"""
    try:
        cache_key = generate_cache_key("get_medicine_names_from_chroma")
        medicine_names_cache.invalidate(cache_key)
        logger.info("Medicine names cache invalidated successfully")
        return {"status": "success", "message": "Cache invalidated successfully"}
    except Exception as e:
        logger.error(f"Error invalidating cache: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Failed to invalidate cache: {str(e)}"}


def refresh_medicine_names_cache() -> Dict[str, Any]:
    """Force refresh the medicine names cache"""
    start_time = time.time()
    try:
        # Force refresh by calling with force_refresh=True
        try:
            from .database import get_medicine_names_from_chroma
        except ImportError:
            from database import get_medicine_names_from_chroma
        names = get_medicine_names_from_chroma(force_refresh=True)
        elapsed_time = (time.time() - start_time) * 1000
        
        logger.info(f"Cache refreshed successfully. Found {len(names)} names. Refresh time: {elapsed_time:.2f}ms")
        
        return {
            "status": "success",
            "message": "Cache refreshed successfully",
            "names_count": len(names),
            "refresh_time_ms": round(elapsed_time, 2)
        }
    except Exception as e:
        elapsed_time = (time.time() - start_time) * 1000
        logger.error(f"Error refreshing cache after {elapsed_time:.2f}ms: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to refresh cache: {str(e)}",
            "refresh_time_ms": round(elapsed_time, 2)
        }
