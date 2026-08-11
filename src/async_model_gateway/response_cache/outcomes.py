"""Closed outcomes for response-cache operations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

__all__ = [
    "CacheFailureKind",
    "CacheHit",
    "CacheMiss",
    "CacheSkipReason",
    "Failed",
    "Invalidated",
    "NotFound",
    "Remembered",
    "Skipped",
]


class CacheFailureKind(str, Enum):
    """Known operational failure owners."""

    STORE = "store"
    CODEC = "codec"
    VERSION_TOKEN = "version_token"


class CacheSkipReason(str, Enum):
    """Closed reasons for deliberately skipped writes."""

    CLOSED = "closed"


@dataclass(frozen=True, slots=True)
class CacheHit:
    """A decoded fresh response-cache value."""

    value: str


@dataclass(frozen=True, slots=True)
class CacheMiss:
    """A cache lookup without a supported fresh value."""


@dataclass(frozen=True, slots=True)
class Remembered:
    """A successful whole-record replacement."""


@dataclass(frozen=True, slots=True)
class Skipped:
    """A deliberately skipped write."""

    reason: CacheSkipReason

    def __post_init__(self) -> None:
        """Keep the skip outcome closed to the supported reason."""
        if self.reason is not CacheSkipReason.CLOSED:
            msg = "unsupported cache skip reason"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class Failed:
    """A classified operational write failure."""

    kind: CacheFailureKind

    def __post_init__(self) -> None:
        """Keep write failures within the declared error family."""
        if not _is_failure_kind(self.kind):
            msg = "unsupported cache failure kind"
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class Invalidated:
    """A key-local invalidation that removed a record."""


@dataclass(frozen=True, slots=True)
class NotFound:
    """A key-local invalidation that found no record."""


def _is_failure_kind(value: object) -> bool:
    """Return whether a runtime value belongs to the closed failure enum."""
    return isinstance(value, CacheFailureKind)
