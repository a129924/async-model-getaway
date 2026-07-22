"""RED coverage for the abstract LoadedRuntimeModel consumption contract."""

from __future__ import annotations

import inspect
from abc import ABC

import pytest

from async_model_gateway.model_runtime.model_artifact import LoaderFamily, ModelArtifact
from async_model_gateway.model_runtime.runtime_model import LoadedRuntimeModel
from async_model_gateway.model_runtime.runtime_model import (
    loaded_runtime_model as loaded_runtime_model_module,
)


class _TestLoadedRuntimeModel(LoadedRuntimeModel[object]):
    """Keep concrete provider state local to this contract test."""

    __slots__ = ("_loader_family", "_provider_model")

    def __init__(self, *, loader_family: LoaderFamily, provider_model: object) -> None:
        self._loader_family = loader_family
        self._provider_model = provider_model

    @property
    def loader_family(self) -> LoaderFamily:
        return self._loader_family

    def _provider_runtime(self) -> object:
        return self._provider_model


def test_test_local_concrete_handle_preserves_loader_family_provenance() -> None:
    """The abstract contract retains provenance and provider identity for internal use."""
    provider_model = object()
    handle = _TestLoadedRuntimeModel(
        loader_family=LoaderFamily.TORCH,
        provider_model=provider_model,
    )

    assert isinstance(handle, LoadedRuntimeModel)
    assert handle.loader_family is LoaderFamily.TORCH
    assert handle._provider_runtime() is provider_model


def test_loaded_runtime_model_is_abstract_and_rejects_direct_construction() -> None:
    """Package consumers receive an abstract boundary rather than a concrete value object."""
    assert issubclass(LoadedRuntimeModel, ABC)
    assert inspect.isabstract(LoadedRuntimeModel)

    with pytest.raises(TypeError):
        LoadedRuntimeModel()


def test_loaded_runtime_model_has_no_public_payload_or_lifecycle_api() -> None:
    """Provider payload must remain opaque until a separate execution topic defines use."""
    handle = _TestLoadedRuntimeModel(
        loader_family=LoaderFamily.PICKLE,
        provider_model=object(),
    )

    assert {name for name in dir(handle) if not name.startswith("_")} == {"loader_family"}
    assert not hasattr(handle, "provider_model")
    assert not hasattr(handle, "unwrap")
    assert not hasattr(handle, "invoke")
    assert not hasattr(handle, "close")
    assert not hasattr(handle, "unload")
    assert not hasattr(handle, "timeout")
    assert not hasattr(handle, "cache")
    assert not hasattr(handle, "reuse")
    assert not hasattr(handle, "identity")
    assert not hasattr(handle, "serialize")


def test_loaded_runtime_model_rejects_accidental_public_surface_expansion() -> None:
    """The abstract base must not leave an instance dictionary on local handles."""
    handle = _TestLoadedRuntimeModel(
        loader_family=LoaderFamily.ONNX,
        provider_model=object(),
    )

    with pytest.raises(AttributeError):
        handle.provider_model = object()  # type: ignore[attr-defined]


def test_runtime_model_contract_module_defines_no_concrete_local_handle_or_factory() -> None:
    """Concrete local construction belongs to LocalModelLoader, never this module."""
    module_source = inspect.getsource(loaded_runtime_model_module)

    assert "class _LocalLoadedRuntimeModel" not in module_source
    assert "def _create_loaded_runtime_model" not in module_source
    assert not hasattr(loaded_runtime_model_module, "_LocalLoadedRuntimeModel")
    assert not hasattr(loaded_runtime_model_module, "_create_loaded_runtime_model")


def test_loaded_runtime_model_has_a_covariant_generic_runtime_parameter() -> None:
    """The private runtime seam must preserve one covariant provider type."""
    module_source = inspect.getsource(loaded_runtime_model_module)

    assert LoadedRuntimeModel.__parameters__[0].__name__ == "RuntimeT"
    assert LoadedRuntimeModel.__parameters__[0].__covariant__
    assert 'TypeVar("RuntimeT", covariant=True)' in module_source
    assert "Generic[RuntimeT]" in module_source
    assert LoadedRuntimeModel[object]


def test_loaded_runtime_model_private_handoff_has_the_locked_generic_signature() -> None:
    """The abstract contract retains only the typed private provider handoff."""
    abstract_handoff_signature = inspect.signature(LoadedRuntimeModel._provider_runtime)

    assert tuple(abstract_handoff_signature.parameters) == ("self",)
    assert abstract_handoff_signature.return_annotation == "RuntimeT"


def test_shared_read_contracts_remain_non_generic() -> None:
    """Artifact metadata and family vocabulary must not own provider runtime typing."""
    assert not hasattr(ModelArtifact, "__parameters__")
    assert not hasattr(LoaderFamily, "__parameters__")
