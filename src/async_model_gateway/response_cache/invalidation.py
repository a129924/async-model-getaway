"""Separate store-backed key-local invalidation implementation."""

from __future__ import annotations

from .key import CacheKey
from .outcomes import Invalidated, NotFound
from .ports.store import CacheStore

__all__ = ["StoreCacheInvalidator"]


class StoreCacheInvalidator:
    """Map a store's key-local delete result to invalidation outcomes."""

    def __init__(self, *, store: CacheStore) -> None:
        """Bind the separate invalidation owner to its store."""
        self._store = store

    async def invalidate(self, *, key: CacheKey) -> Invalidated | NotFound:
        """Invalidate the supplied key without outcome translation of failures."""
        if await self._store.delete(key=key):
            return Invalidated()
        return NotFound()
