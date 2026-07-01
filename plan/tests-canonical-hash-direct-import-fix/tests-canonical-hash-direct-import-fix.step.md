---
topic: tests-canonical-hash-direct-import-fix
phase: implement-plan
created: 2026-06-30
---

# tests-canonical-hash-direct-import-fix — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for later review.
> Update this file at:
> `plan/tests-canonical-hash-direct-import-fix/tests-canonical-hash-direct-import-fix.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] implementation

## Implementation Steps

- [X] 1. Update `tests/model_registry/model_payload/test_canonical_hash.py` to replace `from importlib import import_module` and each `import_module(...)` call with direct module imports while preserving the existing `ModelPayloadHasher` import and the same three public-surface assertion semantics.
- [X] 2. Re-check `src/async_model_gateway/model_registry/__init__.py` and `src/async_model_gateway/model_registry/model_payload/__init__.py` as read-only inspection surfaces so the rewritten test continues to assert the intended package boundaries without modifying those source files.
- [X] 3. Run `uv run ruff check tests/model_registry/model_payload/test_canonical_hash.py` and `uv run pytest tests/model_registry/model_payload/test_canonical_hash.py --cov-fail-under=0`, then update `plan/tests-canonical-hash-direct-import-fix/tests-canonical-hash-direct-import-fix.step.md` to reflect implementer-owned completion truthfully.
