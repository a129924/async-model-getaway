"""RED coverage for private LocalModelLoader explicit family dispatch."""

from __future__ import annotations

import inspect

import pytest
from typing_extensions import assert_never

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
import async_model_gateway.model_runtime.model_pool._local_model_loader as local_model_loader_module
from async_model_gateway.model_runtime.model_pool._local_model_loader import LocalModelLoader
from async_model_gateway.model_runtime.runtime_model import LoadedRuntimeModel
from async_model_gateway.model_runtime.runtime_model.loaded_runtime_model import (
    _create_loaded_runtime_model,
)


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


def test_local_model_loader_methods_have_the_locked_typed_return_contract() -> None:
    """All local-acquisition routes must return the concrete consumption handle."""
    assert (
        inspect.signature(LocalModelLoader.load).return_annotation
        == "LoadedRuntimeModel[object]"
    )
    assert (
        inspect.signature(LocalModelLoader._load_pickle).return_annotation
        == "LoadedRuntimeModel[object]"
    )
    assert (
        inspect.signature(LocalModelLoader._load_torch).return_annotation
        == "LoadedRuntimeModel[object]"
    )
    assert (
        inspect.signature(LocalModelLoader._load_onnx).return_annotation
        == "LoadedRuntimeModel[object]"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("loader_family", list(LoaderFamily))
async def test_local_model_loader_routes_each_family_to_its_matching_private_handler(
    monkeypatch: pytest.MonkeyPatch,
    loader_family: LoaderFamily,
) -> None:
    """Every family must await only the private handler named for that family."""
    calls = {family: [] for family in LoaderFamily}
    results = {
        family: _create_loaded_runtime_model(
            loader_family=family,
            provider_model=object(),
        )
        for family in LoaderFamily
    }

    async def load_pickle(
        _self: LocalModelLoader,
        artifact: ModelArtifact,
    ) -> LoadedRuntimeModel[object]:
        calls[LoaderFamily.PICKLE].append(artifact)
        return results[LoaderFamily.PICKLE]

    async def load_torch(
        _self: LocalModelLoader,
        artifact: ModelArtifact,
    ) -> LoadedRuntimeModel[object]:
        calls[LoaderFamily.TORCH].append(artifact)
        return results[LoaderFamily.TORCH]

    async def load_onnx(
        _self: LocalModelLoader,
        artifact: ModelArtifact,
    ) -> LoadedRuntimeModel[object]:
        calls[LoaderFamily.ONNX].append(artifact)
        return results[LoaderFamily.ONNX]

    monkeypatch.setattr(LocalModelLoader, "_load_pickle", load_pickle)
    monkeypatch.setattr(LocalModelLoader, "_load_torch", load_torch)
    monkeypatch.setattr(LocalModelLoader, "_load_onnx", load_onnx)
    artifact = _artifact(loader_family)

    result = await LocalModelLoader().load(artifact)

    assert result is results[loader_family]
    assert calls[loader_family] == [artifact]
    assert all(calls[family] == [] for family in LoaderFamily if family is not loader_family)


@pytest.mark.asyncio
async def test_local_model_loader_uses_family_not_artifact_path_appearance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An explicit family must win when the path suggests another format."""
    calls = {family: [] for family in LoaderFamily}
    pickle_result = _create_loaded_runtime_model(
        loader_family=LoaderFamily.PICKLE,
        provider_model=object(),
    )

    async def load_pickle(
        _self: LocalModelLoader,
        artifact: ModelArtifact,
    ) -> LoadedRuntimeModel[object]:
        calls[LoaderFamily.PICKLE].append(artifact)
        return pickle_result

    async def unexpected_handler(
        _self: LocalModelLoader,
        artifact: ModelArtifact,
    ) -> LoadedRuntimeModel[object]:
        calls[artifact.loader_family].append(artifact)
        raise AssertionError("a non-pickle handler must not be selected")

    monkeypatch.setattr(LocalModelLoader, "_load_pickle", load_pickle)
    monkeypatch.setattr(LocalModelLoader, "_load_torch", unexpected_handler)
    monkeypatch.setattr(LocalModelLoader, "_load_onnx", unexpected_handler)
    artifact = _artifact(LoaderFamily.PICKLE, artifact_path="models/not-a-pickle.onnx")

    result = await LocalModelLoader().load(artifact)

    assert result is pickle_result
    assert calls[LoaderFamily.PICKLE] == [artifact]
    assert calls[LoaderFamily.TORCH] == []
    assert calls[LoaderFamily.ONNX] == []


@pytest.mark.asyncio
@pytest.mark.parametrize("loader_family", list(LoaderFamily))
async def test_local_model_loader_default_handlers_fail_closed_without_loading(
    loader_family: LoaderFamily,
) -> None:
    """No default handler may claim to load an artifact before I/O is implemented."""
    with pytest.raises(NotImplementedError):
        await LocalModelLoader().load(_artifact(loader_family))


def test_local_model_loader_uses_typing_extensions_assert_never_for_the_unreachable_case() -> None:
    """The closed-enum fallback must remain the static exhaustiveness contract."""
    module_source = inspect.getsource(local_model_loader_module)
    load_source = inspect.getsource(LocalModelLoader.load)

    assert local_model_loader_module.assert_never is assert_never
    assert "from typing_extensions import assert_never" in module_source
    assert (
        "            case _:\n                assert_never(artifact.loader_family)"
    ) in load_source
