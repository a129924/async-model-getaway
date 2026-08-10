"""RED cross-contract coverage for migration-only behavior and record validation."""

from __future__ import annotations

import asyncio
from dataclasses import fields, is_dataclass
from datetime import datetime, timedelta, timezone

import pytest


def test_stored_record_and_version_token_are_immutable_and_validate_the_contract() -> None:
    """Records accept only the frozen schema, aware UTC ordering, and bounded metadata."""
    from async_model_gateway.response_cache.record import CacheVersionToken, StoredCacheRecord

    written_at = datetime(2026, 8, 6, tzinfo=timezone.utc)
    token = CacheVersionToken(value="opaque")
    record = StoredCacheRecord(
        schema_version=1,
        codec_id="utf-8",
        payload=b"value",
        written_at=written_at,
        expires_at=written_at + timedelta(seconds=1),
        version_token=token,
        metadata=(("source", "test"),),
    )

    assert is_dataclass(record)
    assert record.__dataclass_params__.frozen is True
    assert [field.name for field in fields(record)] == [
        "schema_version",
        "codec_id",
        "payload",
        "written_at",
        "expires_at",
        "version_token",
        "metadata",
    ]
    for expires_at in (written_at, written_at - timedelta(seconds=1)):
        with pytest.raises(ValueError):
            StoredCacheRecord(1, "utf-8", b"value", written_at, expires_at, token, ())
    for schema_version in (0, 2):
        with pytest.raises(ValueError, match="schema_version must be exactly 1"):
            StoredCacheRecord(
                schema_version,
                "utf-8",
                b"value",
                written_at,
                written_at + timedelta(seconds=1),
                token,
                (),
            )
    with pytest.raises(ValueError):
        StoredCacheRecord(
            1,
            "utf-8",
            b"value",
            written_at,
            written_at + timedelta(seconds=1),
            token,
            tuple((str(index), "v") for index in range(9)),
        )


@pytest.mark.asyncio
async def test_stale_cleanup_race_keeps_concurrent_replacement_and_original_lookup_is_miss() -> (
    None
):
    """The facade sends the observed token to atomic compare-delete, never unconditional delete."""
    from async_model_gateway.response_cache.cache import ResponseCache
    from async_model_gateway.response_cache.outcomes import CacheMiss
    from async_model_gateway.response_cache.record import CacheVersionToken, StoredCacheRecord

    written_at = datetime(2026, 8, 6, tzinfo=timezone.utc)
    observed = StoredCacheRecord(
        1,
        "utf-8",
        b"old",
        written_at,
        written_at + timedelta(seconds=1),
        CacheVersionToken(value="A"),
        (),
    )
    replacement = StoredCacheRecord(
        1,
        "utf-8",
        b"new",
        written_at,
        written_at + timedelta(days=1),
        CacheVersionToken(value="B"),
        (),
    )

    class Store:
        record = observed

        async def get(self, *, key: object) -> object:
            return self.record

        async def set(self, *, key: object, record: object) -> None:
            self.record = record

        async def delete(self, *, key: object) -> bool:
            raise AssertionError("cleanup must not use delete")

        async def delete_if_version(self, *, key: object, version_token: object) -> bool:
            self.record = replacement
            return False

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
        clock=lambda: written_at + timedelta(days=2),
    )

    assert await cache.lookup(key=object(), context=object()) == CacheMiss()
    assert store.record is replacement


@pytest.mark.asyncio
async def test_legacy_adapter_maps_set_and_invalidate_cancellation() -> None:
    """Compatibility maps outcomes only; its invalidator remains a separate async collaborator."""
    import async_model_gateway.response_cache.compat as compat
    from async_model_gateway.response_cache.outcomes import (
        CacheFailureKind,
        CacheSkipReason,
        Failed,
        Invalidated,
        NotFound,
        Remembered,
        Skipped,
    )

    class Facade:
        def __init__(self, result: object) -> None:
            self.result = result
            self.contexts: list[object] = []

        async def remember(self, *, key: object, value: str, context: object) -> object:
            self.contexts.append(context)
            if isinstance(self.result, BaseException):
                raise self.result
            return self.result

    class Invalidator:
        def __init__(self, result: object) -> None:
            self.result = result

        async def invalidate(self, *, key: object) -> object:
            if isinstance(self.result, BaseException):
                raise self.result
            return self.result

    with pytest.warns(DeprecationWarning):
        adapter = compat.LegacyResponseCacheAdapter(
            facade=Facade(Remembered()), invalidator=Invalidator(Invalidated())
        )
    assert await adapter.set(key=object(), entry=compat.ResponseCacheEntry("value")) is None
    assert await adapter.invalidate(key=object()) is True

    with pytest.warns(DeprecationWarning):
        closed_adapter = compat.LegacyResponseCacheAdapter(
            facade=Facade(Skipped(CacheSkipReason.CLOSED)), invalidator=Invalidator(NotFound())
        )
    with pytest.raises(compat.LegacyCacheClosedError):
        await closed_adapter.set(key=object(), entry=compat.ResponseCacheEntry("value"))
    assert await closed_adapter.invalidate(key=object()) is False

    with pytest.warns(DeprecationWarning):
        failed_adapter = compat.LegacyResponseCacheAdapter(
            facade=Facade(Failed(CacheFailureKind.CODEC)),
            invalidator=Invalidator(asyncio.CancelledError()),
        )
    with pytest.raises(compat.LegacyCacheOperationError):
        await failed_adapter.set(key=object(), entry=compat.ResponseCacheEntry("value"))
    with pytest.raises(asyncio.CancelledError):
        await failed_adapter.invalidate(key=object())

    with pytest.warns(DeprecationWarning):
        cancelled_adapter = compat.LegacyResponseCacheAdapter(
            facade=Facade(asyncio.CancelledError()), invalidator=Invalidator(NotFound())
        )
    with pytest.raises(asyncio.CancelledError):
        await cancelled_adapter.set(key=object(), entry=compat.ResponseCacheEntry("value"))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error_type",
    [
        "CacheStoreOperationalError",
        "CacheClosedStoreError",
        "CacheCodecOperationalError",
        "CacheVersionTokenOperationalError",
    ],
)
async def test_lookup_maps_each_known_operational_error_to_miss(
    error_type: str,
) -> None:
    """Lookup closes every expected collaborator operational failure to a miss."""
    from async_model_gateway.response_cache.cache import ResponseCache
    from async_model_gateway.response_cache.errors import (
        CacheClosedStoreError,
        CacheCodecOperationalError,
        CacheOperationalError,
        CacheStoreOperationalError,
        CacheVersionTokenOperationalError,
    )
    from async_model_gateway.response_cache.outcomes import CacheMiss

    errors: dict[str, type[CacheOperationalError]] = {
        "CacheStoreOperationalError": CacheStoreOperationalError,
        "CacheClosedStoreError": CacheClosedStoreError,
        "CacheCodecOperationalError": CacheCodecOperationalError,
        "CacheVersionTokenOperationalError": CacheVersionTokenOperationalError,
    }

    class Store:
        async def get(self, *, key: object) -> object:
            raise errors[error_type]()

        async def set(self, *, key: object, record: object) -> None:
            raise AssertionError("lookup must not write")

        async def delete(self, *, key: object) -> bool:
            raise AssertionError("lookup must not invalidate")

        async def delete_if_version(self, *, key: object, version_token: object) -> bool:
            raise AssertionError("failed lookup must not clean up")

    cache = ResponseCache(
        store=Store(),
        codec=object(),
        version_token_factory=object(),
        freshness_policy=object(),
        clock=lambda: datetime(2026, 8, 6, tzinfo=timezone.utc),
    )

    assert await cache.lookup(key=object(), context=object()) == CacheMiss()


@pytest.mark.asyncio
async def test_lookup_cleanup_operational_failure_remains_a_miss() -> None:
    """Best-effort stale cleanup never turns a miss into an exception."""
    from async_model_gateway.response_cache.cache import ResponseCache
    from async_model_gateway.response_cache.errors import CacheStoreOperationalError
    from async_model_gateway.response_cache.outcomes import CacheMiss
    from async_model_gateway.response_cache.record import CacheVersionToken, StoredCacheRecord

    written_at = datetime(2026, 8, 6, tzinfo=timezone.utc)
    expired = StoredCacheRecord(
        1,
        "utf-8",
        b"expired",
        written_at,
        written_at + timedelta(seconds=1),
        CacheVersionToken(value="observed"),
        (),
    )

    class Store:
        async def get(self, *, key: object) -> object:
            return expired

        async def set(self, *, key: object, record: object) -> None:
            raise AssertionError("lookup must not write")

        async def delete(self, *, key: object) -> bool:
            raise AssertionError("stale cleanup must compare-delete")

        async def delete_if_version(self, *, key: object, version_token: object) -> bool:
            raise CacheStoreOperationalError()

    class Codec:
        codec_id = "utf-8"

        def encode(self, *, value: str) -> bytes:
            return value.encode()

        def decode(self, *, payload: bytes) -> str:
            return payload.decode()

    cache = ResponseCache(
        store=Store(),
        codec=Codec(),
        version_token_factory=object(),
        freshness_policy=object(),
        clock=lambda: written_at + timedelta(days=1),
    )

    assert await cache.lookup(key=object(), context=object()) == CacheMiss()


@pytest.mark.asyncio
async def test_lookup_cleanup_propagates_cancelled_error_identity() -> None:
    """Cancellation from compare-delete remains visible to the lookup caller."""
    from async_model_gateway.response_cache.cache import ResponseCache
    from async_model_gateway.response_cache.record import CacheVersionToken, StoredCacheRecord

    written_at = datetime(2026, 8, 6, tzinfo=timezone.utc)
    expired = StoredCacheRecord(
        1,
        "utf-8",
        b"expired",
        written_at,
        written_at + timedelta(seconds=1),
        CacheVersionToken(value="observed"),
        (),
    )
    cancellation = asyncio.CancelledError("sentinel stale-cleanup cancellation")

    class Store:
        async def get(self, *, key: object) -> object:
            return expired

        async def set(self, *, key: object, record: object) -> None:
            raise AssertionError("lookup must not write")

        async def delete(self, *, key: object) -> bool:
            raise AssertionError("stale cleanup must compare-delete")

        async def delete_if_version(self, *, key: object, version_token: object) -> bool:
            raise cancellation

    class Codec:
        codec_id = "utf-8"

        def encode(self, *, value: str) -> bytes:
            return value.encode()

        def decode(self, *, payload: bytes) -> str:
            return payload.decode()

    cache = ResponseCache(
        store=Store(),
        codec=Codec(),
        version_token_factory=object(),
        freshness_policy=object(),
        clock=lambda: written_at + timedelta(days=1),
    )

    with pytest.raises(asyncio.CancelledError) as raised:
        await cache.lookup(key=object(), context=object())

    assert raised.value is cancellation


@pytest.mark.asyncio
async def test_lookup_cleanup_propagates_unexpected_runtime_error_identity() -> None:
    """Unexpected compare-delete defects never become a stale cache miss."""
    from async_model_gateway.response_cache.cache import ResponseCache
    from async_model_gateway.response_cache.record import CacheVersionToken, StoredCacheRecord

    written_at = datetime(2026, 8, 6, tzinfo=timezone.utc)
    expired = StoredCacheRecord(
        1,
        "utf-8",
        b"expired",
        written_at,
        written_at + timedelta(seconds=1),
        CacheVersionToken(value="observed"),
        (),
    )
    defect = RuntimeError("sentinel stale-cleanup defect")

    class Store:
        async def get(self, *, key: object) -> object:
            return expired

        async def set(self, *, key: object, record: object) -> None:
            raise AssertionError("lookup must not write")

        async def delete(self, *, key: object) -> bool:
            raise AssertionError("stale cleanup must compare-delete")

        async def delete_if_version(self, *, key: object, version_token: object) -> bool:
            raise defect

    class Codec:
        codec_id = "utf-8"

        def encode(self, *, value: str) -> bytes:
            return value.encode()

        def decode(self, *, payload: bytes) -> str:
            return payload.decode()

    cache = ResponseCache(
        store=Store(),
        codec=Codec(),
        version_token_factory=object(),
        freshness_policy=object(),
        clock=lambda: written_at + timedelta(days=1),
    )

    with pytest.raises(RuntimeError) as raised:
        await cache.lookup(key=object(), context=object())

    assert raised.value is defect


@pytest.mark.asyncio
async def test_store_backed_invalidator_is_key_local_and_propagates_failures() -> None:
    """Invalidation alone maps ordinary deletion results; errors stay caller-visible."""
    from async_model_gateway.response_cache.errors import CacheStoreOperationalError
    from async_model_gateway.response_cache.invalidation import StoreCacheInvalidator
    from async_model_gateway.response_cache.outcomes import Invalidated, NotFound

    class Store:
        def __init__(self) -> None:
            self.present = True

        async def delete(self, *, key: object) -> bool:
            if key == "operational":
                raise CacheStoreOperationalError()
            if key == "cancelled":
                raise asyncio.CancelledError()
            was_present = self.present
            self.present = False
            return was_present

    invalidator = StoreCacheInvalidator(store=Store())

    assert await invalidator.invalidate(key="key") == Invalidated()
    assert await invalidator.invalidate(key="key") == NotFound()
    with pytest.raises(CacheStoreOperationalError):
        await invalidator.invalidate(key="operational")
    with pytest.raises(asyncio.CancelledError):
        await invalidator.invalidate(key="cancelled")
