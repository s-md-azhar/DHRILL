import hashlib
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import diskcache as dc
except ImportError:
    dc = None

from app.config import settings

logger = logging.getLogger("dhrill.cache")


class InspectionCache:
    """
    Two-tier deterministic cache:
    Tier 1: Fast in-process LRU dict
    Tier 2: Persistent SQLite-backed diskcache
    """

    def __init__(self, cache_dir: Optional[str] = None, enabled: bool = True):
        self.enabled = enabled
        self._memory_cache: Dict[str, Any] = {}
        self._disk_cache = None
        self.hits = 0
        self.misses = 0

        if self.enabled:
            target_dir = Path(cache_dir or settings.cache.cache_dir)
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                if dc is not None:
                    self._disk_cache = dc.Cache(str(target_dir), size_limit=settings.cache.max_size_mb * 1024 * 1024)
                    logger.info(f"Initialized disk cache at {target_dir}")
            except Exception as e:
                logger.warning(f"Could not initialize disk cache at {target_dir}: {e}. Using memory-only cache.")

    @staticmethod
    def compute_hash(
        response_text: str,
        reference_context: Optional[str] = None,
        prompt: Optional[str] = None,
        pipeline_version: str = "v2.0"
    ) -> str:
        """
        Computes a deterministic SHA-256 digest over normalized inputs.
        """
        payload = {
            "version": pipeline_version,
            "response": (response_text or "").strip(),
            "context": (reference_context or "").strip(),
            "prompt": (prompt or "").strip(),
            "nli_model": settings.models_nli.name,
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None

        # Tier 1: In-memory
        if key in self._memory_cache:
            self.hits += 1
            return self._memory_cache[key]

        # Tier 2: Disk cache
        if self._disk_cache is not None:
            try:
                val = self._disk_cache.get(key)
                if val is not None:
                    self.hits += 1
                    self._memory_cache[key] = val  # Promote to memory
                    return val
            except Exception as e:
                logger.error(f"Error reading disk cache for key {key}: {e}")

        self.misses += 1
        return None

    def set(self, key: str, value: Dict[str, Any], expire: Optional[int] = None) -> None:
        if not self.enabled:
            return

        expire_time = expire if expire is not None else settings.cache.ttl_seconds

        # Store in memory
        self._memory_cache[key] = value
        if len(self._memory_cache) > 200:
            # Simple eviction: drop first key
            first_k = next(iter(self._memory_cache))
            del self._memory_cache[first_k]

        # Store in disk cache
        if self._disk_cache is not None:
            try:
                self._disk_cache.set(key, value, expire=expire_time)
            except Exception as e:
                logger.error(f"Error writing to disk cache for key {key}: {e}")

    def clear(self) -> None:
        self._memory_cache.clear()
        if self._disk_cache is not None:
            try:
                self._disk_cache.clear()
            except Exception as e:
                logger.error(f"Error clearing disk cache: {e}")


# Global cache instance
cache_instance = InspectionCache(
    cache_dir=settings.cache.cache_dir,
    enabled=settings.cache.enabled
)
