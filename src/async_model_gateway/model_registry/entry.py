"""Concrete registry-entry surface."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

__all__ = ["ModelSourceKind", "RegistryEntry"]


class ModelSourceKind(str, Enum):
    """Allowed model-source kinds for registry identity."""

    LOCAL = "local"
    REMOTE = "remote"


@dataclass(frozen=True, slots=True)
class RegistryEntry:
    """Concrete registry entry keyed by model identity context."""

    model_name: str
    model_source_kind: ModelSourceKind
    payload_hash: str
