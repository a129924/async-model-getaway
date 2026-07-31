---
topic: response-cache-feature-identity
phase: plan-authoring
created: 2026-07-31
---

# response-cache-feature-identity — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/response-cache-feature-identity/response-cache-feature-identity.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

> Execution may start only after the Reviewer-owned plan-review artifact records `approved` and the Human-owned human-check artifact explicitly clears the topic for `implement-plan`. The optional analysis layer is absent and is recorded as a semantic warning; the human override is the frozen baseline unless a later analysis artifact conflicts and routes the topic back to `spec-and-plan-finalization`.

## Implementation Steps

- [X] 1. As the first `implement-plan` Python subphase, add direct-import RED tests in `tests/response_cache/test_canonical_feature_hasher.py` and record `plan/response-cache-feature-identity/response-cache-feature-identity.red-tests.yaml`. Cover the frozen canonical JSON pair-list form, fixed UTF-8/SHA-256 lowercase digest, insertion-order independence, value/key distinction, non-normalization, `TypeError` failures, and factory injection without changing existing regression tests.
- [X] 2. Add `src/async_model_gateway/response_cache/_canonical_feature_hasher.py` with internal `CanonicalFeatureHasher(FeatureHasher)`. Validate runtime keys and values before sorting, serialize the sorted two-string pair list using the locked JSON settings, UTF-8 encode it, and return `sha256(...).hexdigest()`; do not add exports, fallback behavior, or other interfaces.
- [X] 3. Make the RED tests green and run `uv run pytest tests/response_cache/test_canonical_feature_hasher.py -v --no-cov`, `uv run pytest`, `uv run ruff check src tests plan/response-cache-feature-identity`, `uv run pyright`, and `uv run pre-commit run --all-files`. Update `plan/response-cache-feature-identity/response-cache-feature-identity.step.md` only for creator-owned completed work; leave reviewer and human artifacts to their owners.
