"""RED coverage for the private, precisely typed ONNX loader package."""

from __future__ import annotations

import ast
import inspect
import shutil
import subprocess
import sys
from pathlib import Path

import onnxruntime
import pytest

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
import async_model_gateway.model_runtime.model_pool.loaders as loaders_package
import async_model_gateway.model_runtime.model_pool.loaders._onnx_model_loader as onnx_loader_module
import async_model_gateway.model_runtime.model_pool._runtime_binding as binding_module
from async_model_gateway.model_runtime.model_pool.loaders._model_loader import ModelLoader
from async_model_gateway.model_runtime.model_pool.loaders._onnx_model_loader import (
    _OnnxModelLoader,
)
from async_model_gateway.model_runtime.runtime_model._onnx_runtime import _OnnxRuntime

_FIXTURES_PATH = Path(__file__).with_name("fixtures")
_GENERATOR_PATH = _FIXTURES_PATH / "build_minimal_identity_model.py"
_MINIMAL_IDENTITY_MODEL_PATH = _FIXTURES_PATH / "minimal_identity.onnx"


def _artifact(path: Path) -> ModelArtifact:
    return ModelArtifact(
        loader_family=LoaderFamily.ONNX,
        artifact_path=str(path),
        loader_options={},
    )


def _cast_targets(source: str) -> list[str]:
    tree = ast.parse(source)
    return [
        ast.unparse(node.args[0])
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "cast"
        and node.args
    ]


def test_loader_package_is_private_and_model_loader_is_split_into_its_own_module() -> None:
    load_signature = inspect.signature(ModelLoader.load)

    assert loaders_package.__all__ == []
    assert inspect.isabstract(ModelLoader)
    assert ModelLoader.__parameters__[0].__name__ == "RuntimeT"
    assert tuple(load_signature.parameters) == ("self", "artifact")
    assert load_signature.return_annotation == "RuntimeT"


def test_onnx_runtime_protocol_declares_only_get_providers() -> None:
    providers_signature = inspect.signature(_OnnxRuntime.get_providers)

    assert {name for name in _OnnxRuntime.__dict__ if not name.startswith("_")} == {"get_providers"}
    assert tuple(providers_signature.parameters) == ("self",)
    assert providers_signature.return_annotation == "list[str]"


def test_committed_identity_model_matches_its_generator() -> None:
    result = subprocess.run(
        [sys.executable, str(_GENERATOR_PATH), "--check"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_identity_model_check_detects_byte_drift_without_rewriting_artifact(
    tmp_path: Path,
) -> None:
    generator_path = tmp_path / _GENERATOR_PATH.name
    model_path = tmp_path / _MINIMAL_IDENTITY_MODEL_PATH.name
    shutil.copy2(_GENERATOR_PATH, generator_path)
    shutil.copy2(_MINIMAL_IDENTITY_MODEL_PATH, model_path)

    drifted_bytes = model_path.read_bytes() + b"\x00"
    model_path.write_bytes(drifted_bytes)

    result = subprocess.run(
        [sys.executable, str(generator_path), "--check"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert model_path.read_bytes() == drifted_bytes


@pytest.mark.asyncio
async def test_onnx_loader_returns_a_real_cpu_only_session_from_committed_asset() -> None:
    session = await _OnnxModelLoader().load(_artifact(_MINIMAL_IDENTITY_MODEL_PATH))

    assert isinstance(session, onnxruntime.InferenceSession)
    assert session.get_providers() == ["CPUExecutionProvider"]


@pytest.mark.asyncio
async def test_onnx_loader_invalid_artifact_failure_originates_from_provider(
    tmp_path: Path,
) -> None:
    invalid_model_path = tmp_path / "invalid-model.onnx"
    invalid_model_path.write_bytes(b"not an ONNX model")

    with pytest.raises(Exception) as raised:
        await _OnnxModelLoader().load(_artifact(invalid_model_path))

    assert type(raised.value).__module__.startswith("onnxruntime.")


def test_onnx_loader_casts_only_the_optional_stub_boundary_to_the_runtime_protocol() -> None:
    source = inspect.getsource(onnx_loader_module)

    assert "asyncio.to_thread" in source
    assert _cast_targets(source) == ["_OnnxRuntime"]


def test_runtime_binding_erases_the_precise_onnx_pairing_only_at_outer_resolution() -> None:
    source = inspect.getsource(binding_module)

    assert _cast_targets(source) == ["RuntimeBinding[object, object, object]"]
