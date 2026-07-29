"""RED coverage for the internal in-memory response-cache store."""

from __future__ import annotations

import inspect
from datetime import datetime, timedelta

import pytest

from async_model_gateway.response_cache import ResponseCacheEntry, ResponseCacheKey
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
async def test_in_memory_store_overwrite_replaces_entry_and_write_timestamp() -> None:
    """A same-key overwrite must establish a new record rather than return old content."""
    policy = RecordingFreshnessPolicy([True, True])
    store = InMemoryResponseCacheStore(freshness_policy=policy)
    original = ResponseCacheEntry(response="original response")
    replacement = ResponseCacheEntry(response="replacement response")

    await store.set(key=_key(), entry=original)
    assert await store.get(key=_key()) is original
    first_written_at = policy.calls[0][0]

    await store.set(key=_key(), entry=replacement)
    assert await store.get(key=_key()) is replacement

    assert policy.calls[1][0] != first_written_at


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
