"""RED coverage for the private, precisely typed ONNX loader package."""

from __future__ import annotations

import ast
import inspect

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


def _artifact() -> ModelArtifact:
    return ModelArtifact(
        loader_family=LoaderFamily.ONNX,
        artifact_path="models/precise-runtime.onnx",
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


@pytest.mark.asyncio
async def test_onnx_loader_returns_a_runtime_that_satisfies_the_precise_protocol(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeOnnxRuntime:
        def get_providers(self) -> list[str]:
            return ["CPUExecutionProvider"]

    raw_runtime = _FakeOnnxRuntime()

    async def load_onnx_runtime(artifact: ModelArtifact) -> _OnnxRuntime:
        assert artifact.loader_family is LoaderFamily.ONNX
        return raw_runtime

    monkeypatch.setattr(onnx_loader_module, "load_onnx_runtime", load_onnx_runtime)

    actual = await _OnnxModelLoader().load(_artifact())

    assert actual is raw_runtime
    assert actual.get_providers() == ["CPUExecutionProvider"]


def test_onnx_loader_casts_only_the_optional_stub_boundary_to_the_runtime_protocol() -> None:
    source = inspect.getsource(onnx_loader_module)

    assert "asyncio.to_thread" in source
    assert _cast_targets(source) == ["_OnnxRuntime"]


def test_runtime_binding_erases_the_precise_onnx_pairing_only_at_outer_resolution() -> None:
    source = inspect.getsource(binding_module)

    assert _cast_targets(source) == ["RuntimeBinding[object, object, object]"]
