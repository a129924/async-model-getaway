"""RED behavior tests for the internal canonical feature hasher."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from unittest.mock import patch

import pytest

import async_model_gateway.response_cache as response_cache_module
import async_model_gateway.response_cache.key_factory as key_factory_module
import async_model_gateway.response_cache.ports as response_cache_ports_module
from async_model_gateway.response_cache import ResponseCacheKeyFactory
from async_model_gateway.response_cache._canonical_feature_hasher import (
    CanonicalFeatureHasher,
)
from async_model_gateway.response_cache.ports import FeatureHasher


class DuplicateBaseKeyFeatures(Mapping[str, str]):
    """Mapping-like test input that can emit duplicate canonical key material."""

    def __init__(self, pairs: list[tuple[str, str]]) -> None:
        self._pairs = pairs

    def __getitem__(self, key: str) -> str:
        for emitted_key, value in self._pairs:
            if emitted_key == key:
                return value
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return (key for key, _ in self._pairs)

    def __len__(self) -> int:
        return len(self._pairs)

    def items(self) -> list[tuple[str, str]]:
        """Return every emitted pair, including duplicate base-string keys."""
        return self._pairs


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


def test_hash_features_uses_base_string_material_for_str_subclasses_with_overridden_str() -> None:
    """Hostile ``__str__`` overrides cannot rewrite or collapse identity material."""

    class HostileFeatureString(str):
        def __str__(self) -> str:
            msg = "Canonical feature hashing must not call subclass __str__."
            raise AssertionError(msg)

    hasher = CanonicalFeatureHasher()
    baseline_digest = hasher.hash_features({"mode": "chat"})
    hostile_digest = hasher.hash_features(
        {HostileFeatureString("mode"): HostileFeatureString("chat")},
    )
    distinct_hostile_digest = hasher.hash_features(
        {HostileFeatureString("mode"): HostileFeatureString("relaxed")},
    )

    assert hostile_digest == baseline_digest
    assert distinct_hostile_digest != baseline_digest


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


def test_hash_features_orders_duplicate_base_keys_by_complete_pair() -> None:
    """Equal base keys with distinct values remain valid and insertion-order independent."""

    class FirstFeatureKey(str):
        pass

    class SecondFeatureKey(str):
        pass

    forward_features = DuplicateBaseKeyFeatures(
        [
            (FirstFeatureKey("mode"), "chat"),
            (SecondFeatureKey("mode"), "completion"),
        ],
    )
    reversed_features = DuplicateBaseKeyFeatures(
        [
            (SecondFeatureKey("mode"), "completion"),
            (FirstFeatureKey("mode"), "chat"),
        ],
    )
    baseline_features = DuplicateBaseKeyFeatures(
        [("mode", "chat"), ("mode", "completion")],
    )
    hasher = CanonicalFeatureHasher()

    forward_digest = hasher.hash_features(forward_features)
    reversed_digest = hasher.hash_features(reversed_features)
    baseline_digest = hasher.hash_features(baseline_features)

    assert forward_digest == reversed_digest == baseline_digest
    assert forward_digest != hasher.hash_features({"mode": "chat"})
    assert forward_digest != hasher.hash_features({"mode": "completion"})


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


def test_hash_features_rejects_unpaired_surrogate_as_chained_type_error() -> None:
    """Canonical material that cannot strictly UTF-8 encode must fail closed."""
    with pytest.raises(TypeError) as raised_error:
        CanonicalFeatureHasher().hash_features({"mode": "\ud800"})

    assert isinstance(raised_error.value.__cause__, UnicodeEncodeError)


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


def test_factory_uses_complete_pair_ordering_for_duplicate_base_keys() -> None:
    """Factory integration keeps duplicate base-key feature hashes deterministic."""

    class FirstFeatureKey(str):
        pass

    class SecondFeatureKey(str):
        pass

    forward_features = DuplicateBaseKeyFeatures(
        [
            (FirstFeatureKey("mode"), "chat"),
            (SecondFeatureKey("mode"), "completion"),
        ],
    )
    reversed_features = DuplicateBaseKeyFeatures(
        [
            (SecondFeatureKey("mode"), "completion"),
            (FirstFeatureKey("mode"), "chat"),
        ],
    )
    baseline_features = DuplicateBaseKeyFeatures(
        [("mode", "chat"), ("mode", "completion")],
    )
    factory = ResponseCacheKeyFactory(CanonicalFeatureHasher())

    forward_key = factory.build(
        namespace="response-cache",
        model_payload_hash="payload-hash",
        features=forward_features,
    )
    reversed_key = factory.build(
        namespace="response-cache",
        model_payload_hash="payload-hash",
        features=reversed_features,
    )
    baseline_key = factory.build(
        namespace="response-cache",
        model_payload_hash="payload-hash",
        features=baseline_features,
    )

    assert forward_key.feature_hash == reversed_key.feature_hash == baseline_key.feature_hash


def test_factory_propagates_concrete_hasher_type_error_without_constructing_a_key() -> None:
    """Factory use must expose the hasher failure instead of returning a fallback key."""
    factory = ResponseCacheKeyFactory(CanonicalFeatureHasher())

    with pytest.raises(TypeError):
        factory.build(
            namespace="response-cache",
            model_payload_hash="payload-hash",
            features={"mode": 1},  # type: ignore[dict-item]
        )


def test_factory_propagates_unpaired_surrogate_type_error_without_constructing_a_key() -> None:
    """Factory propagation must retain the concrete hasher's chained error policy."""
    factory = ResponseCacheKeyFactory(CanonicalFeatureHasher())

    with patch.object(key_factory_module, "ResponseCacheKey") as response_cache_key:
        with pytest.raises(TypeError) as raised_error:
            factory.build(
                namespace="response-cache",
                model_payload_hash="payload-hash",
                features={"mode": "\ud800"},
            )

    assert isinstance(raised_error.value.__cause__, UnicodeEncodeError)
    response_cache_key.assert_not_called()
