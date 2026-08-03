---
topic: response-cache-explicit-key-invalidation
phase: plan-authoring
created: 2026-08-03
---

# response-cache-explicit-key-invalidation — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [ ] code-review

> This topic requires a fresh independent Reviewer-owned `approved` plan-review artifact and fresh Human-owned human-check clearance before Tester may begin RED test authoring. This lookup-decision revision invalidates the existing plan-review verdict for gate purposes; do not alter that JSON here, and require a fresh Reviewer verdict for this exact revision. Tester must create RED evidence before the Implementer modifies production behavior. After all implementation steps are complete, an independent Reviewer must create implementation-review evidence before routing to `pr-comment`. Chat approval does not clear these repo-visible gates.

## Implementation Steps

- [X] 1. In `tests/response_cache/test_cache.py`, `tests/response_cache/test_in_memory_store.py`, and `tests/response_cache/test_response_cache_package_surface.py`, write direct-import RED tests for explicit-key invalidation and four separate private lookup cases: fresh `HIT` preservation of `ResponseCacheEntry | None`; absent `MISS` without policy access; stale-reclaimed `MISS`; and policy exception, cancellation, or unexpected failure propagation rather than `MISS`. Separately verify ordinary direct imports with no dynamic module loading; record the matching `*.red-tests.yaml` evidence before source changes.
- [X] 2. In `src/async_model_gateway/response_cache/ports/store.py`, add the matching abstract keyword-only async `invalidate(...) -> bool` method while retaining submodule-only exposure and existing get/set contracts.
- [X] 3. In `src/async_model_gateway/response_cache/cache.py`, add the one direct-await facade invalidation method with no error handling or additional async behavior.
- [X] 4. In `src/async_model_gateway/response_cache/_in_memory_store.py`, implement fresh/absent/stale explicit-key outcomes and propagation-preserving policy failure behavior.
- [X] 5. In `docs/architecture.md` and `docs/specs/response-cache-boundary.md`, align only the narrow explicit-key invalidation wording and retain all broader exclusions.
- [X] 6. In `src/async_model_gateway/response_cache/_in_memory_store.py`, add the private lookup-only `_CacheLookupDecision(str, Enum)` with `HIT` / `MISS` and `match` mapping while preserving failure propagation and every public boundary.
- [X] 7. After Steps 1-6, run the declared focused/full test, lint, type, and pre-commit commands so the final evidence covers the private lookup-decision implementation and preserved invalidation contract; update this step tracker for completed creator work and leave reviewer/human evidence to their owners.
