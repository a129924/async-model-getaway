"""RED coverage for the target two-method response-cache facade."""

from __future__ import annotations

import asyncio
import inspect
from datetime import datetime, timedelta, timezone

import pytest


def _key() -> object:
    from async_model_gateway.response_cache.key import CacheKey

    return CacheKey("response-cache", "payload", "feature")


def _record(*, value: str, token: str, expires_at: datetime | None = None) -> object:
    from async_model_gateway.response_cache.record import CacheVersionToken, StoredCacheRecord

    written_at = datetime(2026, 8, 6, 12, 0, tzinfo=timezone.utc)
    return StoredCacheRecord(
        schema_version=1,
        codec_id="utf-8",
        payload=value.encode(),
        written_at=written_at,
        expires_at=expires_at or written_at + timedelta(seconds=30),
        version_token=CacheVersionToken(value=token),
        metadata=(),
    )


def test_response_cache_has_exactly_five_keyword_only_collaborators_and_two_methods() -> None:
    """The root facade must not retain any old synchronous or invalidation surface."""
    from async_model_gateway.response_cache.cache import ResponseCache

    constructor = inspect.signature(ResponseCache.__init__)

    assert tuple(constructor.parameters) == (
        "self",
        "store",
        "codec",
        "version_token_factory",
        "freshness_policy",
        "clock",
    )
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY
        for name, parameter in constructor.parameters.items()
        if name != "self"
    )
    assert inspect.iscoroutinefunction(ResponseCache.lookup)
    assert inspect.iscoroutinefunction(ResponseCache.remember)
    assert not any(hasattr(ResponseCache, name) for name in ("get", "set", "invalidate"))


@pytest.mark.asyncio
async def test_lookup_returns_hit_for_fresh_supported_record_without_observing_context() -> None:
    """A context is invocation-only and neither changes reads nor reaches persistence."""
    from async_model_gateway.response_cache.cache import ResponseCache
    from async_model_gateway.response_cache.outcomes import CacheHit

    class Store:
        async def get(self, *, key: object) -> object:
            return _record(value="cached", token="A")

        async def set(self, *, key: object, record: object) -> None:
            raise AssertionError("lookup must not write")

        async def delete(self, *, key: object) -> bool:
            raise AssertionError("lookup must use compare-delete only")

        async def delete_if_version(self, *, key: object, version_token: object) -> bool:
            raise AssertionError("fresh lookup must not clean up")

    class Codec:
        codec_id = "utf-8"

        def encode(self, *, value: str) -> bytes:
            return value.encode()

        def decode(self, *, payload: bytes) -> str:
            return payload.decode()

    class Tokens:
        def new(self) -> object:
            raise AssertionError("lookup must not create a token")

    class Policy:
        def expires_at(self, *, written_at: datetime) -> datetime:
            return written_at + timedelta(seconds=30)

    class ExplodingContext:
        def __getattribute__(self, name: str) -> object:
            raise AssertionError(f"context was observed through {name}")

    cache = ResponseCache(
        store=Store(),
        codec=Codec(),
        version_token_factory=Tokens(),
        freshness_policy=Policy(),
        clock=lambda: datetime(2026, 8, 6, tzinfo=timezone.utc),
    )

    result = await cache.lookup(key=_key(), context=ExplodingContext())

    assert result == CacheHit(value="cached")


@pytest.mark.asyncio
async def test_remember_writes_one_complete_facade_owned_record_and_returns_remembered() -> None:
    """The facade owns timestamps, codec id, expiry, token request, and empty metadata."""
    from async_model_gateway.response_cache.cache import ResponseCache
    from async_model_gateway.response_cache.outcomes import Remembered
    from async_model_gateway.response_cache.record import CacheVersionToken

    written_at = datetime(2026, 8, 6, 12, 0, tzinfo=timezone.utc)

    class Store:
        def __init__(self) -> None:
            self.records: list[tuple[object, object]] = []

        async def get(self, *, key: object) -> None:
            return None

        async def set(self, *, key: object, record: object) -> None:
            self.records.append((key, record))

        async def delete(self, *, key: object) -> bool:
            return False

        async def delete_if_version(self, *, key: object, version_token: object) -> bool:
            return False

    class Codec:
        codec_id = "test-codec"

        def encode(self, *, value: str) -> bytes:
            assert value == "generated"
            return b"encoded"

        def decode(self, *, payload: bytes) -> str:
            return payload.decode()

    class Tokens:
        def __init__(self) -> None:
            self.calls = 0

        def new(self) -> CacheVersionToken:
            self.calls += 1
            return CacheVersionToken(value="new-token")

    class Policy:
        def __init__(self) -> None:
            self.calls: list[datetime] = []

        def expires_at(self, *, written_at: datetime) -> datetime:
            self.calls.append(written_at)
            return written_at + timedelta(seconds=30)

    class ExplodingContext:
        def __getattribute__(self, name: str) -> object:
            raise AssertionError(f"context was observed through {name}")

    store = Store()
    tokens = Tokens()
    policy = Policy()
    clock_calls: list[None] = []
    cache = ResponseCache(
        store=store,
        codec=Codec(),
        version_token_factory=tokens,
        freshness_policy=policy,
        clock=lambda: (clock_calls.append(None), written_at)[1],
    )

    result = await cache.remember(key=_key(), value="generated", context=ExplodingContext())

    assert result == Remembered()
    assert len(clock_calls) == 1
    assert tokens.calls == 1
    assert policy.calls == [written_at]
    assert len(store.records) == 1
    stored_key, record = store.records[0]
    assert stored_key == _key()
    assert record.schema_version == 1
    assert record.codec_id == "test-codec"
    assert record.payload == b"encoded"
    assert record.written_at == written_at
    assert record.expires_at == written_at + timedelta(seconds=30)
    assert record.version_token == CacheVersionToken(value="new-token")
    assert record.metadata == ()


@pytest.mark.asyncio
@pytest.mark.parametrize("schema_version, expires_offset, lookup_offset", [(1, 1, 2)])
async def test_lookup_misses_and_compare_deletes_expired_records(
    schema_version: int, expires_offset: int, lookup_offset: int
) -> None:
    """Expired records cannot leak a value and cleanup uses the observed token."""
    from async_model_gateway.response_cache.cache import ResponseCache
    from async_model_gateway.response_cache.outcomes import CacheMiss
    from async_model_gateway.response_cache.record import CacheVersionToken, StoredCacheRecord

    written_at = datetime(2026, 8, 6, 12, 0, tzinfo=timezone.utc)
    record = StoredCacheRecord(
        schema_version=schema_version,
        codec_id="utf-8",
        payload=b"value",
        written_at=written_at,
        expires_at=written_at + timedelta(seconds=expires_offset),
        version_token=CacheVersionToken(value="observed"),
        metadata=(),
    )

    class Store:
        def __init__(self) -> None:
            self.deleted: list[tuple[object, object]] = []

        async def get(self, *, key: object) -> object:
            return record

        async def set(self, *, key: object, record: object) -> None:
            raise AssertionError("lookup must not write")

        async def delete(self, *, key: object) -> bool:
            raise AssertionError("unconditional stale delete is forbidden")

        async def delete_if_version(self, *, key: object, version_token: object) -> bool:
            self.deleted.append((key, version_token))
            return True

    class Codec:
        codec_id = "utf-8"

        def encode(self, *, value: str) -> bytes:
            return value.encode()

        def decode(self, *, payload: bytes) -> str:
            return payload.decode()

    store = Store()
    cache = ResponseCache(
        store=store,
        codec=Codec(),
        version_token_factory=object(),
        freshness_policy=object(),
        clock=lambda: written_at + timedelta(seconds=lookup_offset),
    )

    assert await cache.lookup(key=_key(), context=object()) == CacheMiss()
    assert store.deleted == [(_key(), CacheVersionToken(value="observed"))]


@pytest.mark.asyncio
async def test_lookup_maps_known_failure_to_miss_and_propagates_cancellation() -> None:
    """The facade catches only its operational family; cancellation remains caller-owned."""
    from async_model_gateway.response_cache.cache import ResponseCache
    from async_model_gateway.response_cache.errors import CacheStoreOperationalError
    from async_model_gateway.response_cache.outcomes import CacheMiss

    class Store:
        async def get(self, *, key: object) -> object:
            raise CacheStoreOperationalError()

        async def set(self, *, key: object, record: object) -> None:
            return None

        async def delete(self, *, key: object) -> bool:
            return False

        async def delete_if_version(self, *, key: object, version_token: object) -> bool:
            return False

    cache = ResponseCache(
        store=Store(),
        codec=object(),
        version_token_factory=object(),
        freshness_policy=object(),
        clock=lambda: datetime.now(timezone.utc),
    )

    assert await cache.lookup(key=_key(), context=object()) == CacheMiss()

    class CancelledStore(Store):
        async def get(self, *, key: object) -> object:
            raise asyncio.CancelledError()

    cancelled_cache = ResponseCache(
        store=CancelledStore(),
        codec=object(),
        version_token_factory=object(),
        freshness_policy=object(),
        clock=lambda: datetime.now(timezone.utc),
    )
    with pytest.raises(asyncio.CancelledError):
        await cancelled_cache.lookup(key=_key(), context=object())


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_name, expected_kind, closed",
    [
        ("CacheStoreOperationalError", "STORE", False),
        ("CacheClosedStoreError", "CLOSED", True),
        ("CacheCodecOperationalError", "CODEC", False),
        ("CacheVersionTokenOperationalError", "VERSION_TOKEN", False),
    ],
)
async def test_remember_maps_every_known_operational_failure_to_the_closed_outcome(
    error_name: str, expected_kind: str, closed: bool
) -> None:
    """Closed stores skip; all other known collaborator failures become matching Failed values."""
    from async_model_gateway.response_cache.cache import ResponseCache
    from async_model_gateway.response_cache import errors, outcomes

    error_type = getattr(errors, error_name)

    class Store:
        async def get(self, *, key: object) -> None:
            return None

        async def set(self, *, key: object, record: object) -> None:
            if expected_kind == "STORE" or closed:
                raise error_type()

        async def delete(self, *, key: object) -> bool:
            return False

        async def delete_if_version(self, *, key: object, version_token: object) -> bool:
            return False

    class Codec:
        codec_id = "utf-8"

        def encode(self, *, value: str) -> bytes:
            if expected_kind == "CODEC":
                raise error_type()
            return value.encode()

        def decode(self, *, payload: bytes) -> str:
            return payload.decode()

    class Tokens:
        def new(self) -> object:
            if expected_kind == "VERSION_TOKEN":
                raise error_type()
            from async_model_gateway.response_cache.record import CacheVersionToken

            return CacheVersionToken(value="token")

    class Policy:
        def expires_at(self, *, written_at: datetime) -> datetime:
            return written_at + timedelta(seconds=1)

    result = await ResponseCache(
        store=Store(),
        codec=Codec(),
        version_token_factory=Tokens(),
        freshness_policy=Policy(),
        clock=lambda: datetime(2026, 8, 6, tzinfo=timezone.utc),
    ).remember(key=_key(), value="value", context=object())

    if closed:
        assert result == outcomes.Skipped(reason=outcomes.CacheSkipReason.CLOSED)
    else:
        assert result == outcomes.Failed(kind=getattr(outcomes.CacheFailureKind, expected_kind))


@pytest.mark.asyncio
async def test_remember_propagates_awaited_store_cancellation_unchanged_without_outcome() -> None:
    """A store cancellation is caller-owned, not a remember result."""
    from async_model_gateway.response_cache.cache import ResponseCache
    from async_model_gateway.response_cache.record import CacheVersionToken

    cancellation = asyncio.CancelledError("store write cancelled")

    class Store:
        def __init__(self) -> None:
            self.records: list[tuple[object, object]] = []

        async def get(self, *, key: object) -> None:
            return None

        async def set(self, *, key: object, record: object) -> None:
            self.records.append((key, record))
            raise cancellation

        async def delete(self, *, key: object) -> bool:
            return False

        async def delete_if_version(self, *, key: object, version_token: object) -> bool:
            return False

    class Codec:
        codec_id = "utf-8"

        def encode(self, *, value: str) -> bytes:
            return value.encode()

        def decode(self, *, payload: bytes) -> str:
            return payload.decode()

    class Tokens:
        def new(self) -> CacheVersionToken:
            return CacheVersionToken(value="token")

    class Policy:
        def expires_at(self, *, written_at: datetime) -> datetime:
            return written_at + timedelta(seconds=1)

    store = Store()
    cache = ResponseCache(
        store=store,
        codec=Codec(),
        version_token_factory=Tokens(),
        freshness_policy=Policy(),
        clock=lambda: datetime(2026, 8, 6, tzinfo=timezone.utc),
    )

    with pytest.raises(asyncio.CancelledError) as raised:
        await cache.remember(key=_key(), value="value", context=object())

    assert raised.value is cancellation
    assert store.records[0][0] == _key()
