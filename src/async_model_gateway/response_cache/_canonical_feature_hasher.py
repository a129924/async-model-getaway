"""Internal canonical hashing for response-cache feature identity."""

from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
import json
from typing import TypeGuard

from .ports import FeatureHasher


def _is_feature_string(value: object) -> TypeGuard[str]:
    """Return whether runtime feature identity material is a string."""
    return isinstance(value, str)


class CanonicalFeatureHasher(FeatureHasher):
    """Derive a deterministic digest from response-cache feature material."""

    def hash_features(self, features: Mapping[str, str]) -> str:
        """Return the locked canonical SHA-256 digest for ``features``."""
        pairs: list[tuple[str, str]] = []
        for key, value in features.items():
            if not _is_feature_string(key):
                msg = "feature keys must be strings"
                raise TypeError(msg)
            if not _is_feature_string(value):
                msg = "feature values must be strings"
                raise TypeError(msg)
            pairs.append((key, value))

        pairs.sort(key=lambda pair: pair[0])
        serialized_pairs = json.dumps(
            pairs,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return sha256(serialized_pairs.encode("utf-8")).hexdigest()
