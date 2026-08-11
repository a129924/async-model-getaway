"""Synchronous opaque-version-token creation port."""

from __future__ import annotations

from typing import Protocol

from ..record import CacheVersionToken

__all__ = ["VersionTokenFactory"]


class VersionTokenFactory(Protocol):
    """Create one opaque token for each stored record replacement."""

    def new(self) -> CacheVersionToken:
        """Return a new opaque record version token."""
        ...
