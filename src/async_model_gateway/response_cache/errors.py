"""Closed operational error family for response-cache collaborators."""

from __future__ import annotations

from .outcomes import CacheFailureKind

__all__ = [
    "CacheClosedStoreError",
    "CacheCodecOperationalError",
    "CacheOperationalError",
    "CacheStoreOperationalError",
    "CacheVersionTokenOperationalError",
]


class CacheOperationalError(Exception):
    """Base class for expected cache collaborator operational failures."""

    kind: CacheFailureKind


class CacheStoreOperationalError(CacheOperationalError):
    """Expected store operation failure."""

    kind = CacheFailureKind.STORE


class CacheClosedStoreError(CacheStoreOperationalError):
    """Known store-closed signal for a skipped write."""


class CacheCodecOperationalError(CacheOperationalError):
    """Expected codec operation failure."""

    kind = CacheFailureKind.CODEC


class CacheVersionTokenOperationalError(CacheOperationalError):
    """Expected opaque token generation failure."""

    kind = CacheFailureKind.VERSION_TOKEN
