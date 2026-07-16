"""RED coverage for the runtime-model package surface."""

from __future__ import annotations

import async_model_gateway as root_module
import async_model_gateway.model_runtime as model_runtime_root_module
import async_model_gateway.model_runtime.runtime_model as runtime_model_module
from async_model_gateway.model_runtime.runtime_model import LoadedRuntimeModel


def test_runtime_model_package_exports_only_loaded_runtime_model() -> None:
    """The handle package must expose exactly its abstract consumption contract."""
    assert runtime_model_module.__all__ == ["LoadedRuntimeModel"]
    assert runtime_model_module.LoadedRuntimeModel is LoadedRuntimeModel
    assert not hasattr(runtime_model_module, "_create_loaded_runtime_model")
    assert not hasattr(runtime_model_module, "_LocalLoadedRuntimeModel")
    assert not hasattr(runtime_model_module, "RuntimeT")
    assert not hasattr(runtime_model_module, "provider_model")


def test_existing_package_roots_do_not_reexport_loaded_runtime_model() -> None:
    """The abstract handle must not leak through unrelated package roots."""
    assert not hasattr(root_module, "LoadedRuntimeModel")
    assert not hasattr(model_runtime_root_module, "LoadedRuntimeModel")
