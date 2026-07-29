"""Internal TTL-based freshness decision for response-cache records."""

from __future__ import annotations
from datetime import datetime, timedelta
from typing_extensions import override

from .freshness_policy import FreshnessPolicy

class TtlFreshnessPolicy(FreshnessPolicy):
    """Treat records as fresh strictly before an injected TTL boundary."""

    def __init__(self, ttl: timedelta) -> None:
        """Create a policy with one strictly positive time-to-live duration."""
        if ttl <= timedelta(0):
            msg = "ttl must be strictly positive"
            raise ValueError(msg)
        self._ttl = ttl

    @override
    def is_fresh(self, *, written_at: datetime, now: datetime) -> bool:
        """Return whether ``now`` remains strictly before the expiry boundary."""
        return now < written_at + self._ttl
