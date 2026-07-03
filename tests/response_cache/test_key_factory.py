"""Tests for the response-cache key factory."""

from __future__ import annotations

import ast
from collections.abc import Mapping
from pathlib import Path

import pytest

from async_model_gateway.response_cache import ResponseCacheKey, ResponseCacheKeyFactory
from async_model_gateway.response_cache.ports import FeatureHasher


class RecordingFeatureHasher(FeatureHasher):
    """FeatureHasher test double that records delegation inputs."""

    def __init__(self, digest: str) -> None:
        self.digest = digest
        self.calls: list[Mapping[str, str]] = []

    def hash_features(self, features: Mapping[str, str]) -> str:
        """Record the delegated mapping before returning a fixed digest."""
        self.calls.append(features)
        return self.digest


def test_build_returns_response_cache_key_from_explicit_hash_input() -> None:
    """Factory should coordinate explicit payload-hash input and feature hashing."""
    feature_hasher = RecordingFeatureHasher("feature-hash")
    factory = ResponseCacheKeyFactory(feature_hasher)
    features = {"mode": "chat", "safety": "strict"}

    key = factory.build(
        namespace="response-cache",
        model_payload_hash="payload-hash",
        features=features,
    )

    assert key == ResponseCacheKey(
        namespace="response-cache",
        model_payload_hash="payload-hash",
        feature_hash="feature-hash",
    )
    assert feature_hasher.calls == [features]


def test_build_propagates_feature_hash_failures_without_wrapping() -> None:
    """Feature hashing failures should escape unchanged."""

    class FailingFeatureHasher(FeatureHasher):
        def hash_features(self, features: Mapping[str, str]) -> str:
            raise ValueError("feature hash failed")

    factory = ResponseCacheKeyFactory(FailingFeatureHasher())

    with pytest.raises(ValueError, match="feature hash failed"):
        factory.build(
            namespace="response-cache",
            model_payload_hash="payload-hash",
            features={"mode": "chat"},
        )


def test_build_passes_features_mapping_through_without_mutation() -> None:
    """The factory should preserve the input mapping boundary as-is."""
    feature_hasher = RecordingFeatureHasher("feature-hash")
    factory = ResponseCacheKeyFactory(feature_hasher)
    features = {"mode": "chat", "tier": "gold"}

    factory.build(
        namespace="response-cache",
        model_payload_hash="payload-hash",
        features=features,
    )

    assert feature_hasher.calls[0] is features
    assert features == {"mode": "chat", "tier": "gold"}


def test_build_preserves_literal_model_payload_hash_without_normalization() -> None:
    """The factory should treat the payload hash as upstream identity material."""
    feature_hasher = RecordingFeatureHasher("feature-digest")
    factory = ResponseCacheKeyFactory(feature_hasher)

    key = factory.build(
        namespace="response-cache",
        model_payload_hash="  payload-hash  ",
        features={"mode": "chat"},
    )

    assert key.namespace == "response-cache"
    assert key.model_payload_hash == "  payload-hash  "
    assert key.feature_hash == "feature-digest"


def test_key_factory_does_not_import_model_registry_boundary() -> None:
    """The response-cache factory must not import model-registry hash owners."""
    module_path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "async_model_gateway"
        / "response_cache"
        / "key_factory.py"
    )
    module = ast.parse(module_path.read_text(encoding="utf-8"))

    deep_imports = [
        node.module
        for node in ast.walk(module)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    ]

    assert "async_model_gateway.model_registry.model_payload" not in deep_imports
    assert "async_model_gateway.model_registry.model_payload.canonical_hash" not in deep_imports
