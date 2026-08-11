"""Internal TTL-based freshness decision for response-cache records."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from typing_extensions import override

from .freshness_policy import FreshnessPolicy


class TtlFreshnessPolicy(FreshnessPolicy):
    """Derive strict positive-TTL expiry timestamps."""

    def __init__(self, *, ttl: timedelta) -> None:
        """Create a policy with one strictly positive time-to-live duration."""
        if ttl <= timedelta(0):
            msg = "ttl must be strictly positive"
            raise ValueError(msg)
        self._ttl = ttl

    @override
    def expires_at(self, *, written_at: datetime) -> datetime:
        """Return the strictly later UTC expiry for ``written_at``."""
        if written_at.tzinfo is None or written_at.utcoffset() != timedelta(0):
            msg = "written_at must be an aware UTC timestamp"
            raise ValueError(msg)
        if written_at.tzinfo is not timezone.utc:
            written_at = written_at.astimezone(timezone.utc)
        return written_at + self._ttl
