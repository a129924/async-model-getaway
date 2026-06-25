"""Async registry-store port."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..entry import ModelSourceKind, RegistryEntry

__all__ = ["RegistryStore"]


class RegistryStore(ABC):
    """Abstract store collaborator for registry lookup and persistence."""

    @abstractmethod
    async def get_entry(
        self,
        *,
        model_name: str,
        model_source_kind: ModelSourceKind,
    ) -> RegistryEntry | None:
        """Return the stored entry for the lookup identity, if present."""

    @abstractmethod
    async def upsert_entry(self, entry: RegistryEntry) -> None:
        """Persist the candidate entry for the lookup identity."""
