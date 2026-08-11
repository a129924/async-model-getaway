"""Internal coherent process-local response-cache store."""

from __future__ import annotations

from .key import CacheKey
from .record import CacheVersionToken, StoredCacheRecord, UnsupportedSchemaRecord


class InMemoryCacheStore:
    """Keep whole records in process memory without freshness ownership."""

    def __init__(self) -> None:
        """Create an empty per-key record map."""
        self._records: dict[CacheKey, StoredCacheRecord] = {}

    async def get(self, *, key: CacheKey) -> StoredCacheRecord | UnsupportedSchemaRecord | None:
        """Return the current complete record for ``key``."""
        return self._records.get(key)

    async def set(self, *, key: CacheKey, record: StoredCacheRecord) -> None:
        """Atomically replace the complete record for ``key``."""
        self._records[key] = record

    async def delete(self, *, key: CacheKey) -> bool:
        """Remove ``key`` for explicit invalidation only."""
        if key not in self._records:
            return False
        del self._records[key]
        return True

    async def delete_if_version(self, *, key: CacheKey, version_token: CacheVersionToken) -> bool:
        """Remove only a record that still has the observed version token."""
        record = self._records.get(key)
        if record is None or record.version_token != version_token:
            return False
        del self._records[key]
        return True
