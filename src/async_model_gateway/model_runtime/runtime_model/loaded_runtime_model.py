"""Passive resource state for one loaded provider runtime."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Generic, TypeVar

RuntimeT = TypeVar("RuntimeT")


def _utc_now() -> datetime:
    """Return the current aware UTC timestamp."""
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class LoadedRuntimeModel(Generic[RuntimeT]):
    """Store a loaded provider runtime and its execution state."""

    runtime: RuntimeT
    execution_gate: asyncio.Semaphore
    loaded_at: datetime = field(default_factory=_utc_now)
    last_used_at: datetime | None = None

    def mark_used(self) -> None:
        """Record that execution has begun for this runtime."""
        self.last_used_at = _utc_now()
