---
topic: response-cache-freshness-policy
phase: plan-authoring
created: 2026-07-28
---

# response-cache-freshness-policy — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/response-cache-freshness-policy/response-cache-freshness-policy.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

> Re-review required: this tracker carries the unique-basename path rework from `tests/response_cache/test_freshness_policy.py` to `tests/response_cache/test_response_cache_freshness_policy.py`. The pre-implementation RED collection evidence recorded at the old path covers the same unchanged freshness requirements and remains valid historical evidence after the mechanical rename. Because the rename is non-semantic, the new path requires only an explicit old-to-new evidence mapping plus focused and full GREEN validation; `new_red_evidence_created: false` is expected. Do not create or claim new RED evidence after production implementation exists. This correction requires renewed Reviewer and Human gates; keep `plan-review` pending until they are regenerated. Direct imports remain required, and neither `pyproject.toml` nor `tests/model_registry/test_freshness_policy.py` changes.
Renewed plan-review and human-check approve this corrected historical
traceability only. They do not require repeating the already completed rename
or creating a new RED result after production implementation.

## Implementation Steps

- [X] 1. Historical completed action: under the prior cleared gate, mechanically
  renamed `tests/response_cache/test_freshness_policy.py` to
  `tests/response_cache/test_response_cache_freshness_policy.py`; retained
  direct imports; and ran focused and full GREEN validation. The predecessor
  path's pre-implementation RED collection evidence covers the same unchanged
  requirements. No post-implementation RED evidence is required or permitted;
  `new_red_evidence_created: false` is expected.
- [X] 2. Add `src/async_model_gateway/response_cache/freshness_policy.py` with the internal, fully typed `FreshnessPolicy.is_fresh(*, written_at, now) -> bool` contract; do not add a list, pipeline, generic cache-policy abstraction, or re-export.
- [X] 3. Add `src/async_model_gateway/response_cache/ttl_freshness_policy.py` with injected `TtlFreshnessPolicy`, strict positive-`timedelta` validation, and strict-before-expiry freshness semantics; keep it synchronous and internal.
- [X] 4. Add `src/async_model_gateway/response_cache/_in_memory_store.py` with internal `InMemoryResponseCacheStore` implementing the unchanged async `ResponseCacheStore` port, keyword-only `freshness_policy` injection, aware-UTC successful-write timestamps, non-renewing reads, overwrite timestamp replacement, and expired-as-`None` lookup behavior; do not add locks, lifecycle methods, eviction/deletion, or a public export.
- [X] 5. Update only `README.md`, `docs/architecture.md`, `docs/settings-policy.md`, and `docs/specs/response-cache-boundary.md` to match the frozen internal-policy/store scope; leave every ReadOnly public-boundary and version path unchanged.
- [X] 6. Run `uv run pytest tests/response_cache/test_response_cache_freshness_policy.py -v --no-cov`, `uv run pytest`, `uv run ruff check README.md docs src tests plan/response-cache-freshness-policy`, `uv run pyright`, and `uv run pre-commit run --all-files`; update `plan/response-cache-freshness-policy/response-cache-freshness-policy.step.md` with completed implementation work, while leaving Reviewer- and Human-owned artifacts for their owners.
