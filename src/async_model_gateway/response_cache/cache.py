"""Operational response-cache owner."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .entry import ResponseCacheEntry
from .key import ResponseCacheKey

if TYPE_CHECKING:
    from .ports.store import ResponseCacheStore

__all__ = ["ResponseCache"]


class ResponseCache:
    """Delegate response-cache reads and writes to the configured store port."""

    def __init__(self, store: ResponseCacheStore) -> None:
        """Bind the operational owner to the caller-provided store reference."""
        self._store = store

    async def get(self, *, key: ResponseCacheKey) -> ResponseCacheEntry | None:
        """Return the cached entry for the supplied key, if present."""
        return await self._store.get(key=key)

    async def set(self, *, key: ResponseCacheKey, entry: ResponseCacheEntry) -> None:
        """Persist the supplied entry for the provided key."""
        await self._store.set(key=key, entry=entry)
