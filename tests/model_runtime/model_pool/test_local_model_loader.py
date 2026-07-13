"""RED coverage for private LocalModelLoader explicit family dispatch."""

from __future__ import annotations

import inspect

import pytest
from typing_extensions import assert_never

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
import async_model_gateway.model_runtime.model_pool._local_model_loader as local_model_loader_module
from async_model_gateway.model_runtime.model_pool._local_model_loader import LocalModelLoader


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


def test_local_model_loader_load_keeps_the_exact_deferred_contract_todo() -> None:
    """The deferred runtime-model type must stay documentation-only."""
    source = inspect.getsource(LocalModelLoader.load)

    assert (
        "# TODO: Replace `object` with the agreed runtime-model contract\n"
        "        # (tentatively `LoadedRuntimeModel`) once that boundary is defined."
    ) in source


@pytest.mark.asyncio
@pytest.mark.parametrize("loader_family", list(LoaderFamily))
async def test_local_model_loader_routes_each_family_to_its_matching_private_handler(
    monkeypatch: pytest.MonkeyPatch,
    loader_family: LoaderFamily,
) -> None:
    """Every family must await only the private handler named for that family."""
    calls = {family: [] for family in LoaderFamily}
    results = {family: object() for family in LoaderFamily}

    async def load_pickle(
        _self: LocalModelLoader,
        artifact: ModelArtifact,
    ) -> object:
        calls[LoaderFamily.PICKLE].append(artifact)
        return results[LoaderFamily.PICKLE]

    async def load_torch(
        _self: LocalModelLoader,
        artifact: ModelArtifact,
    ) -> object:
        calls[LoaderFamily.TORCH].append(artifact)
        return results[LoaderFamily.TORCH]

    async def load_onnx(
        _self: LocalModelLoader,
        artifact: ModelArtifact,
    ) -> object:
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
    pickle_result = object()

    async def load_pickle(
        _self: LocalModelLoader,
        artifact: ModelArtifact,
    ) -> object:
        calls[LoaderFamily.PICKLE].append(artifact)
        return pickle_result

    async def unexpected_handler(
        _self: LocalModelLoader,
        artifact: ModelArtifact,
    ) -> object:
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
        "            case _:\n"
        "                assert_never(artifact.loader_family)"
    ) in load_source
