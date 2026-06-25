"""RED coverage for registry freshness-policy and result surfaces."""

from __future__ import annotations

from async_model_gateway.model_registry.entry import ModelSourceKind, RegistryEntry
from async_model_gateway.model_registry.freshness_policy import RegistryFreshnessPolicy
from async_model_gateway.model_registry.freshness_result import (
    RegistryFreshnessDecision,
    RegistryFreshnessResult,
)
import inspect


def test_registry_freshness_result_shape_is_locked_to_three_fields() -> None:
    """The result contract should stay limited to decision, entry, and previous hash."""
    assert set(RegistryFreshnessResult.__annotations__) == {
        "decision",
        "entry",
        "previous_payload_hash",
    }


def test_registry_freshness_policy_evaluate_is_sync_only() -> None:
    """The policy surface should remain synchronous inside the async flow."""
    evaluate_signature = inspect.signature(RegistryFreshnessPolicy.evaluate)

    assert not inspect.iscoroutinefunction(RegistryFreshnessPolicy.evaluate)
    assert tuple(evaluate_signature.parameters) == (
        "self",
        "candidate_entry",
        "stored_entry",
    )
    assert evaluate_signature.parameters["candidate_entry"].kind is (
        inspect.Parameter.KEYWORD_ONLY
    )
    assert evaluate_signature.parameters["stored_entry"].kind is inspect.Parameter.KEYWORD_ONLY


def test_registry_freshness_policy_returns_first_seen_for_missing_entry() -> None:
    """A missing stored entry should classify as first-seen."""
    policy = RegistryFreshnessPolicy()
    candidate_entry = RegistryEntry(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        payload_hash="payload-hash-v1",
    )

    result = policy.evaluate(
        candidate_entry=candidate_entry,
        stored_entry=None,
    )

    assert result.decision is RegistryFreshnessDecision.FIRST_SEEN
    assert result.entry is candidate_entry
    assert result.previous_payload_hash is None


def test_registry_freshness_policy_returns_unchanged_for_same_payload_hash() -> None:
    """Equivalent payload hashes should stay unchanged."""
    policy = RegistryFreshnessPolicy()
    stored_entry = RegistryEntry(
        model_name="demo",
        model_source_kind=ModelSourceKind.REMOTE,
        payload_hash="payload-hash-v1",
    )
    candidate_entry = RegistryEntry(
        model_name="demo",
        model_source_kind=ModelSourceKind.REMOTE,
        payload_hash="payload-hash-v1",
    )

    result = policy.evaluate(
        candidate_entry=candidate_entry,
        stored_entry=stored_entry,
    )

    assert result.decision is RegistryFreshnessDecision.UNCHANGED
    assert result.entry is candidate_entry


def test_registry_freshness_policy_returns_changed_with_previous_payload_hash() -> None:
    """Different payload hashes should report changed and carry the old hash."""
    policy = RegistryFreshnessPolicy()
    stored_entry = RegistryEntry(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        payload_hash="payload-hash-v1",
    )
    candidate_entry = RegistryEntry(
        model_name="demo",
        model_source_kind=ModelSourceKind.LOCAL,
        payload_hash="payload-hash-v2",
    )

    result = policy.evaluate(
        candidate_entry=candidate_entry,
        stored_entry=stored_entry,
    )

    assert result.decision is RegistryFreshnessDecision.CHANGED
    assert result.entry is candidate_entry
    assert result.previous_payload_hash == "payload-hash-v1"
