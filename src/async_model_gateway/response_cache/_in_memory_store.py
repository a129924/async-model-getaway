"""Internal process-local response-cache store implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from typing_extensions import override

from .entry import ResponseCacheEntry
from .freshness_policy import FreshnessPolicy
from .key import ResponseCacheKey
from .ports.store import ResponseCacheStore


def _utc_now() -> datetime:
    """Return the current aware UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class _StoredResponseCacheEntry:
    """Pair a cached response entry with its original successful-write time."""

    entry: ResponseCacheEntry
    written_at: datetime


class InMemoryResponseCacheStore(ResponseCacheStore):
    """Keep response-cache records in process memory with injected freshness."""

    def __init__(self, *, freshness_policy: FreshnessPolicy) -> None:
        """Bind the store to its caller-provided freshness decision."""
        self._freshness_policy = freshness_policy
        self._entries: dict[ResponseCacheKey, _StoredResponseCacheEntry] = {}

    @override
    async def get(self, *, key: ResponseCacheKey) -> ResponseCacheEntry | None:
        """Return a fresh entry, or a normal miss when none is fresh."""
        stored_entry = self._entries.get(key)
        if stored_entry is None:
            return None
        if not self._freshness_policy.is_fresh(
            written_at=stored_entry.written_at,
            now=_utc_now(),
        ):
            return None
        return stored_entry.entry

    @override
    async def set(self, *, key: ResponseCacheKey, entry: ResponseCacheEntry) -> None:
        """Persist an entry with the timestamp of this successful write."""
        self._entries[key] = _StoredResponseCacheEntry(
            entry=entry,
            written_at=_utc_now(),
        )
