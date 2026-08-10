"""RED coverage for the compatibility-only feature hashing helpers."""

from __future__ import annotations

import pytest


def test_legacy_feature_hashers_live_only_in_compat_and_factory_warns() -> None:
    """No target cache collaborator recalculates a feature hash."""
    import async_model_gateway.response_cache.compat as compat
    from async_model_gateway.response_cache.key import CacheKey

    assert issubclass(compat.CanonicalFeatureHasher, compat.FeatureHasher)
    with pytest.warns(DeprecationWarning):
        factory = compat.ResponseCacheKeyFactory(compat.CanonicalFeatureHasher())

    key = factory.build(
        namespace="response-cache",
        model_payload_hash="payload",
        features={"mode": "fast"},
    )

    assert isinstance(key, CacheKey)
    assert key.namespace == "response-cache"
    assert key.model_payload_hash == "payload"


def test_legacy_canonical_feature_hasher_uses_predecessor_pair_list_goldens() -> None:
    """The compatibility digest remains order-independent and pair-list canonical."""
    import async_model_gateway.response_cache.compat as compat

    hasher = compat.CanonicalFeatureHasher()

    first_digest = hasher.hash_features({"mode": "chat", "safety": "strict"})
    reversed_digest = hasher.hash_features({"safety": "strict", "mode": "chat"})

    assert first_digest == "1d668737b0884fb29b1ca28c66e6c565e8801bf3a8454a34753e69ecf7cb125d"
    assert reversed_digest == first_digest
    assert hasher.hash_features({}) == (
        "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
    )
    assert hasher.hash_features({"label": "café"}) == (
        "81d3eb80a488458a94e507bf38706ba9aaded47b143f56701a3b36ce7bfd2c05"
    )


@pytest.mark.parametrize("features", [{1: "chat"}, {"mode": 1}, {"mode": ["chat"]}])
def test_legacy_canonical_feature_hasher_fails_closed_for_non_string_pairs(
    features: dict[object, object],
) -> None:
    """The predecessor mapping contract rejects non-string keys and values."""
    import async_model_gateway.response_cache.compat as compat

    with pytest.raises(TypeError):
        compat.CanonicalFeatureHasher().hash_features(features)  # type: ignore[arg-type]


def test_legacy_canonical_feature_hasher_chains_unencodable_unicode() -> None:
    """Strict UTF-8 failure remains a chained TypeError at the compatibility boundary."""
    import async_model_gateway.response_cache.compat as compat

    with pytest.raises(TypeError) as raised_error:
        compat.CanonicalFeatureHasher().hash_features({"mode": "\ud800"})

    assert isinstance(raised_error.value.__cause__, UnicodeEncodeError)


def test_direct_legacy_feature_hasher_routes_are_removed() -> None:
    """Only the documented compatibility module may expose this old helper family."""
    with pytest.raises(ModuleNotFoundError):
        import async_model_gateway.response_cache._canonical_feature_hasher as legacy_hasher  # noqa: F401
    with pytest.raises(ModuleNotFoundError):
        import async_model_gateway.response_cache.ports.feature_hasher as legacy_port  # noqa: F401
