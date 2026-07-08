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


def test_model_artifact_returns_plain_loader_options_dict_copy() -> None:
    """The public loader-options surface must be a standard dict copy."""
    artifact_module = importlib.import_module("async_model_gateway.model_artifact.artifact")
    loader_family_module = importlib.import_module(
        "async_model_gateway.model_artifact.loader_family"
    )

    artifact = artifact_module.ModelArtifact(
        loader_family=loader_family_module.LoaderFamily.TORCH,
        artifact_path="weights/model.pt",
        loader_options={"map_location": "cpu"},
    )

    first_read = artifact.loader_options
    second_read = artifact.loader_options

    assert isinstance(first_read, dict)
    assert first_read.copy() == {"map_location": "cpu"}
    assert first_read == {"map_location": "cpu"}
    assert second_read == {"map_location": "cpu"}
    assert first_read is not second_read


def test_model_artifact_returns_plain_nested_loader_options_containers() -> None:
    """Nested loader-options values must also use standard dict and list containers."""
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

    assert isinstance(session, dict)
    assert isinstance(providers, list)
    assert isinstance(graph_optimization, dict)
    assert isinstance(tensor_names, list)
    assert session.copy() == loader_options["session"]
    assert providers.copy() == ["CPUExecutionProvider"]
    assert tensor_names.copy() == ["input_ids", "attention_mask"]


def test_model_artifact_loader_options_mutation_does_not_affect_artifact_state() -> None:
    """Mutating a returned loader-options snapshot must not mutate the artifact."""
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

    snapshot = artifact.loader_options
    session = cast(dict[str, object], snapshot["session"])
    providers = cast(list[str], session["providers"])
    graph_optimization = cast(dict[str, object], session["graph_optimization"])
    tensor_names = cast(list[str], snapshot["tensor_names"])

    snapshot["device"] = "cuda"
    providers.append("CUDAExecutionProvider")
    graph_optimization["level"] = 1
    tensor_names.append("token_type_ids")

    assert snapshot != loader_options
    assert artifact.loader_options == loader_options


def test_model_artifact_builtin_dict_mutation_only_changes_returned_snapshot() -> None:
    """Built-in dict mutators must not reach the artifact's stored loader options."""
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

    snapshot = artifact.loader_options
    dict.__setitem__(snapshot, "x", 1)

    assert snapshot["x"] == 1
    assert artifact.loader_options == loader_options


def test_model_artifact_builtin_list_mutation_only_changes_returned_snapshot() -> None:
    """Built-in list mutators must not reach nested stored loader options."""
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

    snapshot = artifact.loader_options
    session = cast(dict[str, object], snapshot["session"])
    providers = cast(list[str], session["providers"])

    list.append(providers, "CUDAExecutionProvider")

    assert providers == ["CPUExecutionProvider", "CUDAExecutionProvider"]
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
