"""RED coverage for the abstract LoadedRuntimeModel consumption contract."""

from __future__ import annotations

import inspect
from abc import ABC

import pytest

from async_model_gateway.model_runtime.model_artifact import LoaderFamily
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


def test_loaded_runtime_model_private_implementation_uses_ordinary_construction() -> None:
    """The corrected private concrete class must not recreate the rejected immutable design."""
    module_source = inspect.getsource(loaded_runtime_model_module)

    assert "class _LocalLoadedRuntimeModel" in module_source
    assert "def __init__" in module_source
    assert "def __new__" not in module_source
    assert "def __setattr__" not in module_source
    assert "@dataclass(frozen=True" not in module_source


def test_loaded_runtime_model_does_not_introduce_a_generic_contract() -> None:
    """The bounded consumption handle must not pre-commit provider-type generics."""
    module_source = inspect.getsource(loaded_runtime_model_module)

    assert not hasattr(LoadedRuntimeModel, "__parameters__")
    assert "TypeVar" not in module_source
    assert "Generic[" not in module_source


def test_loaded_runtime_model_private_helper_has_the_locked_internal_signature() -> None:
    """The provider payload can enter only through the typed private factory seam."""
    helper_signature = inspect.signature(_create_loaded_runtime_model)

    assert tuple(helper_signature.parameters) == ("loader_family", "provider_model")
    assert helper_signature.parameters["loader_family"].kind is inspect.Parameter.KEYWORD_ONLY
    assert helper_signature.parameters["loader_family"].annotation == "LoaderFamily"
    assert helper_signature.parameters["provider_model"].kind is inspect.Parameter.KEYWORD_ONLY
    assert helper_signature.parameters["provider_model"].annotation == "object"
    assert helper_signature.return_annotation == "LoadedRuntimeModel"
