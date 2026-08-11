"""RED coverage for the retained strict positive-TTL expiry policy."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest


def test_ttl_policy_derives_a_strictly_later_aware_utc_expiry() -> None:
    """Expiry is calculated once at write time and never needs a read-time clock."""
    from async_model_gateway.response_cache.ttl_freshness_policy import TtlFreshnessPolicy

    written_at = datetime(2026, 8, 6, 12, 0, tzinfo=timezone.utc)
    policy = TtlFreshnessPolicy(ttl=timedelta(seconds=30))

    assert policy.expires_at(written_at=written_at) == written_at + timedelta(seconds=30)
    assert policy.expires_at(written_at=written_at) > written_at
    assert policy.expires_at(written_at=written_at).utcoffset() == timedelta(0)
    assert not hasattr(policy, "is_fresh")


@pytest.mark.parametrize("ttl", [timedelta(0), timedelta(seconds=-1)])
def test_ttl_policy_rejects_non_positive_ttl(ttl: timedelta) -> None:
    """The strict positive TTL boundary remains a configuration defect."""
    from async_model_gateway.response_cache.ttl_freshness_policy import TtlFreshnessPolicy

    with pytest.raises(ValueError):
        TtlFreshnessPolicy(ttl=ttl)
    assert not hasattr(TtlFreshnessPolicy, "is_fresh")


def test_ttl_policy_rejects_naive_or_non_utc_write_timestamps_and_overflow() -> None:
    """Only aware UTC values can enter the record expiry contract."""
    from async_model_gateway.response_cache.ttl_freshness_policy import TtlFreshnessPolicy

    policy = TtlFreshnessPolicy(ttl=timedelta(seconds=1))

    with pytest.raises(ValueError):
        policy.expires_at(written_at=datetime(2026, 8, 6, 12, 0))
    with pytest.raises(ValueError):
        policy.expires_at(
            written_at=datetime(2026, 8, 6, 20, 0, tzinfo=timezone(timedelta(hours=8)))
        )
    with pytest.raises(OverflowError):
        TtlFreshnessPolicy(ttl=timedelta(days=1)).expires_at(
            written_at=datetime.max.replace(tzinfo=timezone.utc)
        )
