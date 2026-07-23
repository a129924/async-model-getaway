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
- [X] code-review (not applicable: amended plan uses validation-only review as final gate)

## Gate Status

- The original dependency/CI/AST repair remains historical truth, but its plan-review,
  Human clearance, implementation-review, and code-review artifacts do not approve the
  newly added human-check terminal-LF path.
- Fresh Plan-Reviewer `approved` and Human's exact final-LF gate write are recorded in
  the declared artifacts. The human-check now ends `7d 0a`, and parsed JSON remains
  exactly `{"cleared_for":"implement-plan"}` with no other byte or gate-semantic
  change.
- D1 validation-hygiene retrofit is `trivial`: no fresh spec, RED artifact, source,
  dependency, lock, workflow, test, docs, PR response, commit, or push change is
  authorized.
- Validation-only Reviewer recorded `verdict: approved` after pre-commit all-files,
  `git diff --check`, raw diff inspection, and terminal-LF/parsed-JSON guards. The
  amended plan declares this validation-only implementation review as the final review
  gate; the existing code-review artifact remains Historical ReadOnly and no fresh code
  review is required.
- Current workflow position: `pr-comment` / Human handoff. Commit, push, PR update,
  GitHub reply, and thread resolution have not been authorized or performed; each
  requires separate explicit Human permission.

## Implementation Steps

- [X] 1. Historical ReadOnly — the AST-helper deterministic-order repair is complete;
  `tests/model_runtime/model_execution/test_model_execution_package_surface.py` must
  not change for this retrofit.
- [X] 2. Historical ReadOnly — the published extra/dev dependency and `uv.lock` repair
  are complete; `pyproject.toml` and `uv.lock` must not change for this retrofit.
- [X] 3. Historical ReadOnly — the CI plain frozen dev-sync repair is complete;
  `.github/workflows/ci.yml` must not change for this retrofit.
- [X] 4. Historical ReadOnly — original normal-dev validation/reviews are complete, but
  do not approve the new final-LF path.
- [X] 5. Fresh Plan-Reviewer reviewed the amended final-LF-only contract and recorded
  `approved` in the declared plan-review artifact.
- [X] 6. After fresh plan review, Human wrote only one terminal LF to the declared
  human-check file, preserving parsed `{"cleared_for":"implement-plan"}` semantics.
- [X] 7. Validation-only Reviewer ran the declared pre-commit/diff/JSON guards and
  recorded approved validation evidence without changing any implementation or PR path.
