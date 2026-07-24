---
topic: loaded-runtime-binding-refactor
phase: plan-authoring
created: 2026-07-24
---

# loaded-runtime-binding-refactor — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/loaded-runtime-binding-refactor/loaded-runtime-binding-refactor.step.md`

## Workflow Stages

- [X] plan-authoring
- [ ] plan-review
- [ ] tdd-test-authoring
- [ ] implementation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [ ] 1. Tester writes/revises declared behavior, surface, AST, composition, precise ONNX loader and ONNX regression tests; writes topic Pyright config/type fixture; executes exact topic Pyright against unchanged production and records RED evidence.
- [ ] 2. Implementer modifies concrete runtime model/package export boundary.
- [ ] 3. Implementer modifies executor/package export boundary with exact gate/timestamp/direct-await lifecycle.
- [ ] 4. Implementer deletes old loader/helper, writes private `model_pool/loaders/` package and `_OnnxRuntime` Protocol with only `get_providers() -> list[str]`; casts `asyncio.to_thread(InferenceSession, ...)` only at optional-stub loader boundary, then modifies binding/resolver to retain precise ONNX pairing until sole outer erasure cast.
- [ ] 5. Implementer modifies composition/private factory and internal pool acquire; removes pool package export.
- [ ] 6. Implementer deletes all declared obsolete sources/tests/live fixtures, leaves all four historical configs untouched, runs pre-merge validation, checks path contract, updates tracker.
