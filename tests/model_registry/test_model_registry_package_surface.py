"""RED coverage for the model-registry package surface contract."""

from __future__ import annotations

import async_model_gateway.model_registry as model_registry_module
import async_model_gateway.model_registry.entry as entry_module
import async_model_gateway.model_registry.freshness_policy as freshness_policy_module
import async_model_gateway.model_registry.freshness_result as freshness_result_module
import async_model_gateway.model_registry.ports as ports_module
import async_model_gateway.model_registry.ports.store as store_module
import inspect


def test_model_registry_package_reexports_only_model_registry() -> None:
    """The package root should expose only the concrete boundary owner."""
    assert model_registry_module.__all__ == ["ModelRegistry"]
    assert hasattr(model_registry_module, "ModelRegistry")

    for attr_name in (
        "InMemoryRegistryStore",
        "RegistryStore",
        "RegistryEntry",
        "RegistryFreshnessPolicy",
        "RegistryFreshnessResult",
        "ModelPayloadHasher",
    ):
        assert not hasattr(model_registry_module, attr_name)


def test_registry_store_port_stays_under_ports_modules() -> None:
    """The only abstract collaborator must stay within ports/*.py."""
    assert hasattr(ports_module, "RegistryStore")
    assert ports_module.RegistryStore is store_module.RegistryStore
    assert store_module.RegistryStore.__module__ == (
        "async_model_gateway.model_registry.ports.store"
    )


def test_registry_store_lookup_contract_is_async_only_and_ignores_payload_hash() -> None:
    """Lookup identity should stay limited to model_name + model_source_kind."""
    get_entry_signature = inspect.signature(store_module.RegistryStore.get_entry)
    upsert_entry_signature = inspect.signature(store_module.RegistryStore.upsert_entry)

    assert inspect.iscoroutinefunction(store_module.RegistryStore.get_entry)
    assert inspect.iscoroutinefunction(store_module.RegistryStore.upsert_entry)

    assert tuple(get_entry_signature.parameters) == (
        "self",
        "model_name",
        "model_source_kind",
    )
    assert get_entry_signature.parameters["model_name"].kind is inspect.Parameter.KEYWORD_ONLY
    assert get_entry_signature.parameters["model_source_kind"].kind is (
        inspect.Parameter.KEYWORD_ONLY
    )
    assert "payload_hash" not in get_entry_signature.parameters

    assert tuple(upsert_entry_signature.parameters) == ("self", "entry")


def test_registry_supporting_surfaces_stay_in_single_concept_modules() -> None:
    """Each registry concept should live in its own module."""
    assert entry_module.RegistryEntry.__module__ == "async_model_gateway.model_registry.entry"
    assert (
        freshness_policy_module.RegistryFreshnessPolicy.__module__
        == "async_model_gateway.model_registry.freshness_policy"
    )
    assert (
        freshness_result_module.RegistryFreshnessResult.__module__
        == "async_model_gateway.model_registry.freshness_result"
    )
