"""Concrete registry-freshness policy."""

from __future__ import annotations

from .entry import RegistryEntry
from .freshness_result import RegistryFreshnessDecision, RegistryFreshnessResult

__all__ = ["RegistryFreshnessPolicy"]


class RegistryFreshnessPolicy:
    """Classify candidate entries against an already stored registry entry."""

    def evaluate(
        self,
        *,
        candidate_entry: RegistryEntry,
        stored_entry: RegistryEntry | None,
    ) -> RegistryFreshnessResult:
        """Return the freshness result for the candidate entry."""
        if stored_entry is None:
            return RegistryFreshnessResult(
                decision=RegistryFreshnessDecision.FIRST_SEEN,
                entry=candidate_entry,
                previous_payload_hash=None,
            )

        if stored_entry.payload_hash == candidate_entry.payload_hash:
            return RegistryFreshnessResult(
                decision=RegistryFreshnessDecision.UNCHANGED,
                entry=candidate_entry,
                previous_payload_hash=None,
            )

        return RegistryFreshnessResult(
            decision=RegistryFreshnessDecision.CHANGED,
            entry=candidate_entry,
            previous_payload_hash=stored_entry.payload_hash,
        )
