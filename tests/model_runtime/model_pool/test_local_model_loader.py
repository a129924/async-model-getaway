"""RED coverage for private LocalModelLoader routing and validation."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import cast

import pytest

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.model_runtime.model_pool._local_model_loader import LocalModelLoader


Route = Callable[[ModelArtifact], Awaitable[object]]


def _artifact(
    loader_family: LoaderFamily,
    *,
    artifact_path: str = "models/runtime-model.bin",
) -> ModelArtifact:
    """Build a valid artifact for an explicitly selected loader family."""
    return ModelArtifact(
        loader_family=loader_family,
        artifact_path=artifact_path,
        loader_options={"source": "test"},
    )


def _complete_route_mapping(
    calls: dict[LoaderFamily, list[ModelArtifact]],
    results: dict[LoaderFamily, object],
) -> dict[LoaderFamily, Route]:
    """Create distinct observable routes for every locked loader family."""
    route_mapping: dict[LoaderFamily, Route] = {}

    for loader_family in LoaderFamily:
        async def route(
            artifact: ModelArtifact,
            *,
            expected_family: LoaderFamily = loader_family,
        ) -> object:
            calls[expected_family].append(artifact)
            return results[expected_family]

        route_mapping[loader_family] = route

    return route_mapping


@pytest.mark.asyncio
@pytest.mark.parametrize("loader_family", list(LoaderFamily))
async def test_local_model_loader_routes_each_family_to_its_own_injected_route(
    loader_family: LoaderFamily,
) -> None:
    """Every locked family must select exactly its explicit mapping route."""
    calls = {family: [] for family in LoaderFamily}
    results = {family: object() for family in LoaderFamily}
    loader = LocalModelLoader(_route_mapping=_complete_route_mapping(calls, results))
    artifact = _artifact(loader_family)

    result = await loader.load(artifact)

    assert result is results[loader_family]
    assert calls[loader_family] == [artifact]
    assert all(calls[family] == [] for family in LoaderFamily if family is not loader_family)


@pytest.mark.asyncio
async def test_local_model_loader_uses_family_not_artifact_path_appearance() -> None:
    """An explicit family must win when the path suggests another serialization type."""
    calls = {family: [] for family in LoaderFamily}
    results = {family: object() for family in LoaderFamily}
    loader = LocalModelLoader(_route_mapping=_complete_route_mapping(calls, results))
    artifact = _artifact(LoaderFamily.PICKLE, artifact_path="models/not-a-pickle.onnx")

    result = await loader.load(artifact)

    assert result is results[LoaderFamily.PICKLE]
    assert calls[LoaderFamily.PICKLE] == [artifact]
    assert calls[LoaderFamily.TORCH] == []
    assert calls[LoaderFamily.ONNX] == []


@pytest.mark.asyncio
@pytest.mark.parametrize("loader_family", list(LoaderFamily))
async def test_local_model_loader_default_routes_fail_closed_without_loading(
    loader_family: LoaderFamily,
) -> None:
    """No default route may claim to load an artifact before I/O is implemented."""
    loader = LocalModelLoader()

    with pytest.raises(NotImplementedError):
        await loader.load(_artifact(loader_family))


def test_local_model_loader_rejects_missing_route_family_before_any_route_await() -> None:
    """A supplied mapping must be complete before a route can be selected."""
    route_calls: list[ModelArtifact] = []

    async def route(artifact: ModelArtifact) -> object:
        route_calls.append(artifact)
        return object()

    incomplete_mapping = dict.fromkeys(LoaderFamily, route)
    del incomplete_mapping[LoaderFamily.ONNX]

    with pytest.raises(ValueError):
        LocalModelLoader(_route_mapping=incomplete_mapping)

    assert route_calls == []


def test_local_model_loader_rejects_extra_or_non_family_route_key() -> None:
    """The test-only mapping seam must reject every key outside LoaderFamily."""
    async def route(_artifact: ModelArtifact) -> object:
        return object()

    invalid_mapping = cast(
        Mapping[LoaderFamily, Route],
        {**dict.fromkeys(LoaderFamily, route), "remote": route},
    )

    with pytest.raises(ValueError):
        LocalModelLoader(_route_mapping=invalid_mapping)


def test_local_model_loader_rejects_non_mapping_route_configuration() -> None:
    """The only test seam must reject configuration that is not a Mapping."""
    invalid_mapping = cast(Mapping[LoaderFamily, Route], object())

    with pytest.raises(TypeError):
        LocalModelLoader(_route_mapping=invalid_mapping)


def test_local_model_loader_rejects_non_callable_route_value() -> None:
    """Every configured family route must be awaitable through a callable value."""
    async def route(_artifact: ModelArtifact) -> object:
        return object()

    invalid_mapping = dict.fromkeys(LoaderFamily, route)
    invalid_mapping[LoaderFamily.TORCH] = cast(Route, object())

    with pytest.raises(TypeError):
        LocalModelLoader(_route_mapping=invalid_mapping)
