"""RED coverage for strict TTL-based response-cache freshness."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from async_model_gateway.response_cache.ttl_freshness_policy import TtlFreshnessPolicy


def test_ttl_freshness_policy_reports_a_hit_strictly_before_expiry() -> None:
    """A positive TTL must retain a response-cache hit before its boundary."""
    policy = TtlFreshnessPolicy(timedelta(seconds=30))
    written_at = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)

    assert policy.is_fresh(
        written_at=written_at,
        now=written_at + timedelta(seconds=29),
    ) is True


def test_ttl_freshness_policy_reports_a_miss_at_exact_expiry() -> None:
    """Equality at the TTL boundary must be expired rather than stale."""
    policy = TtlFreshnessPolicy(timedelta(seconds=30))
    written_at = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)

    assert policy.is_fresh(
        written_at=written_at,
        now=written_at + timedelta(seconds=30),
    ) is False


def test_ttl_freshness_policy_reports_a_miss_after_expiry() -> None:
    """A response must remain a miss after the strict TTL boundary."""
    policy = TtlFreshnessPolicy(timedelta(seconds=30))
    written_at = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)

    assert policy.is_fresh(
        written_at=written_at,
        now=written_at + timedelta(seconds=31),
    ) is False


@pytest.mark.parametrize("ttl", [timedelta(0), timedelta(microseconds=-1)])
def test_ttl_freshness_policy_rejects_non_positive_ttl(ttl: timedelta) -> None:
    """Zero and negative TTL values must fail before a policy is created."""
    with pytest.raises(ValueError):
        TtlFreshnessPolicy(ttl)
