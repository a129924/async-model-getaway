Analysis-layer routing: incomplete optional-analysis mode. Semantic warning: neither `analysis/response-cache-explicit-key-invalidation/requirements.md` nor `analysis/response-cache-explicit-key-invalidation/technical-spec.md` exists. This plan uses the user-supplied locked decisions, the inspected response-cache boundary, and the merged `origin/dev` reclamation baseline as its provisional execution baseline; it does not claim strict analysis mode. The missing optional analysis layer does not block independent plan review. If either companion is added or conflicts with this plan before implementation, return to `spec-and-plan-finalization`.

# response-cache-explicit-key-invalidation

## Goal / Outcome

- Add one bounded public invalidation operation: `ResponseCache.invalidate(*, key: ResponseCacheKey) -> bool`, delegated directly through the existing submodule-public store port to the internal process-local store.
- On completion, invalidating a fresh record removes it and returns `True`; an absent record, a record already removed by a prior invalidation, an already reclaimed record, or a policy-confirmed stale record returns `False`, with stale records reclaimed first and all policy, cancellation, and store failures left visible.

## Scope

- **In scope**:
  - Add `async def invalidate(self, *, key: ResponseCacheKey) -> bool` to `ResponseCache` and `ResponseCacheStore`, without changing either package export surface.
  - Implement key-specific invalidation in internal `InMemoryResponseCacheStore`, reusing the existing injected `FreshnessPolicy` and the merged lookup-time stale-record reclamation semantics.
  - Add one private `_CacheLookupDecision(str, Enum)` with `HIT` and `MISS` only inside the process-local in-memory lookup implementation: `match` maps `HIT` to the current fresh entry and `MISS` to `None` for an absent record or completed stale reclamation.
  - Add direct-import RED and regression coverage in the declared response-cache test files, including four separate private-lookup cases (fresh `HIT`, absent `MISS` without policy access, stale-reclaimed `MISS`, and failure propagation); keep direct-import/no-dynamic-loading governance as a separate check, then align the two existing response-cache documentation boundaries with this narrow explicit-key API.
  - Create this topic's plan, behavior specification, and step tracker; declare later reviewer, human, RED-test, and implementation-review evidence paths without pre-filling them.

- **Out of scope**:
  - New lookup result enums, hit/miss APIs, or a change to `ResponseCache.get(...) -> ResponseCacheEntry | None`.
  - Exposing `_CacheLookupDecision` through `ResponseCache`, `ResponseCacheStore`, a port signature, any export, or public documentation API.
  - Cache identity, TTL/freshness arithmetic, features, payload hashing, entries, `clear`, prefix/namespace/batch invalidation, persistence, capacity/eviction, or background sweeping.
  - Locks, tasks, resource lifecycle, timeout, retry, cancellation wrappers, orchestration wiring, provider/model integration, dependencies, versioning, release, or migration work.

### Executable file inventory

| Classification | Exact paths | Contract |
| --- | --- | --- |
| Written now | `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.plan.md`; `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.spec.md`; `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.step.md` | Planning actor creates only these planning artifacts in this pass. |
| Planned Modify | `src/async_model_gateway/response_cache/cache.py`; `src/async_model_gateway/response_cache/ports/store.py`; `src/async_model_gateway/response_cache/_in_memory_store.py`; `tests/response_cache/test_cache.py`; `tests/response_cache/test_in_memory_store.py`; `tests/response_cache/test_response_cache_package_surface.py`; `docs/architecture.md`; `docs/specs/response-cache-boundary.md` | Tester, Implementer, and document owner may change only these future implementation paths after both plan-review and human-check gates clear. |
| Planned future gate artifacts | `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.plan-review.json`; `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.human-check.json`; `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.red-tests.yaml`; `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.implementation-review.yaml` | Reviewer, Human, Tester, and independent Reviewer respectively create their own evidence at the required gate; the planning actor does not prefill it. |
| ReadOnly / preserve-and-validate | `README.md`; `pyproject.toml`; `uv.lock`; `src/async_model_gateway/__version__.py`; `src/async_model_gateway/response_cache/__init__.py`; `src/async_model_gateway/response_cache/entry.py`; `src/async_model_gateway/response_cache/key.py`; `src/async_model_gateway/response_cache/key_factory.py`; `src/async_model_gateway/response_cache/freshness_policy.py`; `src/async_model_gateway/response_cache/ttl_freshness_policy.py`; `src/async_model_gateway/response_cache/ports/__init__.py`; `src/async_model_gateway/response_cache/ports/feature_hasher.py`; `tests/response_cache/test_entry.py`; `tests/response_cache/test_key.py`; `tests/response_cache/test_key_factory.py`; `tests/response_cache/test_response_cache_freshness_policy.py`; `tests/response_cache/test_ttl_freshness_policy.py`; `docs/settings-policy.md` | Existing exports, identity, entry, freshness/TTL authority, stable summary, settings exclusion, version metadata, and regressions remain unchanged. |
| Deleted | None | This topic deletes no repository file. Runtime deletion is limited to a single process-local record after the required decision path. |
| Out-of-scope / no path authorization | No additional repository paths | Any need for another source, test, documentation, policy, public API, lifecycle, persistence, orchestration, or release path is scope drift and returns to planning. |

## Locked Decisions

- D1 verdict: `non-trivial` — the topic adds a public async facade method, extends the submodule-public async port, changes internal state behavior, touches three production modules and three test modules, updates boundary documentation, and requires the Python workflow gates.
- The merged `origin/dev` reclamation baseline is authoritative: lookup already removes a record only after `FreshnessPolicy.is_fresh(...)` returns `False`; explicit invalidation must preserve that behavior rather than introduce a second freshness authority.
- Public `ResponseCache` gains exactly `async def invalidate(self, *, key: ResponseCacheKey) -> bool`. It only direct-awaits `store.invalidate(key=key)` and returns that boolean unchanged.
- `ResponseCacheStore` gains the same keyword-only signature, and remains public only from `async_model_gateway.response_cache.ports.store`. `async_model_gateway.response_cache`, `async_model_gateway.response_cache.ports`, and every other export remain unchanged.
- `InMemoryResponseCacheStore.invalidate(...)` first looks up the key. An absent record returns `False` without calling policy. A fresh (`True`) policy decision removes exactly that key and returns `True`. A stale (`False`) decision removes exactly that key using the existing reclamation semantics and returns `False`.
- A policy exception or cancellation is not a boolean result: it propagates unchanged and preserves the record. `ResponseCache` does not catch, wrap, translate, retry, or otherwise alter errors or cancellation raised by its store.
- `get(...)` remains `ResponseCacheEntry | None`; no enum, hit/miss object, or lookup behavior change is allowed. Key construction, feature handling, payload identity, TTL, entry shape, and all existing `get` / `set` signatures remain unchanged.
- The sole lookup-internal exception is private `_CacheLookupDecision(str, Enum)` with `HIT` and `MISS` in `_in_memory_store.py`: lookup uses `match` to return the unchanged fresh entry for `HIT` and `None` for `MISS`; absent and policy-confirmed stale reclamation are `MISS`, while policy exception, cancellation, and every unexpected error propagate unchanged and never become `MISS`. It is not a facade, store-port, export, or public-documentation API.
- This topic adopts the Python planning extension: behavior spec, step tracker, Tester-owned RED evidence, and independent implementation-review evidence are mandatory before PR routing. RED test authoring is the first `implement-plan` subphase.
- This is a non-stable-library topic with no version or release intent. `## Stable library metadata` is intentionally omitted because `README.md`, version metadata, and release surfaces are ReadOnly and no stable-library timing is declared.

## Boundaries / Exclusions

- The planning actor writes only the three Written-now artifacts. It does not implement source, tests, documentation, reviewer verdicts, human gates, commits, pushes, or PRs.
- Tester must use normal direct imports in all declared `tests/response_cache/` files. Dynamic module loading is prohibited and no exception is authorized.
- Implementer may modify only Planned Modify paths after the independent plan-review and human-check gates clear. A need to alter `__init__.py`, identity/freshness files, a public export, or any unlisted path returns to `spec-and-plan-finalization`.
- Reviewer independently creates the plan-review and implementation-review artifacts. Human independently creates the human-check evidence and controls human merge. Neither role completes creator-owned implementation steps.
- Explicit key invalidation is not a general deletion or eviction policy. It does not decide proactive reclamation, multi-key selection, capacity, races, synchronization, retention, or persistence semantics.

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Plan-authoring completeness**: `INCOMPLETE` only for the explicitly absent optional analysis companions named in the routing warning; the executable scope, paths, contracts, and async baseline are frozen for independent review.
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

- `approved` requires both a Reviewer-owned `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.plan-review.json` with verdict `approved` and a Human-owned `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.human-check.json` with explicit clearance. Conversational approval does not replace either repo-visible gate.
- This revision invalidates the existing plan-review verdict for gate purposes without modifying `response-cache-explicit-key-invalidation.plan-review.json`; a Reviewer must re-review this exact revised plan and replace that artifact with a fresh independent verdict before any human-check or implementation routing.
- After both gates clear, Tester writes direct-import RED tests and `*.red-tests.yaml` before production source changes. An independent Reviewer must then write `*.implementation-review.yaml` before the topic advances to `pr-comment`.
- If review asks for altered identity, TTL/freshness authority, broader invalidation/deletion, locks, background work, lifecycle, error translation, an export change, or an unlisted path, classify it as scope/contract drift and return to `spec-and-plan-finalization`.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Absent requirements companion | `analysis/response-cache-explicit-key-invalidation/requirements.md` | Analysis producer | Optional business-intent guardrail; absent at plan authoring and not created in this topic pass. |
| Absent technical-spec companion | `analysis/response-cache-explicit-key-invalidation/technical-spec.md` | Analysis producer | Optional execution source; absent at plan authoring and not created in this topic pass. |
| Topic plan | `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.plan.md` | Planning actor | Canonical workflow contract plus supplemental Python implementation contract. |
| Topic behavior spec | `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.spec.md` | Planning actor | Required non-trivial behavioral contract for RED tests and review. |
| Topic step tracker | `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.step.md` | Planning actor -> Implementer | Initialized workflow/progress record; Implementer updates implementation completion only. |
| Plan review | `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.plan-review.json` | Reviewer | Single-object independent planning verdict. |
| Human check | `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.human-check.json` | Human | Explicit repo-visible clearance before RED tests and implementation. |
| RED-test evidence | `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.red-tests.yaml` | Tester | Evidence that direct-import tests failed before production behavior was changed. |
| Implementation review | `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.implementation-review.yaml` | Independent Reviewer | Plan-conformance evidence required before PR routing. |
| Response-cache facade | `src/async_model_gateway/response_cache/cache.py` | Implementer | Add only direct delegation for the public explicit-key invalidation method. |
| Response-cache store port | `src/async_model_gateway/response_cache/ports/store.py` | Implementer | Add only the matching abstract async explicit-key invalidation method. |
| Internal process-local store | `src/async_model_gateway/response_cache/_in_memory_store.py` | Implementer | Implement fresh-key removal, stale reclamation with `False`, propagation-preserving failure behavior, and the private lookup decision. |
| Facade tests | `tests/response_cache/test_cache.py` | Tester | Direct-import coverage for facade signature, direct delegation, boolean preservation, and store failure/cancellation propagation. |
| Store tests | `tests/response_cache/test_in_memory_store.py` | Tester | Direct-import coverage for fresh, absent, stale, exception/cancellation, and key-local explicit invalidation behavior, plus four separate private lookup cases: fresh `HIT`, absent `MISS` without policy access, stale-reclaimed `MISS`, and failure propagation. |
| Package/port surface tests | `tests/response_cache/test_response_cache_package_surface.py` | Tester | Verify the store submodule exposes the new async method while all root/ports export policy remains unchanged. |
| Architecture summary | `docs/architecture.md` | Implementer | Narrowly state that the operational owner supports explicit-key invalidation without broader cache wiring. |
| Response-cache boundary spec | `docs/specs/response-cache-boundary.md` | Implementer | Replace the obsolete blanket invalidation exclusion with the exact key-only contract and retain every broader exclusion. |
| Validation configuration | `pyproject.toml`; `uv.lock`; `src/async_model_gateway/__version__.py` | Reviewer | ReadOnly validation and no-version-bump evidence. |

Artifact path notes:

- This topic does not modify `README.md`, `VERSION`, `.github/copilot-instructions.md`, or package-root / ports-root export files.
- The table is exhaustive. Work outside it is plan drift and must return to planning before change.

## Implementation Steps

1. In `tests/response_cache/test_cache.py`, `tests/response_cache/test_in_memory_store.py`, and `tests/response_cache/test_response_cache_package_surface.py`, author direct-import RED tests and record `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.red-tests.yaml`: lock the facade and port signatures, direct boolean delegation, fresh/absent/stale outcomes, stale reclamation, key locality, policy exception/cancellation record preservation, unchanged exports, and four separate private-lookup tests—fresh `HIT` preserves `ResponseCacheEntry | None`; absent is `MISS` without policy access; stale reclamation is `MISS`; and policy exception, cancellation, or unexpected failure propagates rather than becoming `MISS`. Separately verify ordinary direct imports and no dynamic module loading before production source changes.
2. In `src/async_model_gateway/response_cache/ports/store.py`, add only `async def invalidate(self, *, key: ResponseCacheKey) -> bool` to `ResponseCacheStore`, keeping the class submodule-public and preserving existing `get` / `set` signatures and all export boundaries.
3. In `src/async_model_gateway/response_cache/cache.py`, add `ResponseCache.invalidate(...)` as one direct await of `self._store.invalidate(key=key)`, returning its boolean unchanged and adding no fallback, exception handling, retry, timeout, lock, task, or lifecycle behavior.
4. In `src/async_model_gateway/response_cache/_in_memory_store.py`, implement `InMemoryResponseCacheStore.invalidate(...)`: return `False` without policy access for absent records; call the injected policy for an existing record; remove exactly that key and return `True` for fresh, remove exactly that key and return `False` for stale, and let policy exceptions or cancellation escape before any removal.
5. In `docs/architecture.md` and `docs/specs/response-cache-boundary.md`, make the smallest wording changes that document only explicit-key invalidation, retain `get(...) -> ResponseCacheEntry | None`, and preserve exclusions for `clear`, prefix/namespace/batch operations, broader deletion/eviction, persistence, background work, settings, and orchestration.
6. In `src/async_model_gateway/response_cache/_in_memory_store.py`, keep lookup's public return type as `ResponseCacheEntry | None` while introducing only private `_CacheLookupDecision(str, Enum)` with `HIT` / `MISS`; use `match` to map a fresh `HIT` to the existing entry and absent or policy-confirmed stale reclamation `MISS` to `None`, without converting policy exception, cancellation, or unexpected errors into `MISS` or changing any facade, port, export, or public-documentation API.
7. After Steps 1-6, run `uv run pytest tests/response_cache/test_cache.py tests/response_cache/test_in_memory_store.py tests/response_cache/test_response_cache_package_surface.py -v --no-cov`, `uv run pytest`, `uv run ruff check docs src tests plan/response-cache-explicit-key-invalidation`, `uv run pyright`, and `uv run pre-commit run --all-files`; these final checks cover the private lookup-decision implementation and preserved invalidation contract. Then update only creator-owned completion state in `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.step.md` and submit for independent implementation review.

## Validation / Acceptance Checks

- The plan retains canonical section order, exact path inventory, canonical transitions, non-release intent, and a single JSON reviewer-handoff contract.
- The behavior spec and RED evidence cover all fresh, absent, stale, failure/cancellation, key-local, facade, and port behavior before production changes.
- `ResponseCache.invalidate(*, key)` and `ResponseCacheStore.invalidate(*, key)` are async, keyword-only, fully typed, and direct-delegated; `ResponseCacheStore` remains submodule-public only, and all package/ports exports are unchanged.
- In-memory invalidation returns `True` only for a fresh existing record that it removes. It returns `False` for an absent record without consulting policy, and for a policy-confirmed stale record after reclaiming it.
- Policy exception or cancellation propagates unchanged and preserves the record. Facade store errors and cancellation propagate unchanged. No tests use dynamic module loading.
- Existing lookup stale-reclamation, write timestamps, non-renewal, overwrite, `get(...) -> ResponseCacheEntry | None`, entry/key/hash/feature behavior, and TTL freshness authority remain valid; private lookup tests independently cover fresh `HIT`, absent `MISS` without policy access, stale-reclaimed `MISS`, and failure propagation, while direct-import/no-dynamic-loading governance remains separate.
- Focused pytest, full pytest, Ruff, Pyright strict, and pre-commit pass; independent implementation review verifies artifact-path confinement and no unplanned async mechanism.

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
- After merge, do not change `README.md`, version metadata, `uv.lock`, release notes, tags, publication state, or any response-cache surface outside this plan.

## Open Questions / Unresolved Items

- None. The two absent optional analysis companions are a named routing warning rather than an unresolved implementation decision.

## Python implementation contract (supplemental)

### Goal

- Implement one explicit-key response-cache invalidation method that distinguishes fresh removal from absent or stale reclamation without changing the existing lookup, identity, TTL, or broader cache contract.

### Non-goals

- No new lookup enum or hit/miss API; `get(...)` remains `ResponseCacheEntry | None`.
- No public lookup enum or hit/miss API: `_CacheLookupDecision` is the sole private in-memory implementation detail and remains absent from `ResponseCache`, `ResponseCacheStore`, port signatures, exports, and public documentation APIs.
- No identity, TTL, freshness-policy, features, payload, entry, `clear`, prefix/namespace/batch, persistence, eviction, background, lock, task, lifecycle, timeout, retry, or orchestrator change.
- No root/ports export change, dependency, version, stable-library, release, migration, or dynamic test-module loading.

### Current Context

- `ResponseCache` currently direct-awaits the caller-provided `ResponseCacheStore` for async `get(...)` and `set(...)`; `ResponseCacheStore` is submodule-public only from `response_cache.ports.store`.
- `InMemoryResponseCacheStore.get(...)` already uses the injected synchronous `FreshnessPolicy` and reclaims a confirmed stale record before returning `None`, as merged on `origin/dev`.
- `tests/response_cache/test_cache.py`, `tests/response_cache/test_in_memory_store.py`, and `tests/response_cache/test_response_cache_package_surface.py` directly test the existing facade, internal store, and port/export boundary.

### Requirements

1. `ResponseCache.invalidate(*, key: ResponseCacheKey) -> bool` and `ResponseCacheStore.invalidate(*, key: ResponseCacheKey) -> bool` are the only new public method contracts; the port remains submodule-public only.
2. Facade invalidation performs one direct await, passes the original key unchanged, returns the store boolean unchanged, and propagates store errors and cancellation unchanged.
3. In-memory invalidation returns `True` and removes exactly one key only after its injected policy says the existing record is fresh.
4. In-memory invalidation returns `False` for absent records without policy access and for stale records after reclaiming them; neither path exposes stale content.
5. Policy exception or cancellation propagates and preserves the record. Existing get/set, identity, TTL, export, and documentation exclusions remain unchanged except for the exact new method wording.
6. Only `src/async_model_gateway/response_cache/_in_memory_store.py` may use private `_CacheLookupDecision(str, Enum)` with `HIT` and `MISS`; a `match` returns the fresh existing entry for `HIT` and `None` for absent or policy-confirmed stale reclamation `MISS`, while policy exception, cancellation, and unexpected errors propagate rather than becoming `MISS`. The enum is prohibited from the facade, port, exports, and public documentation APIs.

### Decisions

- Async-planning status: triggered — cite trigger evidence: this topic introduces a public async facade method and matching async store-port method, so the direct-await boundary, resource ownership, failure propagation, and cancellation/timeout policy must be frozen before implementation.
- Module/package placement: modify only `src/async_model_gateway/response_cache/cache.py`, `ports/store.py`, and `_in_memory_store.py`; use the three declared direct-import test modules and two declared response-cache documentation files.
- New public API: yes — `async def ResponseCache.invalidate(self, *, key: ResponseCacheKey) -> bool`; the matching `ResponseCacheStore.invalidate(...)` is public only from `async_model_gateway.response_cache.ports.store`.
- Interface changes: yes — add the same keyword-only async method to `ResponseCacheStore`; `ResponseCache` is already root-public, and root/ports exports otherwise remain unchanged.
- Breaking changes allowed: no — existing signatures and surfaces persist; implementers of the abstract store port must add the new method as the deliberately bounded interface extension.
- New dependencies: no — reuse the existing store, key, and injected freshness-policy contracts.
- Error handling strategy: boolean results represent only successful invalidation decisions. Absent and policy-confirmed stale records return `False`; fresh removal returns `True`; policy exceptions/cancellation and facade store errors/cancellation are neither caught nor translated, and a policy failure must preserve the record.
- Typing strategy: use strict Python 3.10 annotations, the existing `ResponseCacheKey`, `ResponseCacheEntry`, and abstract port types; add no `Any`, union expansion, cast, or new protocol. The sole enum allowance is private `_CacheLookupDecision(str, Enum)` in `src/async_model_gateway/response_cache/_in_memory_store.py`; it is prohibited from the facade, port, exports, and public documentation APIs.
- Lookup-internal representation: permit only `_CacheLookupDecision(str, Enum)` with `HIT` / `MISS` in `_in_memory_store.py`; it does not alter `ResponseCacheEntry | None`, does not cross the `ResponseCache` / `ResponseCacheStore` boundary, and is not exported or documented as public API.

### Async boundary decision

- `ResponseCache.invalidate(...)` and `ResponseCacheStore.invalidate(...)` are async because they extend the existing async cache/store boundary. Freshness-policy evaluation and dictionary mutation remain synchronous internal operations inside the already-running store coroutine.

### Resource lifecycle decision

- `ResponseCache` continues to hold only the caller-provided store reference. It creates, shares, closes, resets, flushes, or owns no resources; `InMemoryResponseCacheStore` adds no resource or lifecycle surface.

### Concurrency model

- The facade makes exactly one direct await to the store. No fan-out, batching, queue, background task, lock, semaphore, or cross-key coordination is introduced; dictionary removal is limited to the supplied key after its required policy result.

### Failure model

- The facade returns the store's `bool` unchanged. It propagates store errors and `CancelledError` unchanged. The internal store propagates a policy exception or cancellation unchanged before deletion; only completed `True` or `False` policy results authorize the specified key-local outcome.
- Lookup converts only absent and completed policy-confirmed stale reclamation into private `MISS`; policy exception, cancellation, and unexpected errors remain failures and do not produce a `MISS` result.

### Cancellation / timeout policy

- No timeout, retry, cancellation wrapper, shield, cleanup handler, or cancellation owner is added. Caller/runtime and store awaitable semantics remain authoritative; policy-raised cancellation is preserved like every other unhandled policy failure.

### Validation plan

- RED tests prove the exact signature and each boolean/error outcome before source changes. Focused tests cover direct delegation and in-memory paths, plus four separately named lookup cases: fresh `HIT` preservation of `ResponseCacheEntry | None`, absent `MISS` without policy access, stale-reclaimed `MISS`, and failure propagation rather than `MISS`. Separately, tests retain ordinary direct imports with no dynamic module loading; then full pytest, Ruff, Pyright, and pre-commit validate regressions. Independent implementation review checks no async mechanism or unlisted path was added.

### Handoff notes for the implementer

- Do not add invalidation to package `__all__`: the existing public `ResponseCache` already owns the method, while `ResponseCacheStore` stays importable only from its store submodule. Do not convert stale invalidation into a `True` deletion result, swallow policy failures, or add locks/background cleanup. Return to planning for any broader invalidation, identity, TTL, or lifecycle request.
- Keep `_CacheLookupDecision` private to the in-memory lookup and use `match` only to map `HIT` to the current fresh entry and `MISS` to `None`. Never catch policy exception, cancellation, or unexpected errors as `MISS`, and never expose the enum through a facade, port, export, or public documentation API.

### Public Contract / API Changes

- `async_model_gateway.response_cache.ResponseCache`
  - New method: `async def invalidate(self, *, key: ResponseCacheKey) -> bool`
  - Returns `True` only when its store successfully invalidates a fresh existing record; returns `False` for absent or reclaimed-stale outcomes supplied by the store.
  - Directly delegates the original key and propagates errors/cancellation unchanged. Existing `get` and `set` signatures and behavior remain unchanged.
- `async_model_gateway.response_cache.ports.store.ResponseCacheStore`
  - New abstract method: `async def invalidate(self, *, key: ResponseCacheKey) -> bool`
  - Remains submodule-public only; neither response-cache package root re-exports it.
- Backward compatibility: no existing API is removed or reshaped. The abstract-port extension is the only required implementation change for concrete stores.

### Affected Files / Modules

Likely affected files:
- `src/async_model_gateway/response_cache/cache.py`
- `src/async_model_gateway/response_cache/ports/store.py`
- `src/async_model_gateway/response_cache/_in_memory_store.py`
- `tests/response_cache/test_cache.py`
- `tests/response_cache/test_in_memory_store.py`
- `tests/response_cache/test_response_cache_package_surface.py`
- `docs/architecture.md`
- `docs/specs/response-cache-boundary.md`

Candidate files to inspect:
- `src/async_model_gateway/response_cache/__init__.py`
- `src/async_model_gateway/response_cache/ports/__init__.py`
- `src/async_model_gateway/response_cache/freshness_policy.py`
- `src/async_model_gateway/response_cache/ttl_freshness_policy.py`
- `tests/response_cache/test_ttl_freshness_policy.py`
- `tests/response_cache/test_response_cache_freshness_policy.py`
- `README.md`
- `pyproject.toml`

### Implementation Steps

1. In `tests/response_cache/test_cache.py`, `tests/response_cache/test_in_memory_store.py`, and `tests/response_cache/test_response_cache_package_surface.py`, write direct-import RED tests for the exact public/port signatures, direct facade delegation, fresh/absent/stale returns, stale reclamation, exception/cancellation preservation, key locality, unchanged exports, and four separate private lookup cases: fresh `HIT` preservation of `ResponseCacheEntry | None`, absent `MISS` without policy access, stale-reclaimed `MISS`, and policy exception, cancellation, or unexpected failure propagation rather than `MISS`. Separately retain ordinary direct imports with no dynamic module loading; record the mapping in `plan/response-cache-explicit-key-invalidation/response-cache-explicit-key-invalidation.red-tests.yaml` before source changes.
2. In `src/async_model_gateway/response_cache/ports/store.py`, add the one abstract keyword-only async `invalidate(...) -> bool` method and preserve submodule-only exposure plus existing get/set contracts.
3. In `src/async_model_gateway/response_cache/cache.py`, add the one direct-await facade method with no error handling or additional async behavior.
4. In `src/async_model_gateway/response_cache/_in_memory_store.py`, add explicit-key invalidation using the existing policy and key dictionary: absent returns `False`; `True` removes and returns `True`; `False` reclaims and returns `False`; exceptions/cancellation leave the record untouched and propagate.
5. In `docs/architecture.md` and `docs/specs/response-cache-boundary.md`, align only the narrow public explicit-key invalidation wording and retain all broader exclusions.
6. In `src/async_model_gateway/response_cache/_in_memory_store.py`, add only private `_CacheLookupDecision(str, Enum)` with `HIT` / `MISS` to lookup and use `match` so `HIT` returns the fresh existing entry and `MISS` returns `None` for absent or policy-confirmed stale reclamation; do not translate policy exception, cancellation, or unexpected errors to `MISS`, and do not alter any facade, port, export, or public-documentation API.
7. After Steps 1-6, run the declared focused/full test, lint, type, and pre-commit commands so the final evidence covers the private lookup-decision implementation and preserved invalidation contract; update the step tracker with completed creator work and leave reviewer/human evidence artifacts to their owners.

### Test Plan

Test files:
- `tests/response_cache/test_cache.py`
- `tests/response_cache/test_in_memory_store.py`
- `tests/response_cache/test_response_cache_package_surface.py`

Test cases:
- Happy path: the facade delegates an unchanged key to a store returning `True`; an internal fresh record is removed and returns `True`.
- Invalid input / dependency failure: a store error and policy exception/cancellation propagate unchanged; the policy failure leaves its record available for a later fresh decision.
- Edge case: an absent key returns `False` without policy access; a fresh-invalidated key and a stale-reclaimed key each return `False` on a repeat invalidation without another policy call.
- Regression: existing lookup stale reclamation, no-read-renewal, timestamp-on-write, overwrite, entry/key/factory, TTL, and get/set delegation tests remain green.
- Backward compatibility: package-root and ports-root exports stay unchanged; `ResponseCacheStore` exposes the new method only from `response_cache.ports.store`, and tests use no dynamic module loading.
- Lookup decision coverage: test fresh `HIT` preserves the public `ResponseCacheEntry | None` lookup contract; test absent `MISS` occurs without policy access; test a policy-confirmed stale record is reclaimed and becomes `MISS`; and test policy exception, cancellation, and unexpected errors propagate rather than becoming `MISS`.
- Direct-import governance: separately verify ordinary direct imports and no dynamic module loading.

### Validation Commands

```text
uv run pytest tests/response_cache/test_cache.py tests/response_cache/test_in_memory_store.py tests/response_cache/test_response_cache_package_surface.py -v --no-cov
uv run pytest
uv run ruff check docs src tests plan/response-cache-explicit-key-invalidation
uv run pyright
uv run pre-commit run --all-files
```

### Risks

- Returning `True` for a stale record after reclamation would conflate stale cleanup with successful explicit invalidation and violate the frozen boolean contract.
- Removing a record before a policy outcome, or in an exception/cancellation path, would discard cache data when freshness could not be decided.
- Re-exporting the port or adding lock/background behavior would widen the public or async boundary beyond the approved paths.

### Rollback Plan

- Revert `src/async_model_gateway/response_cache/cache.py`, `src/async_model_gateway/response_cache/ports/store.py`, `src/async_model_gateway/response_cache/_in_memory_store.py`, the three declared test files, and the two declared documentation files, together with this topic's evidence artifacts as appropriate. No persisted-data, migration, version, or release rollback is required because storage remains process-local and no release workflow runs.

### Open Questions

- None.
