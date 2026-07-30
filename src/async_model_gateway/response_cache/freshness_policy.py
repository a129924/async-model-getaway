"""Internal freshness decision contract for response-cache records."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class FreshnessPolicy(Protocol):
    """Decide whether a stored response-cache record remains fresh."""

    def is_fresh(self, *, written_at: datetime, now: datetime) -> bool:
        """Return whether the record written at ``written_at`` is still fresh."""
        ...
