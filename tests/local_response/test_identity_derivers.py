"""RED coverage for private local response cache-identity derivation."""

from __future__ import annotations

import re

import pytest


def test_private_derivers_canonicalize_order_equivalent_material_without_exports() -> None:
    """Feature and JSON-like input identity are deterministic and opaque."""
    import async_model_gateway.local_response._identity_derivers as identity_derivers

    first_features = {"format": "text", "safety": "strict"}
    second_features = {"safety": "strict", "format": "text"}
    first_input = {"prompt": "hello", "settings": {"top_p": 1.0, "temperature": 0.2}}
    second_input = {"settings": {"temperature": 0.2, "top_p": 1.0}, "prompt": "hello"}

    first_feature_hash = identity_derivers._derive_feature_hash(first_features)
    second_feature_hash = identity_derivers._derive_feature_hash(second_features)
    first_input_hash = identity_derivers._derive_prediction_input_hash(first_input)
    second_input_hash = identity_derivers._derive_prediction_input_hash(second_input)

    assert first_feature_hash == second_feature_hash
    assert first_input_hash == second_input_hash
    assert re.fullmatch(r"[0-9a-f]{64}", first_feature_hash) is not None
    assert re.fullmatch(r"[0-9a-f]{64}", first_input_hash) is not None
    assert "hello" not in first_input_hash
    assert "text" not in first_feature_hash


@pytest.mark.parametrize(
    ("features", "invocation", "invalid_kind"),
    [
        ({"format": "text"}, {"nested": [object()]}, "input"),
        ({"format": "text"}, {1: "not-json-object-key"}, "input"),
    ],
    ids=("nested-input-value", "input-key"),
)
def test_private_derivers_fail_closed_for_invalid_identity_material(
    features: dict[str, object], invocation: dict[object, object], invalid_kind: str
) -> None:
    """Invalid material is rejected rather than normalized or omitted."""
    import async_model_gateway.local_response._identity_derivers as identity_derivers

    if invalid_kind == "feature":
        with pytest.raises(TypeError):
            identity_derivers._derive_feature_hash(features)  # type: ignore[arg-type]
    else:
        with pytest.raises(TypeError):
            identity_derivers._derive_prediction_input_hash(invocation)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "features",
    ({1: "text"}, {"format": object()}),
    ids=("non-string-key", "non-string-value"),
)
def test_feature_identity_hasher_rejects_non_string_feature_keys_and_values(
    features: dict[object, object],
) -> None:
    """Feature identity fails closed for every unsupported mapping key or value."""
    import async_model_gateway.local_response._identity_derivers as identity_derivers

    with pytest.raises(TypeError):
        identity_derivers._derive_feature_hash(features)  # type: ignore[arg-type]


def test_private_key_assembler_only_carries_the_four_supplied_identities() -> None:
    """Assembly is policy-free and cannot leak raw feature or input material."""
    import async_model_gateway.local_response._identity_derivers as identity_derivers

    key = identity_derivers._assemble_cache_key(
        namespace="local-response-v1",
        model_identity_hash="model-identity",
        feature_hash="feature-identity",
        prediction_input_hash="input-identity",
    )

    assert key.namespace == "local-response-v1"
    assert key.model_identity_hash == "model-identity"
    assert key.feature_hash == "feature-identity"
    assert key.prediction_input_hash == "input-identity"


def test_private_namespace_derivation_is_fixed_for_local_response() -> None:
    """The local projection uses one deterministic namespace with no artifact policy."""
    import async_model_gateway.local_response._identity_derivers as identity_derivers

    first = identity_derivers._derive_namespace()
    second = identity_derivers._derive_namespace()

    assert first == second
    assert first
