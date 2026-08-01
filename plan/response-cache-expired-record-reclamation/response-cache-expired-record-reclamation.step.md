---
topic: response-cache-expired-record-reclamation
phase: spec-and-plan-finalization
created: 2026-08-01
---

# response-cache-expired-record-reclamation — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.step.md`

## Workflow Stages

- [X] plan-authoring
- [ ] plan-review
- [ ] tdd-test-authoring
- [ ] implementation
- [ ] implementation-review
- [ ] code-review

> This feature worktree requires a fresh Reviewer-owned `approved` plan-review artifact and fresh Human-owned human-check clearance before Tester may begin RED test authoring. Tester must create RED evidence before the Implementer modifies production behavior. After all implementation steps are complete, an independent Reviewer must create implementation-review evidence before the Observer may route to `pr-comment`. Chat approval does not clear these repo-visible gates.

## Implementation Steps

- [X] 1. In `tests/response_cache/test_in_memory_store.py`, add direct-import RED tests for `False`-driven single-key reclamation, no second policy call after reclamation, same-key reinsertion, other-key isolation, and policy-exception preservation; record matching `*.red-tests.yaml` evidence before source changes.
- [X] 2. In `src/async_model_gateway/response_cache/_in_memory_store.py`, remove only the requested record after the injected policy returns `False`, then preserve the existing `None` miss and all other lookup behavior.
- [X] 3. In `README.md`, `docs/architecture.md`, and `docs/specs/response-cache-boundary.md`, align only the existing internal freshness wording with lookup-time stale-record reclamation and retain all exclusions.
- [X] 4. Run the declared focused/full test, lint, type, and pre-commit commands; update this step tracker for completed creator work and leave reviewer/human evidence to their owners.
