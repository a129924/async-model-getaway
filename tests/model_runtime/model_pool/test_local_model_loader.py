"""RED coverage for generic loaders returning raw provider runtimes."""

from __future__ import annotations

import inspect

import pytest

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
import async_model_gateway.model_runtime.model_pool._local_model_loader as loader_module
from async_model_gateway.model_runtime.model_pool._local_model_loader import (
    ModelLoader,
    _OnnxModelLoader,
)


def _artifact(*, loader_options: dict[str, object] | None = None) -> ModelArtifact:
    return ModelArtifact(
        loader_family=LoaderFamily.ONNX,
        artifact_path="models/raw-session.onnx",
        loader_options={} if loader_options is None else loader_options,
    )


def test_model_loader_is_a_nominal_generic_async_boundary() -> None:
    load_signature = inspect.signature(ModelLoader.load)

    assert inspect.isabstract(ModelLoader)
    assert ModelLoader.__parameters__[0].__name__ == "RuntimeT"
    assert inspect.iscoroutinefunction(ModelLoader.load)
    assert tuple(load_signature.parameters) == ("self", "artifact")
    assert load_signature.return_annotation == "RuntimeT"


@pytest.mark.asyncio
async def test_onnx_loader_returns_the_raw_provider_runtime_without_a_wrapper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_runtime = object()

    async def load_onnx_runtime(artifact: ModelArtifact) -> object:
        assert artifact.loader_family is LoaderFamily.ONNX
        return raw_runtime

    monkeypatch.setattr(loader_module, "load_onnx_runtime", load_onnx_runtime)

    actual = await _OnnxModelLoader().load(_artifact())

    assert actual is raw_runtime


@pytest.mark.asyncio
async def test_onnx_loader_preserves_existing_options_error_unchanged() -> None:
    with pytest.raises(ValueError) as caught:
        await _OnnxModelLoader().load(_artifact(loader_options={"providers": []}))

    assert str(caught.value) == "ONNX loader_options are not supported"


def test_loader_module_has_no_family_dispatch_or_loaded_model_wrapper() -> None:
    module_source = inspect.getsource(loader_module)

    assert "class _LocalLoadedRuntimeModel" not in module_source
    assert "match artifact.loader_family" not in module_source
    assert "LoadedRuntimeModel" not in module_source
