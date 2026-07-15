"""RED coverage for the minimal ModelPool package surface."""

from __future__ import annotations

import inspect

import async_model_gateway as root_module
import async_model_gateway.model_runtime as model_runtime_root_module
import async_model_gateway.model_runtime.model_pool as model_pool_module
import async_model_gateway.model_runtime.model_pool.pool as pool_module
from async_model_gateway.model_runtime.model_pool import ModelPool
from async_model_gateway.model_runtime.model_pool._local_model_loader import LocalModelLoader


def test_model_pool_package_reexports_only_model_pool() -> None:
    """The local acquisition package must expose only its public owner."""
    assert model_pool_module.__all__ == ["ModelPool"]
    assert model_pool_module.ModelPool is ModelPool
    assert not hasattr(model_pool_module, "LocalModelLoader")


def test_existing_package_roots_do_not_reexport_model_pool() -> None:
    """The new owner must not leak through existing umbrella package roots."""
    assert not hasattr(root_module, "ModelPool")
    assert not hasattr(model_runtime_root_module, "ModelPool")


def test_model_pool_acquire_has_the_locked_async_public_signature() -> None:
    """Acquire must stay the only minimal public local-acquisition method."""
    acquire_signature = inspect.signature(ModelPool.acquire)

    assert inspect.iscoroutinefunction(ModelPool.acquire)
    assert tuple(acquire_signature.parameters) == ("self", "artifact")
    assert acquire_signature.parameters["artifact"].annotation == "ModelArtifact"
    assert acquire_signature.return_annotation == "LoadedRuntimeModel"
    assert tuple(inspect.signature(ModelPool).parameters) == ()
    assert pool_module.ModelPool is ModelPool


def test_private_local_model_loader_has_no_constructor_injection_seam() -> None:
    """The private loader must not retain a replaceable routing constructor input."""
    assert tuple(inspect.signature(LocalModelLoader).parameters) == ()
