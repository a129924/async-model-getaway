"""RED tests for the canonical model-payload hashing contract."""

from __future__ import annotations

from importlib import import_module
import re

import pytest


def _load_hash_model_payload():
    """Import the bounded public hashing surface for each test."""
    module = import_module("async_model_gateway.model_registry.model_payload")
    return getattr(module, "hash_model_payload")


def test_hash_model_payload_is_exposed_from_model_payload_public_surface() -> None:
    """The topic-local public package should expose the hashing callable."""
    model_payload_module = import_module("async_model_gateway.model_registry.model_payload")

    assert hasattr(model_payload_module, "hash_model_payload")
    assert callable(model_payload_module.hash_model_payload)


def test_model_registry_package_does_not_reexport_hash_model_payload() -> None:
    """The broader model_registry package must not become a re-export surface."""
    model_registry_module = import_module("async_model_gateway.model_registry")

    assert not hasattr(model_registry_module, "hash_model_payload")


def test_hash_model_payload_returns_same_hex_digest_for_equivalent_nested_payloads() -> None:
    """Nested dict insertion order should not affect the payload hash."""
    hash_model_payload = _load_hash_model_payload()
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

    first_digest = hash_model_payload(first_payload)
    second_digest = hash_model_payload(second_payload)

    assert first_digest == second_digest
    assert re.fullmatch(r"[0-9a-f]{64}", first_digest) is not None


def test_hash_model_payload_matches_golden_digest_for_empty_payload() -> None:
    """Empty payload hashing should stay cross-process stable."""
    hash_model_payload = _load_hash_model_payload()

    digest = hash_model_payload({})

    assert digest == "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"


def test_hash_model_payload_treats_empty_nested_containers_as_valid_identity_material() -> None:
    """Empty dict and list values should still hash deterministically."""
    hash_model_payload = _load_hash_model_payload()
    payload = {
        "metadata": {},
        "artifacts": [],
    }

    digest = hash_model_payload(payload)

    assert re.fullmatch(r"[0-9a-f]{64}", digest) is not None


def test_hash_model_payload_preserves_list_order_in_the_digest() -> None:
    """List order must remain significant for payload identity."""
    hash_model_payload = _load_hash_model_payload()
    first_payload = {"steps": ["load", "tokenize", "infer"]}
    second_payload = {"steps": ["infer", "tokenize", "load"]}

    first_digest = hash_model_payload(first_payload)
    second_digest = hash_model_payload(second_payload)

    assert first_digest != second_digest


def test_hash_model_payload_keeps_scalar_representations_distinct() -> None:
    """Scalar values must not be normalized before hashing."""
    hash_model_payload = _load_hash_model_payload()

    integer_digest = hash_model_payload({"value": 1})
    float_digest = hash_model_payload({"value": 1.0})

    assert integer_digest != float_digest


@pytest.mark.parametrize("invalid_payload", [["x"], ("x",), "x", 1, None])
def test_hash_model_payload_rejects_invalid_top_level_payload_types(
    invalid_payload: object,
) -> None:
    """Only top-level dict[str, JSONLike] payloads are accepted."""
    hash_model_payload = _load_hash_model_payload()

    with pytest.raises(TypeError):
        hash_model_payload(invalid_payload)  # type: ignore[arg-type]


def test_hash_model_payload_rejects_nested_dict_keys_that_are_not_strings() -> None:
    """Nested dict keys must stay within the string-only contract."""
    hash_model_payload = _load_hash_model_payload()

    with pytest.raises(TypeError):
        hash_model_payload({"nested": {1: "value"}})  # type: ignore[dict-item]


def test_hash_model_payload_rejects_unsupported_nested_value_types() -> None:
    """Unsupported runtime values anywhere in the tree must fail closed."""
    hash_model_payload = _load_hash_model_payload()

    with pytest.raises(TypeError):
        hash_model_payload({"nested": [{"value": object()}]})  # type: ignore[list-item]
