"""Async in-memory registry-store implementation."""

from __future__ import annotations

import asyncio

from typing_extensions import override

from ..entry import ModelSourceKind, RegistryEntry
from ..ports.store import RegistryStore

__all__ = ["InMemoryRegistryStore"]


class InMemoryRegistryStore(RegistryStore):
    """Process-local registry store with same-instance serialized access."""

    def __init__(self) -> None:
        """Initialize an empty in-memory registry store."""
        self._entries: dict[tuple[str, ModelSourceKind], RegistryEntry] = {}
        self._lock = asyncio.Lock()

    @override
    async def get_entry(
        self,
        *,
        model_name: str,
        model_source_kind: ModelSourceKind,
    ) -> RegistryEntry | None:
        """Return the stored entry for the lookup identity, if present."""
        async with self._lock:
            return self._entries.get((model_name, model_source_kind))

    @override
    async def upsert_entry(self, entry: RegistryEntry) -> None:
        """Persist the candidate entry for the lookup identity."""
        async with self._lock:
            self._entries[(entry.model_name, entry.model_source_kind)] = entry
