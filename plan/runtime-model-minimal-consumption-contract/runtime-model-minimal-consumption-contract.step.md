---
topic: runtime-model-minimal-consumption-contract
phase: spec-and-plan-finalization
created: 2026-07-15
---

# runtime-model-minimal-consumption-contract — Step Tracking

> **Current state**: `review-ready` for contract-correction revision. The prior immutable
> concrete-handle implementation/reviews are historical evidence only and cannot approve
> this revision. Fresh Plan-Reviewer approval and fresh Human check are required.

## Workflow Stages

- [X] plan-authoring (immutable revision; superseded)
- [ ] contract-correction plan-authoring (complete; awaiting re-review)
- [ ] plan-review (fresh correction revision)
- [ ] human-check
- [ ] tdd-test-authoring
- [ ] implementation
- [ ] implementation-review
- [ ] code-review
- [ ] pr-comment
- [ ] human-merge
- [ ] release

## Implementation Steps

- [X] Historical 1. Tester wrote RED tests for the immutable revision; this evidence is superseded and must not be overwritten.
- [X] Historical 2. Implementer added the immutable opaque handle; this implementation must be corrected only after fresh gates.
- [X] Historical 3. Implementer narrowed `ModelPool.acquire`; retained annotation target remains valid.
- [X] Historical 4. Implementer narrowed private loader/handlers; retained annotation target remains valid.
- [X] Historical 5. Validation evidence applies only to the immutable revision.
- [X] 1. Tester writes fresh replacement RED tests in `tests/model_runtime/runtime_model/test_loaded_runtime_model.py`, `tests/model_runtime/runtime_model/test_runtime_model_package_surface.py`, `tests/model_runtime/model_pool/test_model_pool.py`, `tests/model_runtime/model_pool/test_local_model_loader.py`, and `tests/model_runtime/model_pool/test_model_pool_package_surface.py`; static-imports the private factory, asserts abstract direct-instantiation rejection, factory abstract-boundary/provenance, internal `_provider_runtime()` seam, and no public leakage; removes immutable/mutation expectations without dynamic loading.
- [X] 2. Implementer corrects `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py` and `src/async_model_gateway/model_runtime/runtime_model/__init__.py` to public ABC contract/private ordinary-`__init__` local implementation/private factory export boundary.
- [X] 3. Implementer preserves `src/async_model_gateway/model_runtime/model_pool/pool.py` return type and validation/retention/direct-await behavior while adapting tests to corrected handle semantics.
- [X] 4. Implementer preserves `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` and all handler return types/dispatch/`assert_never`/no-I/O stubs while adapting tests to corrected handle semantics.
- [X] 5. Implementer runs `uv run pytest --no-cov tests/model_runtime/runtime_model tests/model_runtime/model_pool -v`, `uv run pytest -v`, `uv run ruff check src tests plan/runtime-model-minimal-consumption-contract`, `uv run pyright`, `uv lock --check`, and a diff check; records new truthful progress before fresh implementation/code review.
