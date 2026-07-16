"""Strict static contract checks for runtime-model generic erasure."""

from __future__ import annotations

from typing_extensions import assert_type

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.model_runtime.model_pool import ModelPool
from async_model_gateway.model_runtime.model_pool._local_model_loader import (  # pyright: ignore[reportPrivateUsage]
    LocalModelLoader,
)
from async_model_gateway.model_runtime.runtime_model import LoadedRuntimeModel
from async_model_gateway.model_runtime.runtime_model.loaded_runtime_model import (
    _create_loaded_runtime_model,  # pyright: ignore[reportPrivateUsage]
)


class _ProviderRuntime:
    """Represent one private provider runtime type for static assertions."""


def _artifact() -> ModelArtifact:
    """Create an artifact without giving it a provider runtime parameter."""
    return ModelArtifact(
        loader_family=LoaderFamily.TORCH,
        artifact_path="models/runtime-model.bin",
        loader_options={},
    )


def check_private_factory_precision_and_covariance() -> None:
    """Private construction retains the concrete provider type before public erasure."""
    provider = _ProviderRuntime()
    handle = _create_loaded_runtime_model(  # pyright: ignore[reportPrivateUsage]
        loader_family=LoaderFamily.TORCH,
        provider_model=provider,
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
