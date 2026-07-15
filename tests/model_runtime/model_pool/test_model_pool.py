"""RED coverage for ModelPool acquisition and private-loader wiring."""

from __future__ import annotations

import asyncio
from typing import cast

import pytest

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.model_runtime.model_pool import ModelPool
from async_model_gateway.model_runtime.model_pool import pool as pool_module
from async_model_gateway.model_runtime.model_pool._local_model_loader import LocalModelLoader
from async_model_gateway.model_runtime.runtime_model import LoadedRuntimeModel
from async_model_gateway.model_runtime.runtime_model.loaded_runtime_model import (
    _create_loaded_runtime_model,
)


def _artifact(loader_family: LoaderFamily) -> ModelArtifact:
    """Build a valid artifact while keeping the route choice explicit."""
    return ModelArtifact(
        loader_family=loader_family,
        artifact_path="models/not-inferred.onnx",
        loader_options={"family": loader_family.value},
    )


@pytest.mark.asyncio
async def test_model_pool_acquire_retains_factory_loader_and_returns_typed_handle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One pool construction must retain one factory-created loader for all acquires."""
    factory_calls: list[None] = []
    loader_calls: list[ModelArtifact] = []
    sentinel = _create_loaded_runtime_model(
        loader_family=LoaderFamily.PICKLE,
        provider_model=object(),
    )
    loader = LocalModelLoader()

    async def load(artifact: ModelArtifact) -> LoadedRuntimeModel:
        loader_calls.append(artifact)
        return sentinel

    def create_loader() -> LocalModelLoader:
        factory_calls.append(None)
        return loader

    monkeypatch.setattr(loader, "load", load)
    monkeypatch.setattr(pool_module, "_create_local_model_loader", create_loader)
    pool = ModelPool()
    first_artifact = _artifact(LoaderFamily.PICKLE)
    second_artifact = _artifact(LoaderFamily.ONNX)

    first_result = await pool.acquire(first_artifact)
    second_result = await pool.acquire(second_artifact)

    assert first_result is sentinel
    assert second_result is sentinel
    assert factory_calls == [None]
    assert loader_calls == [first_artifact, second_artifact]


@pytest.mark.asyncio
async def test_model_pool_acquire_rejects_non_artifact_before_loader_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invalid public input must fail before the retained loader receives a call."""
    loader_calls: list[ModelArtifact] = []
    loader = LocalModelLoader()

    async def load(artifact: ModelArtifact) -> LoadedRuntimeModel:
        loader_calls.append(artifact)
        return _create_loaded_runtime_model(
            loader_family=artifact.loader_family,
            provider_model=object(),
        )

    monkeypatch.setattr(loader, "load", load)
    monkeypatch.setattr(pool_module, "_create_local_model_loader", lambda: loader)
    pool = ModelPool()

    with pytest.raises(TypeError):
        await pool.acquire(cast(ModelArtifact, object()))

    assert loader_calls == []


@pytest.mark.asyncio
async def test_model_pool_acquire_propagates_loader_failure_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A retained loader exception must escape without boundary translation."""
    failure = RuntimeError("loader failed")
    loader = LocalModelLoader()

    async def load(_artifact: ModelArtifact) -> LoadedRuntimeModel:
        raise failure

    monkeypatch.setattr(loader, "load", load)
    monkeypatch.setattr(pool_module, "_create_local_model_loader", lambda: loader)

    with pytest.raises(RuntimeError) as raised:
        await ModelPool().acquire(_artifact(LoaderFamily.TORCH))

    assert raised.value is failure


@pytest.mark.asyncio
async def test_model_pool_acquire_propagates_cancellation_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cancellation must remain owned by the retained loader awaitable."""
    cancellation = asyncio.CancelledError()
    loader = LocalModelLoader()

    async def load(_artifact: ModelArtifact) -> LoadedRuntimeModel:
        raise cancellation

    monkeypatch.setattr(loader, "load", load)
    monkeypatch.setattr(pool_module, "_create_local_model_loader", lambda: loader)

    with pytest.raises(asyncio.CancelledError) as raised:
        await ModelPool().acquire(_artifact(LoaderFamily.ONNX))

    assert raised.value is cancellation
