"""Async whole-record storage port."""

from __future__ import annotations

from typing import Protocol

from ..key import CacheKey
from ..record import CacheVersionToken, StoredCacheRecord, UnsupportedSchemaRecord

__all__ = ["CacheStore"]


class CacheStore(Protocol):
    """Persist coherent records and support token-guarded deletion."""

    async def get(self, *, key: CacheKey) -> StoredCacheRecord | UnsupportedSchemaRecord | None:
        """Return the complete record for ``key``, if present."""
        ...

    async def set(self, *, key: CacheKey, record: StoredCacheRecord) -> None:
        """Replace the whole record associated with ``key``."""
        ...

    async def delete(self, *, key: CacheKey) -> bool:
        """Delete ``key`` and report whether it was present."""
        ...

    async def delete_if_version(self, *, key: CacheKey, version_token: CacheVersionToken) -> bool:
        """Delete ``key`` only when its currently stored token matches."""
        ...
