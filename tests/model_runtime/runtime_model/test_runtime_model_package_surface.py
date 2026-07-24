"""RED coverage for the internal runtime-model package boundary."""

from __future__ import annotations

import async_model_gateway as root_module
import async_model_gateway.model_runtime as model_runtime_root_module
import async_model_gateway.model_runtime.runtime_model as runtime_model_module


def test_runtime_model_package_reexports_no_implementation_types() -> None:
    assert runtime_model_module.__all__ == []
    assert not hasattr(runtime_model_module, "LoadedRuntimeModel")
    assert not hasattr(runtime_model_module, "RuntimeT")


def test_package_roots_do_not_reexport_the_internal_loaded_resource() -> None:
    assert not hasattr(root_module, "LoadedRuntimeModel")
    assert not hasattr(model_runtime_root_module, "LoadedRuntimeModel")
