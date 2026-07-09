"""RED coverage for the bounded loader-family enum contract."""

from __future__ import annotations

import async_model_gateway.model_artifact.loader_family as loader_family_module

import pytest


def test_loader_family_supports_only_the_locked_starter_vocabulary() -> None:
    """The shared read contract must keep a bounded starter vocabulary."""
    assert loader_family_module.LoaderFamily.__module__ == (
        "async_model_gateway.model_artifact.loader_family"
    )
    assert [member.value for member in loader_family_module.LoaderFamily] == [
        "pickle",
        "torch",
        "onnx",
    ]


@pytest.mark.parametrize("invalid_value", ["safetensors", "joblib", "PICKLE", ""])
def test_loader_family_rejects_unknown_explicit_values(invalid_value: str) -> None:
    """Unknown families must fail closed instead of falling back to heuristics."""
    with pytest.raises(ValueError):
        loader_family_module.LoaderFamily(invalid_value)
