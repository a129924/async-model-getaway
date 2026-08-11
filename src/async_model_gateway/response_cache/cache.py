"""The two-operation response-cache facade."""

# pyright: reportInvalidTypeVarUse=false

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import TypeVar

from .errors import CacheClosedStoreError, CacheOperationalError
from .freshness_policy import FreshnessPolicy
from .key import CacheKey
from .outcomes import (
    CacheFailureKind,
    CacheHit,
    CacheMiss,
    CacheSkipReason,
    Failed,
    Remembered,
    Skipped,
)
from .ports.codec import CacheCodec
from .ports.store import CacheStore
from .ports.version_token_factory import VersionTokenFactory
from .record import CacheVersionToken, StoredCacheRecord, UnsupportedSchemaRecord

__all__ = ["ResponseCache"]

ContextT = TypeVar("ContextT")


def _require_aware_utc(timestamp: datetime) -> None:
    """Reject timestamps that do not represent an aware UTC instant."""
    if timestamp.tzinfo is None or timestamp.utcoffset() != timedelta(0):
        msg = "cache clock must return an aware UTC timestamp"
        raise ValueError(msg)


class ResponseCache:
    """Own cache-record construction and closed facade outcomes."""

    def __init__(
        self,
        *,
        store: CacheStore,
        codec: CacheCodec,
        version_token_factory: VersionTokenFactory,
        freshness_policy: FreshnessPolicy,
        clock: Callable[[], datetime],
    ) -> None:
        """Bind the five collaborators required by the target contract."""
        self._store = store
        self._codec = codec
        self._version_token_factory = version_token_factory
        self._freshness_policy = freshness_policy
        self._clock = clock

    async def lookup(self, *, key: CacheKey, context: ContextT) -> CacheHit | CacheMiss:
        """Return a decoded fresh value; ``context`` is an ignored compatibility sentinel."""
        del context
        try:
            record = await self._store.get(key=key)
            if record is None:
                return CacheMiss()
            if isinstance(record, UnsupportedSchemaRecord):
                return await self._cleanup_stale(key=key, version_token=record.version_token)

            now = self._clock()
            _require_aware_utc(now)
            if record.schema_version != 1 or record.codec_id != self._codec.codec_id:
                return await self._cleanup_stale(key=key, version_token=record.version_token)
            if record.expires_at <= now:
                return await self._cleanup_stale(key=key, version_token=record.version_token)

            return CacheHit(value=self._codec.decode(payload=record.payload))
        except CacheOperationalError:
            return CacheMiss()

    async def remember(
        self, *, key: CacheKey, value: str, context: ContextT
    ) -> Remembered | Skipped | Failed:
        """Write one record; ``context`` is an ignored compatibility sentinel."""
        del context
        try:
            written_at = self._clock()
            _require_aware_utc(written_at)
            expires_at = self._freshness_policy.expires_at(written_at=written_at)
            _require_aware_utc(expires_at)
            if expires_at <= written_at:
                msg = "expires_at must be later than written_at"
                raise ValueError(msg)
            record = StoredCacheRecord(
                schema_version=1,
                codec_id=self._codec.codec_id,
                payload=self._codec.encode(value=value),
                written_at=written_at,
                expires_at=expires_at,
                version_token=self._version_token_factory.new(),
                metadata=(),
            )
            await self._store.set(key=key, record=record)
            return Remembered()
        except CacheClosedStoreError:
            return Skipped(reason=CacheSkipReason.CLOSED)
        except CacheOperationalError as error:
            return Failed(kind=_failure_kind(error))

    async def _cleanup_stale(self, *, key: CacheKey, version_token: CacheVersionToken) -> CacheMiss:
        """Best-effort token-guarded cleanup that preserves replacements."""
        try:
            await self._store.delete_if_version(key=key, version_token=version_token)
        except CacheOperationalError:
            return CacheMiss()
        return CacheMiss()


def _failure_kind(error: CacheOperationalError) -> CacheFailureKind:
    """Return the explicitly declared kind from a known operational error."""
    return error.kind
