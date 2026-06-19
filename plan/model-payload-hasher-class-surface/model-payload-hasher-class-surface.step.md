---
topic: model-payload-hasher-class-surface
phase: implement-plan
created: 2026-06-19
---

# model-payload-hasher-class-surface — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/model-payload-hasher-class-surface/model-payload-hasher-class-surface.step.md`

## Implementer Stages

- [X] tdd-test-authoring
- [X] implementation
- [X] validation

## Implementation Steps

- [X] 1. Update `tests/model_registry/model_payload/test_canonical_hash.py` and record `plan/model-payload-hasher-class-surface/model-payload-hasher-class-surface.red-tests.yaml` so the bounded pytest coverage targets `ModelPayloadHasher`, confirms the old public function is absent from the allowed import surface, preserves the existing hashing semantics, and keeps `model_registry` free of re-exports.
- [X] 2. Update `src/async_model_gateway/model_registry/model_payload/canonical_hash.py` and `src/async_model_gateway/model_registry/model_payload/__init__.py` so `ModelPayloadHasher` becomes the only allowed public owner, the old standalone function is removed, and the internal canonicalization helper continues to enforce the existing runtime validation and digest behavior.
- [X] 3. Update `README.md`, `docs/architecture.md`, `docs/specs/canonical-input-boundary.md`, and `docs/specs/model-side-boundary.md` so every repo-visible description of the hashing core matches the class-first public contract without widening the architecture scope.
- [X] 4. Run `uv run pytest tests/model_registry/model_payload/test_canonical_hash.py -v`, `uv run ruff check README.md docs src tests plan/model-payload-hasher-class-surface`, and `uv run pyright`, then update this file to reflect the completed implementer-owned work before reviewer inspection.
