"""Strict static assertions for the ONNX acquisition erasure boundary."""

from __future__ import annotations

from typing_extensions import assert_type

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.model_runtime.model_pool import ModelPool
from async_model_gateway.model_runtime.model_pool._local_model_loader import (  # pyright: ignore[reportPrivateUsage]
    LocalModelLoader,
)
from async_model_gateway.model_runtime.runtime_model import LoadedRuntimeModel


def _onnx_artifact() -> ModelArtifact:
    """Build a statically valid ONNX artifact without exposing a provider type."""
    return ModelArtifact(
        loader_family=LoaderFamily.ONNX,
        artifact_path="models/opaque-runtime",
        loader_options={},
    )


async def check_onnx_acquisition_remains_publicly_erased() -> None:
    """Both public and private acquisition paths retain object erasure."""
    artifact = _onnx_artifact()
    pool_handle = await ModelPool().acquire(artifact)
    loader = LocalModelLoader()  # pyright: ignore[reportPrivateUsage]
    loader_handle = await loader.load(artifact)
    onnx_handle = await loader._load_onnx(artifact)  # pyright: ignore[reportPrivateUsage]

    assert_type(pool_handle, LoadedRuntimeModel[object])
    assert_type(loader_handle, LoadedRuntimeModel[object])
    assert_type(onnx_handle, LoadedRuntimeModel[object])
