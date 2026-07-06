"""Value surface for cached response material."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["ResponseCacheEntry"]


@dataclass(frozen=True, slots=True)
class ResponseCacheEntry:
    """Immutable cached-response value object."""

    response: str
