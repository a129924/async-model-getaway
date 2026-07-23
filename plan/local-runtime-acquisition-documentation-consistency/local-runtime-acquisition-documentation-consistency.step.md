---
topic: local-runtime-acquisition-documentation-consistency
phase: pr-comment
created: 2026-07-22
---

# local-runtime-acquisition-documentation-consistency — Step Tracking

> **Executor**: Mark each step `[X]` only when complete.
> All documentation and validation steps must be `[X]` before PR routing.
> Update this file at:
> `plan/local-runtime-acquisition-documentation-consistency/local-runtime-acquisition-documentation-consistency.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] human-check
- [X] documentation-update
- [X] validation
- [X] implementation-review
- [ ] pr-comment

## Gate Status

- Documentation/boundary implementation review is complete: the declared
  `local-runtime-acquisition-documentation-consistency.implementation-review.yaml`
  records `verdict: approved`.
- This is a docs-only topic; no code-review stage or code-review artifact is declared
  or required.
- Current workflow position: `pr-comment` is pending. No commit, push, PR creation, or
  PR review surface has been performed or authorized.

## Implementation Steps

- [X] 1. Update only the local runtime/runtime-model wording in `README.md` so it
  distinguishes completed ONNX acquisition from deferred provider invocation and
  lifecycle behavior.
- [X] 2. Update `docs/architecture.md` with the fixed local acquisition-to-result flow
  and corrected loader-local opaque-handle ownership, without extending execution or
  orchestration scope.
- [X] 3. Update `docs/specs/model-side-boundary.md` with detailed explicit routing,
  ONNX session acquisition, opaque-handle, and sole `ModelExecution` handoff wording.
- [X] 4. Update `docs/specs/core-abstractions-boundary.md` with the matching concise
  dependency-direction summary only.
- [X] 5. Run declared focused/full tests, Pyright, Ruff, and `git diff --check`; verify
  changed implementation paths are exactly the four declared documents, then record
  actual progress without closing a Human or PR gate.
