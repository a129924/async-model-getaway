"""RED coverage for the internal in-memory response-cache store."""

from __future__ import annotations

import inspect
from datetime import datetime, timedelta, timezone

import pytest

from async_model_gateway.response_cache import ResponseCacheEntry, ResponseCacheKey
from async_model_gateway.response_cache import _in_memory_store as in_memory_store_module
from async_model_gateway.response_cache._in_memory_store import InMemoryResponseCacheStore
from async_model_gateway.response_cache.freshness_policy import FreshnessPolicy
from async_model_gateway.response_cache.ports.store import ResponseCacheStore


class RecordingFreshnessPolicy(FreshnessPolicy):
    """Internal-policy double that records each store lookup decision."""

    def __init__(self, decisions: list[bool]) -> None:
        self._decisions = decisions
        self.calls: list[tuple[datetime, datetime]] = []

    def is_fresh(self, *, written_at: datetime, now: datetime) -> bool:
        self.calls.append((written_at, now))
        return self._decisions.pop(0)


class RaisingThenRecordingFreshnessPolicy(FreshnessPolicy):
    """Policy double that fails once before returning recorded decisions."""

    def __init__(self, exception: Exception, decisions: list[bool]) -> None:
        self._exception = exception
        self._decisions = decisions
        self.calls: list[tuple[datetime, datetime]] = []

    def is_fresh(self, *, written_at: datetime, now: datetime) -> bool:
        self.calls.append((written_at, now))
        if len(self.calls) == 1:
            raise self._exception
        return self._decisions.pop(0)


def _key(feature_hash: str = "feature-hash") -> ResponseCacheKey:
    return ResponseCacheKey(
        namespace="response-cache",
        model_payload_hash="payload-hash",
        feature_hash=feature_hash,
    )


def test_in_memory_store_implements_unchanged_async_port_with_keyword_policy() -> None:
    """The concrete internal store must retain the locked port and injection shape."""
    init_signature = inspect.signature(InMemoryResponseCacheStore.__init__)

    assert issubclass(InMemoryResponseCacheStore, ResponseCacheStore)
    assert tuple(init_signature.parameters) == ("self", "freshness_policy")
    assert init_signature.parameters["freshness_policy"].kind is inspect.Parameter.KEYWORD_ONLY
    assert inspect.iscoroutinefunction(InMemoryResponseCacheStore.get)
    assert inspect.iscoroutinefunction(InMemoryResponseCacheStore.set)


@pytest.mark.asyncio
async def test_in_memory_store_returns_entry_when_injected_policy_reports_fresh() -> None:
    """A successful write must be returned while the injected policy says fresh."""
    policy = RecordingFreshnessPolicy([True])
    store = InMemoryResponseCacheStore(freshness_policy=policy)
    entry = ResponseCacheEntry(response="cached response")

    await store.set(key=_key(), entry=entry)

    assert await store.get(key=_key()) is entry
    assert len(policy.calls) == 1
    written_at, now = policy.calls[0]
    assert written_at.tzinfo is not None
    assert written_at.utcoffset() == timedelta(0)
    assert now.tzinfo is not None
    assert now.utcoffset() == timedelta(0)


@pytest.mark.asyncio
async def test_in_memory_store_reads_do_not_renew_original_write_timestamp() -> None:
    """Repeated fresh reads must delegate the timestamp established by set unchanged."""
    policy = RecordingFreshnessPolicy([True, True])
    store = InMemoryResponseCacheStore(freshness_policy=policy)
    entry = ResponseCacheEntry(response="cached response")

    await store.set(key=_key(), entry=entry)
    assert await store.get(key=_key()) is entry
    assert await store.get(key=_key()) is entry

    assert policy.calls[0][0] == policy.calls[1][0]


@pytest.mark.asyncio
async def test_in_memory_store_returns_none_when_injected_policy_reports_expired() -> None:
    """An expired record must be a normal miss and never leak stale content."""
    policy = RecordingFreshnessPolicy([False])
    store = InMemoryResponseCacheStore(freshness_policy=policy)

    await store.set(key=_key(), entry=ResponseCacheEntry(response="stale response"))

    assert await store.get(key=_key()) is None
    assert len(policy.calls) == 1


@pytest.mark.asyncio
async def test_in_memory_store_reclaims_stale_key_without_rechecking_and_allows_reinsertion() -> (
    None
):
    """A confirmed stale record is removed before a replacement is written."""
    policy = RecordingFreshnessPolicy([False, True])
    store = InMemoryResponseCacheStore(freshness_policy=policy)
    key = _key()
    replacement = ResponseCacheEntry(response="replacement response")

    await store.set(key=key, entry=ResponseCacheEntry(response="stale response"))

    assert await store.get(key=key) is None
    assert await store.get(key=key) is None
    assert len(policy.calls) == 1

    await store.set(key=key, entry=replacement)

    assert await store.get(key=key) is replacement
    assert len(policy.calls) == 2


@pytest.mark.asyncio
async def test_in_memory_store_preserves_record_when_policy_raises_until_stale_reclamation() -> (
    None
):
    """A policy exception is visible and does not itself reclaim the record."""
    policy_error = RuntimeError("freshness policy failed")
    policy = RaisingThenRecordingFreshnessPolicy(policy_error, [True, False])
    store = InMemoryResponseCacheStore(freshness_policy=policy)
    key = _key()
    entry = ResponseCacheEntry(response="cached response")

    await store.set(key=key, entry=entry)

    with pytest.raises(RuntimeError, match="freshness policy failed") as raised:
        await store.get(key=key)

    assert raised.value is policy_error
    assert await store.get(key=key) is entry
    assert await store.get(key=key) is None
    assert await store.get(key=key) is None
    assert len(policy.calls) == 3


@pytest.mark.asyncio
async def test_in_memory_store_reclaims_only_stale_key_and_keeps_other_key_readable() -> None:
    """Reclaiming one stale record cannot alter another key's fresh record."""
    policy = RecordingFreshnessPolicy([False, True])
    store = InMemoryResponseCacheStore(freshness_policy=policy)
    stale_key = _key("stale-feature-hash")
    fresh_key = _key("fresh-feature-hash")
    fresh_entry = ResponseCacheEntry(response="fresh response")

    await store.set(key=stale_key, entry=ResponseCacheEntry(response="stale response"))
    await store.set(key=fresh_key, entry=fresh_entry)

    assert await store.get(key=stale_key) is None
    assert await store.get(key=fresh_key) is fresh_entry
    assert await store.get(key=stale_key) is None
    assert len(policy.calls) == 2


@pytest.mark.asyncio
async def test_in_memory_store_overwrite_replaces_entry_and_write_timestamp(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A same-key overwrite must establish a new record rather than return old content."""
    policy = RecordingFreshnessPolicy([True, True])
    store = InMemoryResponseCacheStore(freshness_policy=policy)
    original = ResponseCacheEntry(response="original response")
    replacement = ResponseCacheEntry(response="replacement response")
    first_written_at = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)
    timestamps = iter(
        (
            first_written_at,
            first_written_at + timedelta(seconds=1),
            first_written_at + timedelta(seconds=2),
            first_written_at + timedelta(seconds=3),
        )
    )
    monkeypatch.setattr(in_memory_store_module, "_utc_now", lambda: next(timestamps))

    await store.set(key=_key(), entry=original)
    assert await store.get(key=_key()) is original

    await store.set(key=_key(), entry=replacement)
    assert await store.get(key=_key()) is replacement

    assert policy.calls[0][0] == first_written_at
    assert policy.calls[1][0] == first_written_at + timedelta(seconds=2)


@pytest.mark.asyncio
async def test_in_memory_store_isolates_entries_by_response_cache_key() -> None:
    """Distinct keys must not cross-return stored response-cache entries."""
    policy = RecordingFreshnessPolicy([True, True])
    store = InMemoryResponseCacheStore(freshness_policy=policy)
    first_entry = ResponseCacheEntry(response="first response")
    second_entry = ResponseCacheEntry(response="second response")
    first_key = _key("first-feature-hash")
    second_key = _key("second-feature-hash")

    await store.set(key=first_key, entry=first_entry)
    await store.set(key=second_key, entry=second_entry)

    assert await store.get(key=first_key) is first_entry
    assert await store.get(key=second_key) is second_entry
