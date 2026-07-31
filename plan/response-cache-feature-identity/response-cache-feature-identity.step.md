---
topic: response-cache-feature-identity
phase: spec-and-plan-finalization
created: 2026-07-31
---

# response-cache-feature-identity — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/response-cache-feature-identity/response-cache-feature-identity.step.md`

## Workflow Stages

- [X] plan-authoring
- [ ] plan-review
- [X] tdd-test-authoring
- [X] implementation
- [X] implementation-review
- [X] code-review

> This explicit contract/error-policy replan invalidates the prior plan-review, human-check, RED-test, and implementation-review gate evidence for future execution. A fresh Reviewer-owned `approved` plan-review artifact and a fresh Human-owned human-check clearance are required before Tester may start the fresh RED-test stage. After fresh RED evidence, the Implementer may perform the two-path correction; then an independent Reviewer must create fresh implementation-review evidence before return to `pr-comment`. Do not treat chat consensus, old approval, or old human clearance as a gate.

## Implementation Steps

- [X] 1. After fresh plan review and fresh human check, revise direct-import RED tests in `tests/response_cache/test_canonical_feature_hasher.py` and record fresh `plan/response-cache-feature-identity/response-cache-feature-identity.red-tests.yaml` evidence. Cover base-`str` identity material for key/value subclasses that override `__str__`, safe built-in ordering under custom comparison subclasses, strict UTF-8 rejection for an unpaired surrogate, direct `TypeError` whose `__cause__` is the original `UnicodeEncodeError`, and factory propagation without a key.
- [X] 2. Modify only `src/async_model_gateway/response_cache/_canonical_feature_hasher.py`: after `isinstance` validation, obtain accepted subclass material with `str.__str__(key)` and `str.__str__(value)`, sort only that built-in material, retain the locked JSON representation, and translate only the UTF-8 `UnicodeEncodeError` into chained `TypeError`. Do not modify the factory, port, exports, or any other behavior owner.
- [X] 3. Make the fresh RED tests green and run `uv run pytest tests/response_cache/test_canonical_feature_hasher.py -v --no-cov`, `uv run pytest`, `uv run ruff check src tests plan/response-cache-feature-identity`, `uv run pyright`, and `uv run pre-commit run --all-files`. Update this step tracker for completed implementation work; leave fresh reviewer and human artifacts to their independent owners.
