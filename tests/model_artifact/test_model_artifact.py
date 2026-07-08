"""RED coverage for the minimal model-artifact shared read contract."""

from __future__ import annotations

import importlib
import inspect
from typing import cast

import pytest


def test_model_artifact_accepts_only_the_locked_minimal_fields() -> None:
    """The shared read contract must stay limited to three explicit fields."""
    artifact_module = importlib.import_module("async_model_gateway.model_artifact.artifact")

    artifact_signature = inspect.signature(artifact_module.ModelArtifact)

    assert tuple(artifact_signature.parameters) == (
        "loader_family",
        "artifact_path",
        "loader_options",
    )
    assert str(artifact_signature.parameters["loader_family"].annotation) == "LoaderFamily"
    assert str(artifact_signature.parameters["artifact_path"].annotation) == "str"
    assert str(artifact_signature.parameters["loader_options"].annotation) == (
        "dict[str, JSONLike]"
    )


def test_model_artifact_preserves_explicit_loader_family_without_path_inference() -> None:
    """The explicit family must win even if the path suffix suggests another loader."""
    artifact_module = importlib.import_module("async_model_gateway.model_artifact.artifact")
    loader_family_module = importlib.import_module(
        "async_model_gateway.model_artifact.loader_family"
    )

    artifact = artifact_module.ModelArtifact(
        loader_family=loader_family_module.LoaderFamily.PICKLE,
        artifact_path="weights/model.onnx",
        loader_options={"map_location": "cpu"},
    )

    assert artifact.loader_family is loader_family_module.LoaderFamily.PICKLE
    assert artifact.artifact_path == "weights/model.onnx"
    assert artifact.loader_options == {"map_location": "cpu"}


def test_model_artifact_accepts_empty_loader_options_dict() -> None:
    """An explicit empty metadata bag remains a valid shared read contract value."""
    artifact_module = importlib.import_module("async_model_gateway.model_artifact.artifact")
    loader_family_module = importlib.import_module(
        "async_model_gateway.model_artifact.loader_family"
    )

    artifact = artifact_module.ModelArtifact(
        loader_family=loader_family_module.LoaderFamily.TORCH,
        artifact_path="weights/model.pt",
        loader_options={},
    )

    assert artifact.loader_options == {}


def test_model_artifact_accepts_nested_json_like_loader_options() -> None:
    """Nested JSON-like metadata remains valid when explicitly supplied."""
    artifact_module = importlib.import_module("async_model_gateway.model_artifact.artifact")
    loader_family_module = importlib.import_module(
        "async_model_gateway.model_artifact.loader_family"
    )

    loader_options = {
        "session": {
            "providers": ["CPUExecutionProvider"],
            "graph_optimization": {"level": 3, "disabled": False},
        },
        "tensor_names": ["input_ids", "attention_mask"],
        "revision": None,
    }

    artifact = artifact_module.ModelArtifact(
        loader_family=loader_family_module.LoaderFamily.ONNX,
        artifact_path="weights/model.onnx",
        loader_options=loader_options,
    )

    assert artifact.loader_options == loader_options


def test_model_artifact_rejects_top_level_loader_options_mutation() -> None:
    """The shared read contract must reject direct top-level loader-options edits."""
    artifact_module = importlib.import_module("async_model_gateway.model_artifact.artifact")
    loader_family_module = importlib.import_module(
        "async_model_gateway.model_artifact.loader_family"
    )

    artifact = artifact_module.ModelArtifact(
        loader_family=loader_family_module.LoaderFamily.TORCH,
        artifact_path="weights/model.pt",
        loader_options={"map_location": "cpu"},
    )

    with pytest.raises(TypeError, match="loader_options is immutable"):
        artifact.loader_options["device"] = "cuda"

    with pytest.raises(TypeError, match="loader_options is immutable"):
        artifact.loader_options["map_location"] = "cuda"

    assert artifact.loader_options == {"map_location": "cpu"}


def test_model_artifact_rejects_nested_loader_options_mutation() -> None:
    """Nested JSON-like loader metadata must stay immutable after construction."""
    artifact_module = importlib.import_module("async_model_gateway.model_artifact.artifact")
    loader_family_module = importlib.import_module(
        "async_model_gateway.model_artifact.loader_family"
    )

    loader_options = {
        "session": {
            "providers": ["CPUExecutionProvider"],
            "graph_optimization": {"level": 3, "disabled": False},
        },
        "tensor_names": ["input_ids", "attention_mask"],
    }

    artifact = artifact_module.ModelArtifact(
        loader_family=loader_family_module.LoaderFamily.ONNX,
        artifact_path="weights/model.onnx",
        loader_options=loader_options,
    )

    session = cast(dict[str, object], artifact.loader_options["session"])
    providers = cast(list[str], session["providers"])
    graph_optimization = cast(dict[str, object], session["graph_optimization"])
    tensor_names = cast(list[str], artifact.loader_options["tensor_names"])

    with pytest.raises(TypeError, match="loader_options is immutable"):
        providers.append("CUDAExecutionProvider")

    with pytest.raises(TypeError, match="loader_options is immutable"):
        graph_optimization["level"] = 1

    with pytest.raises(TypeError, match="loader_options is immutable"):
        tensor_names.append("token_type_ids")

    assert artifact.loader_options == loader_options


def test_model_artifact_rejects_builtin_dict_bypass_for_loader_options() -> None:
    """dict base mutators must not be able to bypass loader-options immutability."""
    artifact_module = importlib.import_module("async_model_gateway.model_artifact.artifact")
    loader_family_module = importlib.import_module(
        "async_model_gateway.model_artifact.loader_family"
    )

    loader_options = {
        "session": {"providers": ["CPUExecutionProvider"]},
        "revision": None,
    }

    artifact = artifact_module.ModelArtifact(
        loader_family=loader_family_module.LoaderFamily.ONNX,
        artifact_path="weights/model.onnx",
        loader_options=loader_options,
    )

    with pytest.raises(TypeError):
        dict.__setitem__(artifact.loader_options, "x", 1)

    assert artifact.loader_options == loader_options


def test_model_artifact_rejects_builtin_list_bypass_for_nested_loader_options() -> None:
    """list base mutators must not be able to bypass nested immutability."""
    artifact_module = importlib.import_module("async_model_gateway.model_artifact.artifact")
    loader_family_module = importlib.import_module(
        "async_model_gateway.model_artifact.loader_family"
    )

    loader_options = {
        "session": {"providers": ["CPUExecutionProvider"]},
        "revision": None,
    }

    artifact = artifact_module.ModelArtifact(
        loader_family=loader_family_module.LoaderFamily.ONNX,
        artifact_path="weights/model.onnx",
        loader_options=loader_options,
    )

    session = cast(dict[str, object], artifact.loader_options["session"])
    providers = cast(list[str], session["providers"])

    with pytest.raises(TypeError):
        list.append(providers, "CUDAExecutionProvider")

    assert artifact.loader_options == loader_options


@pytest.mark.parametrize("blank_path", ["", "   "])
def test_model_artifact_rejects_blank_artifact_path(blank_path: str) -> None:
    """Artifact location must be explicit and non-blank."""
    artifact_module = importlib.import_module("async_model_gateway.model_artifact.artifact")
    loader_family_module = importlib.import_module(
        "async_model_gateway.model_artifact.loader_family"
    )

    with pytest.raises(ValueError):
        artifact_module.ModelArtifact(
            loader_family=loader_family_module.LoaderFamily.TORCH,
            artifact_path=blank_path,
            loader_options={},
        )


def test_model_artifact_rejects_non_json_like_loader_options() -> None:
    """Loader options must stay within a JSON-like metadata boundary."""
    artifact_module = importlib.import_module("async_model_gateway.model_artifact.artifact")
    loader_family_module = importlib.import_module(
        "async_model_gateway.model_artifact.loader_family"
    )

    with pytest.raises(TypeError):
        artifact_module.ModelArtifact(
            loader_family=loader_family_module.LoaderFamily.ONNX,
            artifact_path="weights/model.onnx",
            loader_options={"session": object()},
        )


def test_model_artifact_rejects_non_enum_loader_family() -> None:
    """Explicit loader family must be provided through the bounded enum."""
    artifact_module = importlib.import_module("async_model_gateway.model_artifact.artifact")

    with pytest.raises(TypeError):
        artifact_module.ModelArtifact(
            loader_family="pickle",
            artifact_path="weights/model.pkl",
            loader_options={},
        )


def test_model_artifact_does_not_accept_identity_material_fields() -> None:
    """The shared read contract must stay separate from model identity material."""
    artifact_module = importlib.import_module("async_model_gateway.model_artifact.artifact")
    loader_family_module = importlib.import_module(
        "async_model_gateway.model_artifact.loader_family"
    )

    with pytest.raises(TypeError):
        artifact_module.ModelArtifact(
            loader_family=loader_family_module.LoaderFamily.PICKLE,
            artifact_path="weights/model.pkl",
            loader_options={},
            model_payload={"name": "demo"},
        )
