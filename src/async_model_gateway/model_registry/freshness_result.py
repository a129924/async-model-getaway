"""Concrete registry-freshness result surface."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .entry import RegistryEntry

__all__ = ["RegistryFreshnessDecision", "RegistryFreshnessResult"]


class RegistryFreshnessDecision(str, Enum):
    """Allowed freshness decisions for a registry candidate."""

    FIRST_SEEN = "first-seen"
    UNCHANGED = "unchanged"
    CHANGED = "changed"


@dataclass(frozen=True, slots=True)
class RegistryFreshnessResult:
    """Decision material returned from registry freshness resolution."""

    decision: RegistryFreshnessDecision
    entry: RegistryEntry
    previous_payload_hash: str | None
