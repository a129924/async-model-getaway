"""Feature-hash authority boundary for response-cache key construction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping

__all__ = ["FeatureHasher"]


class FeatureHasher(ABC):
    """Abstract feature-hash collaborator held by the key factory."""

    @abstractmethod
    def hash_features(self, features: Mapping[str, str]) -> str:
        """Return a stable digest for the provided feature mapping."""
