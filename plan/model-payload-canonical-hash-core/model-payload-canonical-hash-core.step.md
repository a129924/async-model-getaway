---
topic: model-payload-canonical-hash-core
phase: plan-authoring
created: 2026-06-19
---

# model-payload-canonical-hash-core — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/model-payload-canonical-hash-core/model-payload-canonical-hash-core.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

## Gate Status

- Reviewer verdict: `approved`
- Human check: passed
- Current workflow position: `implement-plan` is complete; this topic is ready
  to enter `pr-comment`

## Implementation Steps

- [X] 1. Add bounded pytest coverage in `tests/model_registry/model_payload/test_canonical_hash.py` for the happy path: equal nested payload content with different dict insertion order must hash to the same SHA-256 hex string, while preserving the public import surface from `async_model_gateway.model_registry.model_payload`.
- [X] 2. Extend `tests/model_registry/model_payload/test_canonical_hash.py` with invalid, edge, regression, and backward-compatibility coverage: unsupported nested types raise `TypeError`, nested non-`str` dict keys raise `TypeError`, empty nested containers are accepted, list order affects the hash, and scalar values such as `1` and `1.0` are not normalized to the same digest.
- [X] 3. Add `src/async_model_gateway/model_registry/model_payload/canonical_hash.py` with the internal recursive canonicalization helper and the public `hash_model_payload` function so the implementation accepts only `dict[str, JSONLike]` at the top level, canonicalizes nested dicts recursively, preserves list order, rejects unsupported types with `TypeError`, and returns a SHA-256 hex digest.
- [X] 4. Add `src/async_model_gateway/model_registry/model_payload/__init__.py` and `src/async_model_gateway/model_registry/__init__.py` so the allowed public import surface is `async_model_gateway.model_registry.model_payload`, `model_payload/__init__.py` may re-export `hash_model_payload`, and `model_registry/__init__.py` does not re-export it.
