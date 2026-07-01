"""Tests for the class-first canonical model-payload hashing contract."""

from __future__ import annotations

import re

import pytest
import async_model_gateway.model_registry as model_registry_module
import async_model_gateway.model_registry.model_payload as model_payload_module
from async_model_gateway.model_registry.model_payload import ModelPayloadHasher


def test_model_payload_hasher_is_exposed_from_model_payload_public_surface() -> None:
    """The topic-local public package should expose the hashing owner."""
    assert hasattr(model_payload_module, "ModelPayloadHasher")
    assert model_payload_module.ModelPayloadHasher is ModelPayloadHasher


def test_hash_model_payload_function_is_not_exposed_from_model_payload_public_surface() -> None:
    """The old function-first public surface should no longer exist."""
    assert not hasattr(model_payload_module, "hash_model_payload")


def test_model_registry_package_does_not_reexport_model_payload_hasher() -> None:
    """The broader model_registry package must not become a re-export surface."""
    assert not hasattr(model_registry_module, "ModelPayloadHasher")


def test_model_payload_hasher_returns_same_hex_digest_for_equivalent_nested_payloads() -> None:
    """Nested dict insertion order should not affect the payload hash."""
    hasher = ModelPayloadHasher()
    first_payload = {
        "model": {
            "name": "demo",
            "config": {
                "temperature": 0.1,
                "max_tokens": 128,
            },
        },
        "features": ["vision", "tool-call"],
    }
    second_payload = {
        "features": ["vision", "tool-call"],
        "model": {
            "config": {
                "max_tokens": 128,
                "temperature": 0.1,
            },
            "name": "demo",
        },
    }

    first_digest = hasher.hash_model_payload(first_payload)
    second_digest = hasher.hash_model_payload(second_payload)

    assert first_digest == second_digest
    assert re.fullmatch(r"[0-9a-f]{64}", first_digest) is not None


def test_model_payload_hasher_matches_golden_digest_for_empty_payload() -> None:
    """Empty payload hashing should stay cross-process stable."""
    hasher = ModelPayloadHasher()

    digest = hasher.hash_model_payload({})

    assert digest == "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"


def test_model_payload_hasher_treats_empty_nested_containers_as_valid_identity_material() -> None:
    """Empty dict and list values should still hash deterministically."""
    hasher = ModelPayloadHasher()
    payload = {
        "metadata": {},
        "artifacts": [],
    }

    digest = hasher.hash_model_payload(payload)

    assert re.fullmatch(r"[0-9a-f]{64}", digest) is not None


def test_model_payload_hasher_preserves_list_order_in_the_digest() -> None:
    """List order must remain significant for payload identity."""
    hasher = ModelPayloadHasher()
    first_payload = {"steps": ["load", "tokenize", "infer"]}
    second_payload = {"steps": ["infer", "tokenize", "load"]}

    first_digest = hasher.hash_model_payload(first_payload)
    second_digest = hasher.hash_model_payload(second_payload)

    assert first_digest != second_digest


def test_model_payload_hasher_keeps_scalar_representations_distinct() -> None:
    """Scalar values must not be normalized before hashing."""
    hasher = ModelPayloadHasher()

    integer_digest = hasher.hash_model_payload({"value": 1})
    float_digest = hasher.hash_model_payload({"value": 1.0})

    assert integer_digest != float_digest


@pytest.mark.parametrize("invalid_payload", [["x"], ("x",), "x", 1, None])
def test_model_payload_hasher_rejects_invalid_top_level_payload_types(
    invalid_payload: object,
) -> None:
    """Only top-level dict[str, JSONLike] payloads are accepted."""
    hasher = ModelPayloadHasher()

    with pytest.raises(TypeError):
        hasher.hash_model_payload(invalid_payload)  # type: ignore[arg-type]


def test_model_payload_hasher_rejects_nested_dict_keys_that_are_not_strings() -> None:
    """Nested dict keys must stay within the string-only contract."""
    hasher = ModelPayloadHasher()

    with pytest.raises(TypeError):
        hasher.hash_model_payload({"nested": {1: "value"}})  # type: ignore[dict-item]


def test_model_payload_hasher_rejects_unsupported_nested_value_types() -> None:
    """Unsupported runtime values anywhere in the tree must fail closed."""
    hasher = ModelPayloadHasher()

    with pytest.raises(TypeError):
        hasher.hash_model_payload({"nested": [{"value": object()}]})  # type: ignore[list-item]
