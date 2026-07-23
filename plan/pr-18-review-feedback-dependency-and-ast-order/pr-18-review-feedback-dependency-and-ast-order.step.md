---
topic: pr-18-review-feedback-dependency-and-ast-order
phase: pr-comment
created: 2026-07-23
---

# pr-18-review-feedback-dependency-and-ast-order — Step Tracking

> **Executor**: Mark each step `[X]` only when complete.
> All Implementation Steps must be `[X]` before submitting for
> `python-implementation-review`.
> Update this file at:
> `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [X] human-check
- [X] tdd-test-authoring
- [X] implementation
- [X] validation
- [X] implementation-review
- [X] code-review

## Gate Status

- Fresh Plan-Reviewer `approved` verdict and Human clearance
  `cleared_for: implement-plan` are recorded in the declared artifacts.
- D1 is `trivial`: no `*.spec.md` or fresh RED evidence artifact is required. The
  deterministic AST-helper test update was the first implementation step.
- The only implementation paths are `pyproject.toml`, `uv.lock`,
  `.github/workflows/ci.yml`, and
  `tests/model_runtime/model_execution/test_model_execution_package_surface.py`.
- Dev sync/import, static analysis, focused and full tests, lint, pre-commit, and
  `git diff --check` passed. Both declared implementation-review and code-review
  artifacts record `verdict: approved`.
- All implementation and review gates are complete. Current workflow position:
  `pr-comment` / Human handoff. No commit, push, PR update, GitHub reply, or thread
  resolution has been performed or authorized. Each publish/PR action and each GitHub
  reply/resolve action requires separate explicit Human permission.

## Implementation Steps

- [X] 1. In `tests/model_runtime/model_execution/test_model_execution_package_surface.py`,
  make `_provider_runtime_call_paths()` return a deterministically sorted collected
  relative `Path` list without changing scan semantics or its assertion target.
- [X] 2. In `pyproject.toml` and `uv.lock`, retain the published `onnx` optional-extra
  ONNX Runtime constraint and add that exact existing constraint to dev without
  unrelated resolution drift.
- [X] 3. In `.github/workflows/ci.yml`, restore only the `Sync dependencies` command
  to `uv sync --frozen --group dev` and preserve every other workflow line.
- [X] 4. Run normal dev sync/import, static, focused/full test, lint, pre-commit, and
  diff validation; inspect only the four declared implementation diffs and hand off to
  independent implementation review without PR thread actions.
