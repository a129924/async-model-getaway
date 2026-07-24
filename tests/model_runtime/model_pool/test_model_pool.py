"""RED coverage for internal injected-loader pool acquisition."""

from __future__ import annotations

import asyncio
from typing import cast

import pytest

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.model_runtime.model_pool.loaders._model_loader import ModelLoader
from async_model_gateway.model_runtime.model_pool.pool import ModelPool


class _RecordingLoader(ModelLoader[object]):
    """Return one raw runtime and record every injected pool call."""

    def __init__(self, runtime: object) -> None:
        self.runtime = runtime
        self.artifacts: list[ModelArtifact] = []

    async def load(self, artifact: ModelArtifact) -> object:
        self.artifacts.append(artifact)
        return self.runtime


def _artifact() -> ModelArtifact:
    return ModelArtifact(
        loader_family=LoaderFamily.ONNX,
        artifact_path="models/internal-runtime.onnx",
        loader_options={},
    )


@pytest.mark.asyncio
async def test_pool_wraps_raw_runtime_from_the_injected_loader_with_requested_gate() -> None:
    runtime = object()
    loader = _RecordingLoader(runtime)
    artifact = _artifact()

    loaded = await ModelPool().acquire(artifact, loader=loader, max_concurrency=1)

    assert loader.artifacts == [artifact]
    assert loaded.runtime is runtime
    assert isinstance(loaded.execution_gate, asyncio.Semaphore)
    assert loaded.execution_gate.locked() is False


@pytest.mark.asyncio
async def test_pool_is_uncached_and_does_not_retain_the_injected_loader() -> None:
    loader = _RecordingLoader(object())
    pool = ModelPool()

    first = await pool.acquire(_artifact(), loader=loader, max_concurrency=1)
    second = await pool.acquire(_artifact(), loader=loader, max_concurrency=1)

    assert first is not second
    assert loader.artifacts == [_artifact(), _artifact()]
    assert not hasattr(pool, "_loader")
    assert not hasattr(pool, "_models")
    assert not hasattr(pool, "_binding_resolver")
    assert not hasattr(pool, "_executor")


@pytest.mark.asyncio
async def test_pool_rejects_non_artifact_before_calling_injected_loader() -> None:
    loader = _RecordingLoader(object())

    with pytest.raises(TypeError):
        await ModelPool().acquire(cast(ModelArtifact, object()), loader=loader, max_concurrency=1)

    assert loader.artifacts == []


@pytest.mark.asyncio
async def test_pool_propagates_loader_cancellation_unchanged() -> None:
    cancellation = asyncio.CancelledError("loader cancellation")

    class _CancelledLoader(ModelLoader[object]):
        async def load(self, _artifact: ModelArtifact) -> object:
            raise cancellation

    with pytest.raises(asyncio.CancelledError) as caught:
        await ModelPool().acquire(_artifact(), loader=_CancelledLoader(), max_concurrency=1)

    assert caught.value is cancellation
