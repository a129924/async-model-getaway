"""Strict static contract checks for runtime-model generic erasure."""

from __future__ import annotations

from typing_extensions import assert_type

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.model_runtime.model_pool import ModelPool
from async_model_gateway.model_runtime.model_pool._local_model_loader import (  # pyright: ignore[reportPrivateUsage]
    LocalModelLoader,
)
from async_model_gateway.model_runtime.runtime_model import LoadedRuntimeModel


class _ProviderRuntime:
    """Represent one private provider runtime type for static assertions."""


class _TestLoadedRuntimeModel(LoadedRuntimeModel[_ProviderRuntime]):
    """Provide test-local typed construction without a production factory."""

    def __init__(self, runtime: _ProviderRuntime) -> None:
        self._runtime = runtime

    @property
    def loader_family(self) -> LoaderFamily:
        return LoaderFamily.TORCH

    def _provider_runtime(self) -> _ProviderRuntime:
        return self._runtime


def _as_loaded_runtime_model(
    model: LoadedRuntimeModel[_ProviderRuntime],
) -> LoadedRuntimeModel[_ProviderRuntime]:
    """Preserve the public opaque-handle type for the generic fixture."""
    return model


def _artifact() -> ModelArtifact:
    """Create an artifact without giving it a provider runtime parameter."""
    return ModelArtifact(
        loader_family=LoaderFamily.TORCH,
        artifact_path="models/runtime-model.bin",
        loader_options={},
    )


def check_test_local_handle_precision_and_covariance() -> None:
    """Test-local construction retains a concrete provider type before public erasure."""
    provider = _ProviderRuntime()
    handle: LoadedRuntimeModel[_ProviderRuntime] = _as_loaded_runtime_model(
        _TestLoadedRuntimeModel(provider)
    )

    assert_type(handle, LoadedRuntimeModel[_ProviderRuntime])
    assert_type(
        handle._provider_runtime(),  # pyright: ignore[reportPrivateUsage]
        _ProviderRuntime,
    )


async def check_public_acquisition_erasure() -> None:
    """Pool, loader, and each private handler erase runtime type at acquisition."""
    artifact = _artifact()
    pool_handle = await ModelPool().acquire(artifact)
    loader = LocalModelLoader()  # pyright: ignore[reportPrivateUsage]
    loader_handle = await loader.load(artifact)
    pickle_handle = await loader._load_pickle(artifact)  # pyright: ignore[reportPrivateUsage]
    torch_handle = await loader._load_torch(artifact)  # pyright: ignore[reportPrivateUsage]
    onnx_handle = await loader._load_onnx(artifact)  # pyright: ignore[reportPrivateUsage]

    assert_type(pool_handle, LoadedRuntimeModel[object])
    assert_type(loader_handle, LoadedRuntimeModel[object])
    assert_type(pickle_handle, LoadedRuntimeModel[object])
    assert_type(torch_handle, LoadedRuntimeModel[object])
    assert_type(onnx_handle, LoadedRuntimeModel[object])
