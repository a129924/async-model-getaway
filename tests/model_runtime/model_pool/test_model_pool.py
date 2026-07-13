"""RED coverage for ModelPool acquisition and private-loader wiring."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import cast

import pytest

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.model_runtime.model_pool import ModelPool
from async_model_gateway.model_runtime.model_pool._local_model_loader import LocalModelLoader


Route = Callable[[ModelArtifact], Awaitable[object]]


def _artifact(loader_family: LoaderFamily) -> ModelArtifact:
    """Build a valid artifact while keeping the route choice explicit."""
    return ModelArtifact(
        loader_family=loader_family,
        artifact_path="models/not-inferred.onnx",
        loader_options={"family": loader_family.value},
    )


def _route_mapping(
    calls: list[ModelArtifact],
    result: object,
) -> dict[LoaderFamily, Route]:
    """Create complete routes that prove the exact artifact reaches a loader."""
    async def route(artifact: ModelArtifact) -> object:
        calls.append(artifact)
        return result

    return dict.fromkeys(LoaderFamily, route)


@pytest.mark.asyncio
async def test_model_pool_acquire_retains_factory_loader_and_returns_route_object(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One pool construction must retain one factory-created loader for all acquires."""
    factory_calls: list[None] = []
    route_calls: list[ModelArtifact] = []
    sentinel = object()
    loader = LocalModelLoader(_route_mapping=_route_mapping(route_calls, sentinel))

    def create_loader() -> LocalModelLoader:
        factory_calls.append(None)
        return loader

    monkeypatch.setattr(
        "async_model_gateway.model_runtime.model_pool.pool._create_local_model_loader",
        create_loader,
    )
    pool = ModelPool()
    first_artifact = _artifact(LoaderFamily.PICKLE)
    second_artifact = _artifact(LoaderFamily.ONNX)

    first_result = await pool.acquire(first_artifact)
    second_result = await pool.acquire(second_artifact)

    assert first_result is sentinel
    assert second_result is sentinel
    assert factory_calls == [None]
    assert route_calls == [first_artifact, second_artifact]


@pytest.mark.asyncio
async def test_model_pool_acquire_rejects_non_artifact_before_loader_route(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invalid public input must fail before the retained loader receives a route call."""
    route_calls: list[ModelArtifact] = []
    loader = LocalModelLoader(_route_mapping=_route_mapping(route_calls, object()))

    monkeypatch.setattr(
        "async_model_gateway.model_runtime.model_pool.pool._create_local_model_loader",
        lambda: loader,
    )
    pool = ModelPool()

    with pytest.raises(TypeError):
        await pool.acquire(cast(ModelArtifact, object()))

    assert route_calls == []


@pytest.mark.asyncio
async def test_model_pool_acquire_propagates_route_failure_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A selected route exception must escape without boundary translation."""
    failure = RuntimeError("route failed")

    async def failing_route(_artifact: ModelArtifact) -> object:
        raise failure

    loader = LocalModelLoader(
        _route_mapping=dict.fromkeys(LoaderFamily, failing_route),
    )
    monkeypatch.setattr(
        "async_model_gateway.model_runtime.model_pool.pool._create_local_model_loader",
        lambda: loader,
    )

    with pytest.raises(RuntimeError) as raised:
        await ModelPool().acquire(_artifact(LoaderFamily.TORCH))

    assert raised.value is failure


@pytest.mark.asyncio
async def test_model_pool_acquire_propagates_cancellation_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cancellation must remain owned by the selected route awaitable."""
    cancellation = asyncio.CancelledError()

    async def cancelling_route(_artifact: ModelArtifact) -> object:
        raise cancellation

    loader = LocalModelLoader(
        _route_mapping=dict.fromkeys(LoaderFamily, cancelling_route),
    )
    monkeypatch.setattr(
        "async_model_gateway.model_runtime.model_pool.pool._create_local_model_loader",
        lambda: loader,
    )

    with pytest.raises(asyncio.CancelledError) as raised:
        await ModelPool().acquire(_artifact(LoaderFamily.ONNX))

    assert raised.value is cancellation
