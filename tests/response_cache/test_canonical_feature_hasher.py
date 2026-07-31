"""RED behavior tests for the internal canonical feature hasher."""

from __future__ import annotations

import pytest

import async_model_gateway.response_cache as response_cache_module
import async_model_gateway.response_cache.ports as response_cache_ports_module
from async_model_gateway.response_cache import ResponseCacheKeyFactory
from async_model_gateway.response_cache._canonical_feature_hasher import (
    CanonicalFeatureHasher,
)
from async_model_gateway.response_cache.ports import FeatureHasher


def test_canonical_feature_hasher_implements_port_and_remains_internal() -> None:
    """The concrete hasher is usable internally without expanding public exports."""
    assert isinstance(CanonicalFeatureHasher(), FeatureHasher)
    assert not hasattr(response_cache_module, "CanonicalFeatureHasher")
    assert not hasattr(response_cache_ports_module, "CanonicalFeatureHasher")


def test_hash_features_is_insertion_order_independent() -> None:
    """Equivalent feature collections should share the frozen canonical digest."""
    hasher = CanonicalFeatureHasher()

    first_digest = hasher.hash_features({"mode": "chat", "safety": "strict"})
    reversed_digest = hasher.hash_features({"safety": "strict", "mode": "chat"})

    assert first_digest == "1d668737b0884fb29b1ca28c66e6c565e8801bf3a8454a34753e69ecf7cb125d"
    assert reversed_digest == first_digest
    assert len(first_digest) == 64
    assert first_digest == first_digest.lower()


def test_hash_features_matches_golden_empty_mapping_digest() -> None:
    """An empty mapping must encode as the locked canonical JSON list ``[]``."""
    digest = CanonicalFeatureHasher().hash_features({})

    assert digest == "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"


def test_hash_features_uses_locked_utf8_json_representation_for_unicode() -> None:
    """Non-ASCII values must use raw UTF-8 JSON, rather than ASCII escaping."""
    digest = CanonicalFeatureHasher().hash_features({"label": "café"})

    assert digest == "81d3eb80a488458a94e507bf38706ba9aaded47b143f56701a3b36ce7bfd2c05"


def test_hash_features_accepts_string_subclasses_via_isinstance_validation() -> None:
    """Runtime validation must accept ``str`` subclasses for both identity positions."""

    class FeatureString(str):
        pass

    digest = CanonicalFeatureHasher().hash_features(
        {FeatureString("mode"): FeatureString("chat")},
    )

    assert digest == CanonicalFeatureHasher().hash_features({"mode": "chat"})


def test_hash_features_normalizes_string_subclasses_before_sorting() -> None:
    """String subclasses must not alter canonical ordering through ``__lt__``."""

    class NeverLessThanString(str):
        def __lt__(self, other: object) -> bool:
            return False

    hasher = CanonicalFeatureHasher()
    baseline_digest = hasher.hash_features({"mode": "chat", "safety": "strict"})
    subclass_digest = hasher.hash_features(
        {
            NeverLessThanString("safety"): NeverLessThanString("strict"),
            NeverLessThanString("mode"): NeverLessThanString("chat"),
        },
    )

    assert subclass_digest == baseline_digest


def test_hash_features_distinguishes_representative_key_and_value_changes() -> None:
    """A changed identity key or value must not share the baseline digest."""
    hasher = CanonicalFeatureHasher()
    baseline_digest = hasher.hash_features({"mode": "chat", "safety": "strict"})

    changed_key_digest = hasher.hash_features({"mode": "chat", "guard": "strict"})
    changed_value_digest = hasher.hash_features({"mode": "chat", "safety": "relaxed"})

    assert changed_key_digest != baseline_digest
    assert changed_value_digest != baseline_digest


@pytest.mark.parametrize(
    "changed_features",
    [
        {"mode": " chat"},
        {"mode": "CHAT"},
        {"mode": "café"},
    ],
)
def test_hash_features_preserves_raw_whitespace_case_and_unicode_material(
    changed_features: dict[str, str],
) -> None:
    """Valid raw string differences must not be normalized into one identity."""
    hasher = CanonicalFeatureHasher()

    baseline_digest = hasher.hash_features({"mode": "chat"})

    assert hasher.hash_features(changed_features) != baseline_digest


@pytest.mark.parametrize(
    "invalid_features",
    [
        {1: "chat"},
        {"mode": 1},
    ],
)
def test_hash_features_rejects_non_string_keys_or_values(
    invalid_features: dict[object, object],
) -> None:
    """Invalid identity material must fail closed before any digest is returned."""
    with pytest.raises(TypeError):
        CanonicalFeatureHasher().hash_features(invalid_features)  # type: ignore[arg-type]


def test_factory_uses_concrete_hasher_without_rewriting_identity_material() -> None:
    """Factory injection preserves literal upstream material and caller mapping state."""
    hasher = CanonicalFeatureHasher()
    factory = ResponseCacheKeyFactory(hasher)
    features = {"mode": "chat", "safety": "strict"}

    key = factory.build(
        namespace="  response-cache  ",
        model_payload_hash="  payload-hash  ",
        features=features,
    )

    assert key.namespace == "  response-cache  "
    assert key.model_payload_hash == "  payload-hash  "
    assert key.feature_hash == hasher.hash_features(features)
    assert features == {"mode": "chat", "safety": "strict"}


def test_factory_propagates_concrete_hasher_type_error_without_constructing_a_key() -> None:
    """Factory use must expose the hasher failure instead of returning a fallback key."""
    factory = ResponseCacheKeyFactory(CanonicalFeatureHasher())

    with pytest.raises(TypeError):
        factory.build(
            namespace="response-cache",
            model_payload_hash="payload-hash",
            features={"mode": 1},  # type: ignore[dict-item]
        )
