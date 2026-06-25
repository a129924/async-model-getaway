"""Async model-registry boundary owner."""

from __future__ import annotations

from .entry import ModelSourceKind, RegistryEntry
from .freshness_policy import RegistryFreshnessPolicy
from .freshness_result import RegistryFreshnessDecision, RegistryFreshnessResult
from .model_payload.canonical_hash import JSONLike, ModelPayloadHasher
from .ports import RegistryStore

__all__ = ["ModelRegistry"]


class ModelRegistry:
    """Resolve registry freshness for a model identity context."""

    def __init__(
        self,
        store: RegistryStore,
        *,
        freshness_policy: RegistryFreshnessPolicy | None = None,
        payload_hasher: ModelPayloadHasher | None = None,
    ) -> None:
        """Bind the concrete registry owner to its single abstract collaborator."""
        self._store = store
        self._freshness_policy = (
            RegistryFreshnessPolicy()
            if freshness_policy is None
            else freshness_policy
        )
        self._payload_hasher = (
            ModelPayloadHasher() if payload_hasher is None else payload_hasher
        )

    async def resolve_freshness(
        self,
        *,
        model_name: str,
        model_source_kind: ModelSourceKind,
        model_payload: dict[str, JSONLike],
    ) -> RegistryFreshnessResult:
        """Resolve the freshness state for the supplied model identity."""
        stored_entry = await self._store.get_entry(
            model_name=model_name,
            model_source_kind=model_source_kind,
        )
        candidate_entry = RegistryEntry(
            model_name=model_name,
            model_source_kind=model_source_kind,
            payload_hash=self._payload_hasher.hash_model_payload(model_payload),
        )
        result = self._freshness_policy.evaluate(
            candidate_entry=candidate_entry,
            stored_entry=stored_entry,
        )

        if result.decision is not RegistryFreshnessDecision.UNCHANGED:
            await self._store.upsert_entry(result.entry)

        return result
