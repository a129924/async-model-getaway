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
from async_model_gateway.model_runtime.runtime_model.loaded_runtime_model import (
    _create_loaded_runtime_model,
)


def test_loaded_runtime_model_private_helper_preserves_loader_family_provenance() -> None:
    """The private construction seam must retain typed provenance and provider identity."""
    provider_model = object()
    handle = _create_loaded_runtime_model(
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
    handle = _create_loaded_runtime_model(
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
    handle = _create_loaded_runtime_model(
        loader_family=LoaderFamily.ONNX,
        provider_model=object(),
    )

    with pytest.raises(AttributeError):
        handle.provider_model = object()  # type: ignore[attr-defined]


def test_loaded_runtime_model_private_implementation_uses_ordinary_construction() -> None:
    """The corrected private concrete class must not recreate the rejected immutable design."""
    module_source = inspect.getsource(loaded_runtime_model_module)

    assert "class _LocalLoadedRuntimeModel" in module_source
    assert "def __init__" in module_source
    assert "def __new__" not in module_source
    assert "def __setattr__" not in module_source
    assert "@dataclass(frozen=True" not in module_source


def test_loaded_runtime_model_has_a_covariant_generic_runtime_parameter() -> None:
    """The private runtime seam must preserve one covariant provider type."""
    module_source = inspect.getsource(loaded_runtime_model_module)

    assert LoadedRuntimeModel.__parameters__[0].__name__ == "RuntimeT"
    assert LoadedRuntimeModel.__parameters__[0].__covariant__
    assert 'TypeVar("RuntimeT", covariant=True)' in module_source
    assert "Generic[RuntimeT]" in module_source
    assert LoadedRuntimeModel[object]


def test_loaded_runtime_model_private_helpers_have_the_locked_generic_signatures() -> None:
    """The provider payload can enter only through the typed private factory seam."""
    helper_signature = inspect.signature(_create_loaded_runtime_model)
    abstract_handoff_signature = inspect.signature(LoadedRuntimeModel._provider_runtime)
    local_handoff_signature = inspect.signature(
        loaded_runtime_model_module._LocalLoadedRuntimeModel._provider_runtime,
    )

    assert tuple(helper_signature.parameters) == ("loader_family", "provider_model")
    assert helper_signature.parameters["loader_family"].kind is inspect.Parameter.KEYWORD_ONLY
    assert helper_signature.parameters["loader_family"].annotation == "LoaderFamily"
    assert helper_signature.parameters["provider_model"].kind is inspect.Parameter.KEYWORD_ONLY
    assert helper_signature.parameters["provider_model"].annotation == "RuntimeT"
    assert helper_signature.return_annotation == "LoadedRuntimeModel[RuntimeT]"
    assert abstract_handoff_signature.return_annotation == "RuntimeT"
    assert local_handoff_signature.return_annotation == "RuntimeT"


def test_shared_read_contracts_remain_non_generic() -> None:
    """Artifact metadata and family vocabulary must not own provider runtime typing."""
    assert not hasattr(ModelArtifact, "__parameters__")
    assert not hasattr(LoaderFamily, "__parameters__")
