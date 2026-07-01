"""RED coverage for the registry-store package surface."""

from __future__ import annotations

import async_model_gateway.model_registry as model_registry_module
import inspect

from async_model_gateway.model_registry.ports.store import RegistryStore


def test_model_registry_stores_package_reexports_in_memory_store() -> None:
    """The concrete store should be available only from the stores submodule."""
    import async_model_gateway.model_registry.stores as stores_module

    assert stores_module.__all__ == ["InMemoryRegistryStore"]
    assert hasattr(stores_module, "InMemoryRegistryStore")
    assert issubclass(stores_module.InMemoryRegistryStore, RegistryStore)
    assert stores_module.InMemoryRegistryStore.__module__ == (
        "async_model_gateway.model_registry.stores.in_memory"
    )


def test_model_registry_root_package_does_not_reexport_in_memory_store() -> None:
    """The root model_registry package must not leak the concrete store."""
    import async_model_gateway.model_registry.stores as stores_module

    assert not hasattr(model_registry_module, "InMemoryRegistryStore")
    assert inspect.getmodule(stores_module.InMemoryRegistryStore).__name__ == (
        "async_model_gateway.model_registry.stores.in_memory"
    )
