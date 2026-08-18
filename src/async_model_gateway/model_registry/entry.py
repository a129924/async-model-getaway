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

    @property
    def model_identity_hash(self) -> str:
        """Derive the complete model identity without storing additional state."""
        from .model_identity import ModelIdentityHasher

        return ModelIdentityHasher.hash_model_identity(
            model_name=self.model_name,
            model_source_kind=self.model_source_kind,
            model_payload_hash=self.payload_hash,
        )
