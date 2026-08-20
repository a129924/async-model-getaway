---
topic: four-field-cache-key-and-identity-derivers
phase: plan-authoring
created: 2026-08-18
---

# four-field-cache-key-and-identity-derivers — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for
> `python-implementation-review`.
> Update this file at:
> `plan/four-field-cache-key-and-identity-derivers/four-field-cache-key-and-identity-derivers.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [X] 1. Only after fresh plan review and fresh human check, Tester reconfirms or updates RED tests in the declared local-response and response-cache test files plus `tests/local_response/test_identity_derivers.py`, and records fresh RED evidence before an Implementer is assigned. Cover the new field shape, complete-model identity authority, deterministic internal derivation, `FeatureIdentityHasher` non-`str` key/value `TypeError`, invalid identity material ordering, all three fail-open remember outcomes, caller migration, and removed compat imports without dynamic loading.
- [X] 2. Add `src/async_model_gateway/local_response/_identity_derivers.py` with the locked private synchronous derivation responsibilities, including `FeatureIdentityHasher`. Keep the module unexported; make its feature mapping validation fail closed with `TypeError` for non-`str` keys or values; and make its key assembler consume only four already-derived string identities.
- [X] 3. Change `src/async_model_gateway/response_cache/key.py` to the exact four-field frozen/slotted `CacheKey`; migrate every response-cache test helper and assertion while leaving cache/store/invalidation behavior and signatures unchanged.
- [X] 4. Migrate `src/async_model_gateway/local_response/request.py`, `_local_onnx_executor.py`, and `gateway.py`: remove `_CacheKeyDeriver` and constructor injection, validate/derive before the first registry await, read `freshness.entry.model_identity_hash`, and use one invocation snapshot for identity and execution.
- [X] 5. Modify `src/async_model_gateway/response_cache/compat.py` to retain only the legacy entry/error/operation bridge over opaque four-field keys; remove its `ResponseCacheKey`, feature-hasher, and key-factory imports/exports, delete their two dedicated tests, and modify `tests/response_cache/test_response_cache_contract_migration.py` and `tests/response_cache/test_response_cache_package_surface.py` to cover the retained bridge and exactly the compat-retained surface. Do not change `tests/response_cache/test_entry.py`.
- [X] 6. Migrate the local gateway tests, package-surface contract, registry key-shape regression, and public type witness. In `tests/local_response/test_gateway.py`, regress that `Remembered`, `Skipped`, and `Failed` each remain fail-open: after a miss, each returns the generated response without changing execution order. Run the declared validation commands and update the step tracker truthfully for implementation review.
