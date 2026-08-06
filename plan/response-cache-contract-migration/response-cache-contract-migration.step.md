---
topic: response-cache-contract-migration
phase: implementation
created: 2026-08-06
---

# response-cache-contract-migration — Step Tracking

> **Executor**: Mark each step `[X]` only after its approved implementation work and GREEN validation are truthfully complete.
> All Implementation Steps must be `[X]` before requesting independent implementation review.
> Update this file at: `plan/response-cache-contract-migration/response-cache-contract-migration.step.md`

## Implementation Steps

- [X] 1. In the listed `tests/response_cache/` files, establish direct-import RED coverage for the technical-spec and reconciliation contract; do not rewrite the historical `red-tests.yaml`.
- [X] 2. In `key.py`, `outcomes.py`, `record.py`, and `errors.py`, establish `CacheKey`, immutable record / token, closed outcomes, and the sole operational-error family; remove old direct entry routing only through the declared compatibility disposition.
- [X] 3. In `freshness_policy.py`, `ttl_freshness_policy.py`, and `cache.py`, implement write-time expiry, the five keyword-only collaborators, one clock owner, complete record construction, lookup and remember outcomes, and unchanged cancellation / defects.
- [X] 4. In `ports/store.py`, `codec.py`, `version_token_factory.py`, `invalidator.py`, and `ports/__init__.py`, establish the target submodule-only ports and remove normal feature-hasher dependence as specified.
- [X] 5. In `_in_memory_store.py` and `invalidation.py`, implement coherent whole-record replacement, atomic `delete_if_version`, and key-local invalidation; prove stale cleanup cannot delete a concurrent replacement.
- [X] 6. In `compat.py`, with the declared removals of `entry.py`, `key_factory.py`, `_canonical_feature_hasher.py`, and `ports/feature_hasher.py`, implement only the reconciled deprecated direct-import surface, warnings, legacy maps, and ignored context sentinel.
- [X] 7. In `__init__.py` and package-surface tests, expose exactly the target root surface, enforce legacy root/direct-path absence, and prove `compat` with ordinary imports only.
- [X] 8. Update exactly `README.md`, `docs/architecture.md`, and `docs/specs/response-cache-boundary.md` after GREEN behavior validation; then complete the feature tracker and request independent implementation review.

## Validation Evidence

- 2026-08-06 schema-version repair: `uv run pytest tests/response_cache/test_response_cache_contract_migration.py tests/response_cache/test_cache.py -v --no-cov` passed (18 tests).
- 2026-08-06 schema-version repair: `uv run pytest` passed (202 tests; 94.19% coverage).
- 2026-08-06 schema-version repair: `uv run ruff check src tests docs README.md analysis/response-cache-contract-migration plan/response-cache-contract-migration` passed.
- 2026-08-06 schema-version repair: `uv run pyright` passed (0 errors, 0 warnings).
- 2026-08-06 remember-cancellation regression: `uv run pytest tests/response_cache/test_cache.py tests/response_cache/test_response_cache_contract_migration.py -v --no-cov` passed (19 tests), including direct `remember(...)` store-cancellation identity propagation.
- 2026-08-06 remember-cancellation regression: `uv run pytest` passed (203 tests; 94.59% coverage).
- 2026-08-06 remember-cancellation regression: `uv run ruff check src tests docs README.md analysis/response-cache-contract-migration plan/response-cache-contract-migration` and `uv run pyright` passed (0 errors, 0 warnings).
