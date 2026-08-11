"""Internal freshness decision contract for response-cache records."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class FreshnessPolicy(Protocol):
    """Derive a stored record's write-time expiry."""

    def expires_at(self, *, written_at: datetime) -> datetime:
        """Return the expiry timestamp derived from ``written_at``."""
        ...
