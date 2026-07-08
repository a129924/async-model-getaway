"""RED coverage for the minimal model-artifact shared read contract."""

from __future__ import annotations

from dataclasses import asdict, replace
import inspect
import async_model_gateway.model_artifact.artifact as artifact_module
import async_model_gateway.model_artifact.loader_family as loader_family_module
from typing import cast

import pytest


def test_model_artifact_accepts_only_the_locked_minimal_fields() -> None:
    """The shared read contract must stay limited to three explicit fields."""
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
    artifact = artifact_module.ModelArtifact(
        loader_family=loader_family_module.LoaderFamily.TORCH,
        artifact_path="weights/model.pt",
        loader_options={},
    )

    assert artifact.loader_options == {}


def test_model_artifact_accepts_nested_json_like_loader_options() -> None:
    """Nested JSON-like metadata remains valid when explicitly supplied."""
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


def test_model_artifact_asdict_uses_public_loader_options_contract() -> None:
    """dataclasses.asdict must not expose private frozen loader-options storage."""
    loader_options = {
        "session": {"providers": ["CPUExecutionProvider"]},
        "revision": None,
    }
    artifact = artifact_module.ModelArtifact(
        loader_family=loader_family_module.LoaderFamily.ONNX,
        artifact_path="weights/model.onnx",
        loader_options=loader_options,
    )

    assert asdict(artifact) == {
        "loader_family": loader_family_module.LoaderFamily.ONNX,
        "artifact_path": "weights/model.onnx",
        "loader_options": loader_options,
    }


def test_model_artifact_replace_reuses_public_loader_options_contract() -> None:
    """dataclasses.replace must rebuild through public loader_options only."""
    loader_options = {
        "session": {"providers": ["CPUExecutionProvider"]},
        "revision": None,
    }
    artifact = artifact_module.ModelArtifact(
        loader_family=loader_family_module.LoaderFamily.ONNX,
        artifact_path="weights/model.onnx",
        loader_options=loader_options,
    )

    replaced_artifact = replace(artifact, artifact_path="weights/model-v2.onnx")

    assert replaced_artifact is not artifact
    assert replaced_artifact.loader_family is loader_family_module.LoaderFamily.ONNX
    assert replaced_artifact.artifact_path == "weights/model-v2.onnx"
    assert replaced_artifact.loader_options == loader_options


@pytest.mark.parametrize("blank_path", ["", "   "])
def test_model_artifact_rejects_blank_artifact_path(blank_path: str) -> None:
    """Artifact location must be explicit and non-blank."""
    with pytest.raises(ValueError):
        artifact_module.ModelArtifact(
            loader_family=loader_family_module.LoaderFamily.TORCH,
            artifact_path=blank_path,
            loader_options={},
        )


def test_model_artifact_rejects_non_json_like_loader_options() -> None:
    """Loader options must stay within a JSON-like metadata boundary."""
    with pytest.raises(TypeError):
        artifact_module.ModelArtifact(
            loader_family=loader_family_module.LoaderFamily.ONNX,
            artifact_path="weights/model.onnx",
            loader_options={"session": object()},
        )


def test_model_artifact_rejects_non_enum_loader_family() -> None:
    """Explicit loader family must be provided through the bounded enum."""
    with pytest.raises(TypeError):
        artifact_module.ModelArtifact(
            loader_family="pickle",
            artifact_path="weights/model.pkl",
            loader_options={},
        )


def test_model_artifact_does_not_accept_identity_material_fields() -> None:
    """The shared read contract must stay separate from model identity material."""
    with pytest.raises(TypeError):
        artifact_module.ModelArtifact(
            loader_family=loader_family_module.LoaderFamily.PICKLE,
            artifact_path="weights/model.pkl",
            loader_options={},
            model_payload={"name": "demo"},
        )


@pytest.mark.parametrize(
    ("operation_name", "run_operation"),
    [
        ("setattr", lambda frozen_list: setattr(frozen_list, "x", 1)),
        ("delattr", lambda frozen_list: delattr(frozen_list, "_values")),
        ("add", lambda frozen_list: frozen_list.__add__([])),
        ("radd", lambda frozen_list: frozen_list.__radd__([])),
        ("delitem", lambda frozen_list: frozen_list.__delitem__(0)),
        ("iadd", lambda frozen_list: frozen_list.__iadd__(["x"])),
        ("imul", lambda frozen_list: frozen_list.__imul__(2)),
        ("setitem", lambda frozen_list: frozen_list.__setitem__(0, "x")),
        ("append", lambda frozen_list: frozen_list.append("x")),
        ("clear", lambda frozen_list: frozen_list.clear()),
        ("extend", lambda frozen_list: frozen_list.extend(["x"])),
        ("insert", lambda frozen_list: frozen_list.insert(0, "x")),
        ("pop", lambda frozen_list: frozen_list.pop()),
        ("remove", lambda frozen_list: frozen_list.remove("cpu")),
        ("reverse", lambda frozen_list: frozen_list.reverse()),
        ("sort", lambda frozen_list: frozen_list.sort()),
    ],
)
def test_frozen_json_list_rejects_all_mutation_entrypoints(
    operation_name: str,
    run_operation,
) -> None:
    """Every exposed list mutation entrypoint must fail closed."""
    frozen_list = artifact_module._normalize_json_like(
        ["cpu", {"providers": ["CPUExecutionProvider"]}]
    )

    assert frozen_list[0] == "cpu"
    assert frozen_list[1:] == ({"providers": ["CPUExecutionProvider"]},)
    assert len(frozen_list) == 2
    assert repr(frozen_list) == "['cpu', {'providers': ['CPUExecutionProvider']}]"
    assert frozen_list == ["cpu", {"providers": ["CPUExecutionProvider"]}]

    with pytest.raises(TypeError, match="loader_options is immutable"):
        run_operation(frozen_list)

    assert operation_name


@pytest.mark.parametrize(
    ("operation_name", "run_operation"),
    [
        ("setattr", lambda frozen_dict: setattr(frozen_dict, "x", 1)),
        ("delattr", lambda frozen_dict: delattr(frozen_dict, "_values")),
        ("delitem", lambda frozen_dict: frozen_dict.__delitem__("providers")),
        ("ior", lambda frozen_dict: frozen_dict.__ior__({"extra": True})),
        ("setitem", lambda frozen_dict: frozen_dict.__setitem__("extra", True)),
        ("clear", lambda frozen_dict: frozen_dict.clear()),
        ("pop", lambda frozen_dict: frozen_dict.pop("providers")),
        ("popitem", lambda frozen_dict: frozen_dict.popitem()),
        ("setdefault", lambda frozen_dict: frozen_dict.setdefault("extra", True)),
        ("update", lambda frozen_dict: frozen_dict.update({"extra": True})),
    ],
)
def test_frozen_json_dict_rejects_all_mutation_entrypoints(
    operation_name: str,
    run_operation,
) -> None:
    """Every exposed dict mutation entrypoint must fail closed."""
    frozen_dict = artifact_module._normalize_json_like(
        {"providers": ["CPUExecutionProvider"], "revision": None}
    )

    assert frozen_dict["providers"] == ["CPUExecutionProvider"]
    assert tuple(frozen_dict) == ("providers", "revision")
    assert len(frozen_dict) == 2
    assert repr(frozen_dict) == "{'providers': ['CPUExecutionProvider'], 'revision': None}"
    assert frozen_dict == {"providers": ["CPUExecutionProvider"], "revision": None}

    with pytest.raises(TypeError, match="loader_options is immutable"):
        run_operation(frozen_dict)

    assert operation_name


def test_model_artifact_rejects_non_string_loader_options_dict_keys() -> None:
    """Nested loader-option dict keys must remain explicit strings."""
    with pytest.raises(TypeError, match="loader_options dict keys must be strings"):
        artifact_module.ModelArtifact(
            loader_family=loader_family_module.LoaderFamily.ONNX,
            artifact_path="weights/model.onnx",
            loader_options={"session": {1: "cpu"}},
        )


def test_model_artifact_rejects_non_dict_loader_options_boundary() -> None:
    """Top-level loader options must remain a dict boundary."""
    with pytest.raises(TypeError, match="loader_options must be a dict\\[str, JSONLike\\]"):
        artifact_module.ModelArtifact(
            loader_family=loader_family_module.LoaderFamily.ONNX,
            artifact_path="weights/model.onnx",
            loader_options=[],
        )


def test_model_artifact_rejects_non_string_artifact_path() -> None:
    """Artifact path must stay within the explicit string boundary."""
    with pytest.raises(TypeError, match="artifact_path must be a string"):
        artifact_module.ModelArtifact(
            loader_family=loader_family_module.LoaderFamily.ONNX,
            artifact_path=1,
            loader_options={},
        )
