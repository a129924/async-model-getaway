Analysis-layer routing: incomplete optional-analysis mode. Semantic warning: neither `analysis/response-cache-expired-record-reclamation/requirements.md` nor `analysis/response-cache-expired-record-reclamation/technical-spec.md` exists. This plan uses the human-accepted Draft Plan and inspected response-cache boundary as its provisional execution baseline; it does not claim strict analysis mode. If either companion is added or conflicts with this plan before implementation, return to `spec-and-plan-finalization`.

# response-cache-expired-record-reclamation

## Goal / Outcome

- Make an internal process-local response-cache lookup reclaim its own record after the injected freshness policy explicitly reports it stale, while preserving the existing `None` cache-miss result.
- On completion, a fresh record remains readable, a policy exception remains visible and preserves its record, and no response-cache public surface changes.

## Scope

- **In scope**:
  - Modify the stale-result branch in `src/async_model_gateway/response_cache/_in_memory_store.py` so the requested key is removed only after the existing injected freshness policy returns `False`.
  - Extend `tests/response_cache/test_in_memory_store.py` with direct-import coverage for stale-record reclamation, policy-exception preservation, reinsertion, and key isolation.
  - Align the bounded stale-record statement in `README.md`, `docs/architecture.md`, and `docs/specs/response-cache-boundary.md`.
  - Create this topic's plan, behavior specification, and step tracker; declare later gate-evidence paths without pre-filling them.

- **Out of scope**:
  - Changes to TTL/freshness authority or duration semantics, including `FreshnessPolicy`, `TtlFreshnessPolicy`, write timestamps, read renewal, or policy injection.
  - Capacity/admission policy, LRU/FIFO/other eviction, background sweeping, public invalidation/deletion/clear, persistence, settings, metrics, tracing, or orchestrator wiring.
  - Public ports, package exports, key/hash ownership, async resource lifecycle, locks, timeout/retry/cancellation policy, dependencies, versioning, release, or migration work.

### Executable file inventory

| Classification | Exact paths | Contract |
| --- | --- | --- |
| Written now | `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.plan.md`; `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.spec.md`; `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.step.md` | Planning actor creates these planning artifacts in this pass only. |
| Planned Modify | `src/async_model_gateway/response_cache/_in_memory_store.py`; `tests/response_cache/test_in_memory_store.py`; `README.md`; `docs/architecture.md`; `docs/specs/response-cache-boundary.md` | Implementer and Tester may change only these future implementation paths after both plan-review and human-check gates clear. |
| Planned future gate artifacts | `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.plan-review.json`; `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.human-check.json`; `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.red-tests.yaml`; `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.implementation-review.yaml` | Reviewer, Human, Tester, and Reviewer respectively create their own evidence at the required gate; the planning actor does not prefill it. |
| ReadOnly / preserve-and-validate | `pyproject.toml`; `uv.lock`; `src/async_model_gateway/__version__.py`; `src/async_model_gateway/response_cache/__init__.py`; `src/async_model_gateway/response_cache/cache.py`; `src/async_model_gateway/response_cache/entry.py`; `src/async_model_gateway/response_cache/key.py`; `src/async_model_gateway/response_cache/key_factory.py`; `src/async_model_gateway/response_cache/freshness_policy.py`; `src/async_model_gateway/response_cache/ttl_freshness_policy.py`; `src/async_model_gateway/response_cache/ports/__init__.py`; `src/async_model_gateway/response_cache/ports/feature_hasher.py`; `src/async_model_gateway/response_cache/ports/store.py`; `tests/response_cache/test_cache.py`; `tests/response_cache/test_entry.py`; `tests/response_cache/test_key.py`; `tests/response_cache/test_key_factory.py`; `tests/response_cache/test_response_cache_freshness_policy.py`; `tests/response_cache/test_ttl_freshness_policy.py`; `tests/response_cache/test_response_cache_package_surface.py`; `docs/settings-policy.md` | Existing package surface, async port, identity owners, freshness authority, TTL boundary, settings exclusion, version metadata, and regressions stay unchanged. |
| Deleted | None | This topic deletes no file. Internal removal is a runtime record-reclamation behavior only. |
| Out-of-scope / no path authorization | No additional repository paths | Any need for a policy, port, public API, lifecycle, capacity, persistence, settings, orchestrator, or release path is scope drift and returns to planning. |

## Locked Decisions

- D1 verdict: `non-trivial` — this topic changes observable internal store state after a stale decision, adds failure-safety and key-isolation regressions, aligns three repository documentation surfaces, and requires Python workflow gates.
- `FreshnessPolicy.is_fresh(...) is False` is the sole authority that permits reclamation. The store must not calculate expiry or reinterpret TTL itself.
- In `InMemoryResponseCacheStore.get(...)`, lookup first obtains the stored record, calls the existing policy with the original `written_at` and current aware-UTC time, then removes exactly that lookup key only when the policy returns `False`; it returns the existing `None` miss.
- A policy exception is not stale: it propagates unchanged and the record remains available for a later policy decision. A fresh (`True`) result likewise preserves the record and returns its entry.
- Reclamation is synchronous dictionary state handling inside the already-running `get(...)` body. It does not add an `await`, lock, task, cleanup loop, capacity policy, lifecycle method, or public deletion API.
- This topic adopts the Python planning extension: behavior spec, step tracker, RED-test evidence, and implementation-review evidence are mandatory before PR routing. RED-test authoring is the first `implement-plan` subphase.
- Stable-library metadata is required because `README.md` is a Planned Modify path. Version metadata and release intent are explicitly unchanged.

## Boundaries / Exclusions

- The planning actor writes only the three Written-now artifacts. It does not implement source/tests/docs, create a worktree, write reviewer verdicts, close a human gate, commit, push, or open a PR.
- The Tester must use direct imports in `tests/response_cache/test_in_memory_store.py`; dynamic module loading is not authorized.
- The Implementer may modify only the Planned Modify paths and must return to planning if another path, public contract, or async ownership decision becomes necessary.
- The Reviewer independently authors `*.plan-review.json` and `*.implementation-review.yaml`; the Human independently authors `*.human-check.json` and controls human merge. Neither role completes creator-owned work.
- This narrow lookup-time reclamation does not settle whether expired records are proactively swept, retained under capacity pressure, evicted by an admission policy, or removed through a public API; each is a separate future topic.

## Status / Allowed Transitions

- **Current**: `publish-in-progress`
- **Transition evidence**: the Reviewer-owned plan review is `approved`, the Human-owned human check is `cleared` for `implement-plan`, RED-test evidence is `red-tests-ready`, and the independent implementation review is `approved`. The step tracker records all workflow stages and implementation steps complete, including code review. These completed `spec-and-plan-finalization` and `implement-plan` gates make the topic ready for `pr-comment` routing; it is neither merged nor released.
- **Execution model**: `spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix`; stop at `merged`. The conditional `release` workflow does not apply.
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `publish-in-progress` -> `merged`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`

Routing notes:

- `approved` requires both a Reviewer-owned `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.plan-review.json` with verdict `approved` and a Human-owned `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.human-check.json` with explicit clearance. Conversational approval does not replace either repo-visible gate.
- After both gates clear, Tester writes RED tests and `*.red-tests.yaml` before Implementer changes production code. An independent Reviewer must then write `*.implementation-review.yaml` before the topic advances to `pr-comment`.
- If review asks for capacity, background cleanup, public deletion, async/concurrency behavior, freshness authority, public API, or an unlisted path, classify it as scope/contract drift and return to `spec-and-plan-finalization`.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Absent requirements companion | `analysis/response-cache-expired-record-reclamation/requirements.md` | Analysis producer | Optional business-intent guardrail; absent at plan authoring and not created in this topic pass. |
| Absent technical-spec companion | `analysis/response-cache-expired-record-reclamation/technical-spec.md` | Analysis producer | Optional execution source; absent at plan authoring and not created in this topic pass. |
| Topic plan | `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.plan.md` | Planning actor | Canonical workflow contract plus supplemental Python implementation contract. |
| Topic behavior spec | `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.spec.md` | Planning actor | Required non-trivial behavioral contract for RED tests and review. |
| Topic step tracker | `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.step.md` | Planning actor -> Implementer | Initialized workflow/progress record; Implementer updates implementation completion only. |
| Plan review | `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.plan-review.json` | Reviewer | Single-object independent planning verdict. |
| Human check | `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.human-check.json` | Human | Explicit repo-visible clearance before RED tests and implementation. |
| RED-test evidence | `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.red-tests.yaml` | Tester | Evidence that direct-import reclamation tests failed against unchanged production behavior before implementation. |
| Implementation review | `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.implementation-review.yaml` | Reviewer | Plan-conformance evidence required before PR routing. |
| Internal store | `src/async_model_gateway/response_cache/_in_memory_store.py` | Implementer | Add only lookup-time stale-record reclamation after an explicit `False` policy result. |
| Store tests | `tests/response_cache/test_in_memory_store.py` | Tester | Direct-import tests for reclamation, exception preservation, reinsertion, and key isolation. |
| README summary | `README.md` | Implementer | Add only the bounded statement that stale lookup reclaims the confirmed stale process-local record. |
| Architecture summary | `docs/architecture.md` | Implementer | Align gateway/cache responsibility wording with stale lookup-time reclamation. |
| Response-cache boundary spec | `docs/specs/response-cache-boundary.md` | Implementer | Align operational-boundary wording without widening the policy or public contract. |
| Validation configuration | `pyproject.toml`; `uv.lock`; `src/async_model_gateway/__version__.py` | Reviewer | ReadOnly validation and no-version-bump evidence. |

Artifact path notes:

- `README.md` is a Planned Modify path. There is no standalone `VERSION` file; `pyproject.toml`, `src/async_model_gateway/__version__.py`, and `uv.lock` remain ReadOnly with no version bump.
- `.github/copilot-instructions.md` is not modified.
- The table is exhaustive. Work outside it is plan drift and must return to planning before change.

## Stable library metadata

- `README row`: modify only the current response-cache baseline wording to state that lookup-time reclamation removes a record after the internal injected policy confirms it stale; do not claim a new public cache feature.
- `VERSION bump`: no bump. `pyproject.toml`, `src/async_model_gateway/__version__.py`, and `uv.lock` remain synchronized to the existing version.
- `timing`: `publish-in-progress` after implementation review; this documentation alignment does not create a release phase.
- `rationale`: README is a stable-library summary surface, but the topic has no public API, dependency, compatibility, or publication change.
- `release notes`: none; do not create tags, publication, or release notes.

## Implementation Steps

1. In `tests/response_cache/test_in_memory_store.py`, author direct-import RED tests and record `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.red-tests.yaml`: prove a `False` decision returns `None`, removes the requested record so a repeat lookup does not call the policy, permits same-key reinsertion, leaves another fresh key intact, and lets a policy exception propagate while preserving its record.
2. In `src/async_model_gateway/response_cache/_in_memory_store.py`, modify only the existing stale-result branch of `InMemoryResponseCacheStore.get(...)` to remove `key` after `FreshnessPolicy.is_fresh(...)` returns `False`, then return `None`; preserve fresh hits, original timestamps, overwrites, missing-key behavior, and exception propagation.
3. In `README.md`, `docs/architecture.md`, and `docs/specs/response-cache-boundary.md`, update only the existing internal process-local freshness wording to document stale lookup-time reclamation and retain the exclusions for public deletion, capacity/eviction, background cleanup, persistence, settings, and orchestration.
4. Run `uv run pytest tests/response_cache/test_in_memory_store.py -v --no-cov`, `uv run pytest`, `uv run ruff check README.md docs src tests plan/response-cache-expired-record-reclamation`, `uv run pyright`, and `uv run pre-commit run --all-files`; then update only the creator-owned completion state in `plan/response-cache-expired-record-reclamation/response-cache-expired-record-reclamation.step.md` and submit for independent implementation review.

## Validation / Acceptance Checks

- The topic plan has all canonical sections in order, exact path inventory, declared non-release stable metadata, canonical transitions, and a single JSON reviewer-handoff contract.
- The behavior spec covers stale reclamation, exception preservation, same-key reinsertion, fresh-hit preservation, and public-boundary invariants.
- RED evidence is direct-import only, runs before source modification, and maps every behavior-spec acceptance criterion to focused tests.
- A stale `False` policy result produces `None` and permanently removes only that key's stored record; a repeat lookup does not invoke the policy for the removed record.
- A fresh `True` policy result returns the original entry and leaves the record intact; overwrite semantics and original-write timestamps remain covered by existing regressions.
- A policy exception propagates without deletion; a later fresh policy decision may still read the same entry.
- Package roots, ports, key/hash owners, freshness and TTL modules, version metadata, settings boundary, and all ReadOnly regressions remain unchanged.
- Focused pytest, full pytest, Ruff, Pyright strict, and pre-commit pass; implementation review verifies path confinement and no dynamic test-module loading.

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

- No release workflow required.
- After merge, do not change version metadata, `uv.lock`, release notes, tags, publication state, or any response-cache surface outside this plan.

## Open Questions / Unresolved Items

- None. The two absent optional analysis companions are a named routing warning rather than an unresolved implementation decision.

## Python implementation contract (supplemental)

### Goal

- Implement a single stale-record reclamation behavior in the existing internal process-local store without changing the existing cache miss, TTL, policy, public API, or async-port contracts.

### Non-goals

- No TTL/freshness-policy contract, expiry arithmetic, write timestamp, or read-renewal change.
- No capacity/admission/eviction policy, background sweep, public invalidation/deletion/clear, persistence, settings, metrics, tracing, or orchestrator work.
- No public package export, port/signature, dependency, async resource lifecycle, lock, retry, timeout, cancellation, version, release, or migration change.

### Current Context

- `src/async_model_gateway/response_cache/_in_memory_store.py` keeps `_StoredResponseCacheEntry` records in a dictionary. Its async `get(...)` retrieves a record, delegates freshness to injected `FreshnessPolicy`, returns `None` for a `False` result, and otherwise returns the entry; it currently retains the stale record.
- `src/async_model_gateway/response_cache/freshness_policy.py` owns the internal `is_fresh(*, written_at, now) -> bool` contract, while `ttl_freshness_policy.py` owns positive TTL and strict-expiry semantics. Both are ReadOnly.
- `tests/response_cache/test_in_memory_store.py` already verifies the unchanged async-port shape, fresh hit, non-renewing writes, stale miss, overwrite, and key isolation. Package-surface and TTL/freshness regressions keep public exports and authority boundaries stable.

### Requirements

1. When an existing record's injected policy returns `False`, `get(...)` returns `None` and removes exactly the requested key from the internal store.
2. A second lookup of that reclaimed key returns `None` without another policy call; a later `set(...)` for that key creates a normally readable new record.
3. `True` preserves and returns the original entry. A policy exception propagates unchanged and preserves the existing record for a later lookup.
4. A stale key's reclamation cannot remove or change another key's fresh record; existing timestamp-on-write, non-renewal, and overwrite semantics remain unchanged.
5. Public API, `ResponseCacheStore` async signatures, package exports, freshness/TTL authority, dependencies, version metadata, and settings boundary remain unchanged.

### Decisions

- Async-planning status: exempt — cite exemption evidence: this changes only synchronous dictionary state after the pre-existing async `ResponseCacheStore.get(...)` has already made its injected policy decision; it adds no await, async resource lifecycle, lock/concurrency policy, task/worker, external I/O, timeout, retry, cancellation owner, or sync-to-async conversion. Existing direct propagation of policy exceptions remains unchanged.
- Module/package placement: modify only `src/async_model_gateway/response_cache/_in_memory_store.py`, its focused `tests/response_cache/test_in_memory_store.py`, and the three declared documentation files.
- New public API: no — the concrete store remains internal and no public import, method, or argument is added.
- Interface changes: no — `ResponseCacheStore`, `ResponseCache`, entry, key, factory, freshness policy, TTL policy, and all root/ports exports retain their existing signatures and behavior ownership.
- Breaking changes allowed: no — existing callers continue to see the same fresh-hit and stale-`None` lookup surface.
- New dependencies: no — use the existing built-in dictionary behavior and installed dependencies only.
- Error handling strategy: only a boolean `False` causes removal and ordinary `None` miss. `True` returns the stored entry. Exceptions raised by `FreshnessPolicy.is_fresh(...)` are not caught, wrapped, converted to `None`, or followed by deletion.
- Typing strategy: preserve strict Python 3.10 types and current stored-record dataclass; add no `Any`, runtime protocol cast, callback, or clock abstraction.

### Public Contract / API Changes

- No public API changes. `ResponseCacheStore.get(*, key) -> ResponseCacheEntry | None`, `ResponseCacheStore.set(*, key, entry) -> None`, `ResponseCache`, and all package exports remain unchanged.
- The only internal behavior addition is that `InMemoryResponseCacheStore.get(...)` removes the looked-up dictionary record after the existing policy returns `False`.

### Affected Files / Modules

Likely affected files:
- `src/async_model_gateway/response_cache/_in_memory_store.py`
- `tests/response_cache/test_in_memory_store.py`
- `README.md`
- `docs/architecture.md`
- `docs/specs/response-cache-boundary.md`

Candidate files to inspect:
- `src/async_model_gateway/response_cache/freshness_policy.py`
- `src/async_model_gateway/response_cache/ttl_freshness_policy.py`
- `src/async_model_gateway/response_cache/ports/store.py`
- `src/async_model_gateway/response_cache/__init__.py`
- `src/async_model_gateway/response_cache/ports/__init__.py`
- `tests/response_cache/test_response_cache_package_surface.py`
- `tests/response_cache/test_response_cache_freshness_policy.py`
- `tests/response_cache/test_ttl_freshness_policy.py`
- `docs/settings-policy.md`

### Implementation Steps

1. In `tests/response_cache/test_in_memory_store.py`, add direct-import RED tests for `False`-driven single-key reclamation, no second policy call after reclamation, same-key reinsertion, other-key isolation, and policy-exception propagation with record preservation; write the matching `*.red-tests.yaml` evidence before source changes.
2. In `src/async_model_gateway/response_cache/_in_memory_store.py`, delete only the requested dictionary key after the existing policy returns `False`, then retain the existing `None` miss; do not change the policy call, `True` path, timestamps, method signatures, or exception flow.
3. In `README.md`, `docs/architecture.md`, and `docs/specs/response-cache-boundary.md`, make the smallest wording adjustment that accurately states lookup-time stale-record reclamation and retains all existing exclusions.
4. Run the declared focused/full test, lint, type, and pre-commit commands; update the step tracker with completed creator work and leave reviewer/human evidence paths to their owners.

### Test Plan

Test file: `tests/response_cache/test_in_memory_store.py`

Test cases:
- Happy path: a stored entry remains readable when policy returns `True`; a same-key replacement remains readable after a new write.
- Invalid input / dependency failure: policy raises an exception; the exception propagates and a later fresh decision can still return the stored entry.
- Edge case: a `False` result returns `None`, reclaims the record, and a second lookup neither returns content nor calls the policy; reinsertion restores normal lookup.
- Regression: existing timestamp-on-write, no-read-renewal, overwrite, missing-key, and TTL/freshness tests pass unchanged.
- Backward compatibility: package-surface, port, key, entry, cache facade, and settings-boundary regressions confirm no public contract or export drift.

### Validation Commands

```text
uv run pytest tests/response_cache/test_in_memory_store.py -v --no-cov
uv run pytest
uv run ruff check README.md docs src tests plan/response-cache-expired-record-reclamation
uv run pyright
uv run pre-commit run --all-files
```

### Risks

- Deleting before the policy call or in an exception handler would incorrectly discard a record when freshness could not be decided.
- Treating all misses as reclamation could delete an absent/fresh record or make stale cleanup look like a general eviction policy.
- Touching public exports, freshness/TTL code, or adding synchronization would widen the bounded internal behavior and break the frozen contract.

### Rollback Plan

- Revert `src/async_model_gateway/response_cache/_in_memory_store.py`, `tests/response_cache/test_in_memory_store.py`, `README.md`, `docs/architecture.md`, and `docs/specs/response-cache-boundary.md`, together with this topic's evidence artifacts as appropriate. No migration, persisted data cleanup, version rollback, or release rollback is needed because records are process-local and no release workflow runs.

### Open Questions

- None.
