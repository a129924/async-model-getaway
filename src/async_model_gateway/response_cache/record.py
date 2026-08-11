"""Immutable stored response-cache record contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TypeGuard

__all__ = ["CacheVersionToken", "StoredCacheRecord"]

_MAX_METADATA_ITEMS = 8
_MAX_METADATA_KEY_BYTES = 64
_MAX_METADATA_VALUE_BYTES = 256
_MAX_METADATA_BYTES = 2 * 1024


def _is_aware_utc(value: datetime) -> bool:
    """Return whether ``value`` is an aware timestamp at the UTC offset."""
    return value.tzinfo is not None and value.utcoffset() == timedelta(0)


@dataclass(frozen=True, slots=True)
class CacheVersionToken:
    """Opaque version material used only for compare-delete."""

    value: str

    def __post_init__(self) -> None:
        """Reject empty or non-string token material."""
        if not _is_non_empty_string(self.value):
            msg = "version token must be a non-empty string"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class UnsupportedSchemaRecord:
    """Internal read marker for a reclaimable non-current stored schema."""

    schema_version: int
    version_token: CacheVersionToken

    def __post_init__(self) -> None:
        """Accept only a non-boolean schema version other than the supported one."""
        if not _is_schema_version(self.schema_version) or self.schema_version == 1:
            msg = "unsupported schema_version must be a non-1 integer"
            raise ValueError(msg)
        if not _is_version_token(self.version_token):
            msg = "version_token must be a CacheVersionToken"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class StoredCacheRecord:
    """One complete, immutable cache storage envelope."""

    schema_version: int
    codec_id: str
    payload: bytes
    written_at: datetime
    expires_at: datetime
    version_token: CacheVersionToken
    metadata: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        """Validate the closed record schema and metadata limits."""
        if not _is_schema_version(self.schema_version) or self.schema_version != 1:
            msg = "schema_version must be exactly 1"
            raise ValueError(msg)
        if not _is_non_empty_string(self.codec_id):
            msg = "codec_id must be a non-empty string"
            raise ValueError(msg)
        if not _is_bytes(self.payload):
            msg = "payload must be bytes"
            raise ValueError(msg)
        if not _is_aware_utc(self.written_at) or not _is_aware_utc(self.expires_at):
            msg = "cache record timestamps must be aware UTC values"
            raise ValueError(msg)
        if self.expires_at <= self.written_at:
            msg = "expires_at must be later than written_at"
            raise ValueError(msg)
        if not _is_version_token(self.version_token):
            msg = "version_token must be a CacheVersionToken"
            raise ValueError(msg)
        _validate_metadata(self.metadata)


def _is_non_empty_string(value: object) -> bool:
    """Return whether a runtime value is a non-empty string."""
    return isinstance(value, str) and bool(value)


def _is_schema_version(value: object) -> bool:
    """Return whether a runtime value is a non-boolean integer schema marker."""
    return isinstance(value, int) and not isinstance(value, bool)


def _is_bytes(value: object) -> bool:
    """Return whether a runtime value is immutable bytes payload material."""
    return isinstance(value, bytes)


def _is_version_token(value: object) -> bool:
    """Return whether a runtime value is the opaque token value object."""
    return isinstance(value, CacheVersionToken)


def _validate_metadata(metadata: object) -> None:
    """Enforce the fixed UTF-8 metadata budget."""
    if not _is_metadata_tuple(metadata):
        msg = "metadata must be a tuple of string pairs"
        raise ValueError(msg)
    items = metadata
    if len(items) > _MAX_METADATA_ITEMS:
        msg = "metadata has too many items"
        raise ValueError(msg)
    total_bytes = 0
    for item in items:
        if not _is_metadata_pair(item):
            msg = "metadata items must be string pairs"
            raise ValueError(msg)
        key, value = item
        if not isinstance(key, str) or not isinstance(value, str):
            msg = "metadata items must be string pairs"
            raise ValueError(msg)
        key_size = len(key.encode("utf-8"))
        value_size = len(value.encode("utf-8"))
        if key_size > _MAX_METADATA_KEY_BYTES or value_size > _MAX_METADATA_VALUE_BYTES:
            msg = "metadata item exceeds its byte limit"
            raise ValueError(msg)
        total_bytes += key_size + value_size
    if total_bytes > _MAX_METADATA_BYTES:
        msg = "metadata exceeds its byte limit"
        raise ValueError(msg)


def _is_metadata_pair(value: object) -> TypeGuard[tuple[object, object]]:
    """Narrow untrusted metadata tuple items to exactly two values."""
    if not _is_metadata_tuple(value):
        return False
    return len(value) == 2


def _is_metadata_tuple(value: object) -> TypeGuard[tuple[object, ...]]:
    """Narrow untrusted metadata to the immutable top-level tuple shape."""
    return isinstance(value, tuple)
