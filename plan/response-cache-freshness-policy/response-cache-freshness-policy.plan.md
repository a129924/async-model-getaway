Analysis-layer routing: incomplete optional-analysis mode. Semantic warning: neither `analysis/response-cache-freshness-policy/requirements.md` nor `analysis/response-cache-freshness-policy/technical-spec.md` exists. This plan therefore uses the user-supplied locked decisions and the inspected repository boundary as its provisional execution baseline; it does not claim strict analysis mode. If either analysis artifact is added or conflicts with this baseline before implementation, return to `spec-and-plan-finalization`.

# response-cache-freshness-policy

## Goal / Outcome

- Add a bounded internal freshness policy and process-local response-cache store implementation that makes a cached response a hit only while its injected positive TTL has not expired, without changing the existing public response-cache boundary.
- On completion, successful writes have an internal aware-UTC write time, reads never renew that time, and an expired entry is an ordinary cache miss rather than a stale response.

## Scope

- **In scope**:
  - Internal `FreshnessPolicy` and injected `TtlFreshnessPolicy` under `src/async_model_gateway/response_cache/`, plus an internal in-memory implementation of the existing `ResponseCacheStore` port.
  - Focused freshness, TTL, private-store, and package-surface tests under `tests/response_cache/`.
  - Minimal documentation alignment in `README.md`, `docs/architecture.md`, `docs/settings-policy.md`, and `docs/specs/response-cache-boundary.md`.
  - This topic's plan, non-trivial behavior specification, step tracker, and later gate-evidence paths.

- **Out of scope**:
  - Capacity, admission, eviction, invalidation, deletion, persistence, serialization, metrics, tracing, and any future `CapacityPolicy` or `EvictionPolicy`.
  - Settings loading, environment variables, persistence configuration, orchestrator wiring, response-generation flow, and provider/model integration.
  - Changes to `ResponseCacheStore`, `ResponseCache`, `ResponseCacheEntry`, `ResponseCacheKey`, `ResponseCacheKeyFactory`, key/hash ownership, or package-root exports.
  - A public policy API, a public concrete-store API, release/version work, or a global cache-policy pipeline.

### Executable file inventory

| Classification | Exact paths | Contract |
| --- | --- | --- |
| Written now | `plan/response-cache-freshness-policy/response-cache-freshness-policy.plan.md`; `plan/response-cache-freshness-policy/response-cache-freshness-policy.step.md`; `plan/response-cache-freshness-policy/response-cache-freshness-policy.spec.md` | Planning actor creates only these repo-visible planning artifacts in this pass. |
| Historical completed implementation | `README.md`; `docs/architecture.md`; `docs/settings-policy.md`; `docs/specs/response-cache-boundary.md`; `src/async_model_gateway/response_cache/freshness_policy.py`; `src/async_model_gateway/response_cache/ttl_freshness_policy.py`; `src/async_model_gateway/response_cache/_in_memory_store.py`; `tests/response_cache/test_response_cache_package_surface.py`; `tests/response_cache/test_response_cache_freshness_policy.py`; `tests/response_cache/test_ttl_freshness_policy.py`; `tests/response_cache/test_in_memory_store.py`; `plan/response-cache-freshness-policy/response-cache-freshness-policy.step.md`; `plan/response-cache-freshness-policy/response-cache-freshness-policy.red-tests.yaml` | Completed under the prior cleared gate. Renewed plan-review and human-check validate only the historical RED-to-renamed-path traceability correction; they do not require repeating implementation, the test rename, or RED authoring. |
| Planned future gate artifacts | `plan/response-cache-freshness-policy/response-cache-freshness-policy.plan-review.json`; `plan/response-cache-freshness-policy/response-cache-freshness-policy.human-check.json`; `plan/response-cache-freshness-policy/response-cache-freshness-policy.implementation-review.yaml` | Reviewer or Human creates these only at its respective gate; this planning pass declares but does not prefill them. |
| ReadOnly / preserve-and-validate | `pyproject.toml`; `uv.lock`; `src/async_model_gateway/__version__.py`; `src/async_model_gateway/response_cache/__init__.py`; `src/async_model_gateway/response_cache/cache.py`; `src/async_model_gateway/response_cache/entry.py`; `src/async_model_gateway/response_cache/key.py`; `src/async_model_gateway/response_cache/key_factory.py`; `src/async_model_gateway/response_cache/ports/__init__.py`; `src/async_model_gateway/response_cache/ports/store.py`; `tests/response_cache/test_cache.py`; `tests/response_cache/test_entry.py`; `tests/response_cache/test_key.py`; `tests/response_cache/test_key_factory.py` | Existing public contract, version metadata, port, identity ownership, and regression coverage must remain unchanged. |
| Out-of-Scope / no path authorization | No additional repository paths | Implementation must not create or modify settings modules, orchestrator modules, provider/model paths, persistence/backends, capacity/eviction policy paths, or release metadata. |
| Deleted | None | This topic deletes no file or behavior. |

## Locked Decisions

- D1 verdict: `non-trivial` — the change adds three internal modules, an async-port implementation, a policy contract, focused tests, documentation alignment, and later Python workflow gates.
- `FreshnessPolicy` is internal-only and has exactly one contract: `is_fresh(*, written_at, now) -> bool`. It is not a general `CachePolicy`, has no list or pipeline API, and is neither package-root nor `ports` re-exported.
- `TtlFreshnessPolicy` is injected into the internal store. Its constructor accepts a `datetime.timedelta` TTL and rejects zero or negative durations with `ValueError`; freshness is true only when `now` is strictly before `written_at + ttl`.
- The store records an aware-UTC `written_at` only for a successful `set(...)`; a `get(...)` passes the original timestamp to the policy and never renews it. Equality at the TTL boundary is expired, and an expired existing record returns `None` without exposing stale content or introducing deletion/eviction behavior.
- The concrete class is internal as `InMemoryResponseCacheStore` in `src/async_model_gateway/response_cache/_in_memory_store.py`. It implements the existing `ResponseCacheStore` methods unchanged, receives `freshness_policy` by keyword-only injection, and is not re-exported from `async_model_gateway.response_cache` or `async_model_gateway.response_cache.ports`.
- The existing public `ResponseCacheStore` port, `ResponseCache` facade, entry contract, key/hash owners, and root `__all__` stay byte-for-contract unchanged. No new public API or dependency is allowed.
- This topic adopts the Python planning extension: `.spec.md`, `.step.md`, RED-test evidence, and implementation-review evidence are required before PR routing. RED test authoring is the first `implement-plan` subphase.
- Historical RED exception for this non-semantic test-path correction:
  `tests/response_cache/test_freshness_policy.py` completed RED collection
  before any production implementation existed. Its requirements are unchanged
  after the mechanical rename to
  `tests/response_cache/test_response_cache_freshness_policy.py`; therefore
  that predecessor-path RED evidence remains valid. The renamed path requires
  only an explicit old-to-new mapping plus focused and full GREEN validation.
  `new_red_evidence_created: false` is expected. Do not create or claim new
  RED evidence after production implementation exists.
- Stable-library metadata is required because `README.md` is a planned modify path. `project.version`, `src/async_model_gateway/__version__.py`, and `uv.lock` have an explicit no-bump decision; no release workflow is declared.

## Boundaries / Exclusions

- The planning actor writes only the three current planning artifacts. It does not edit production, tests, README, or documentation; it does not write reviewer verdicts or human gates.
- The implementer may edit only the future Planned Modify paths in the file inventory. Any need to alter a ReadOnly path, add a policy family, or introduce a new artifact path returns to `spec-and-plan-finalization`.
- The tester must not use dynamic module loading in `tests/`; direct imports of the declared internal modules are the only planned test-import route.
- The reviewer independently writes the plan-review and implementation-review artifacts; the human independently closes `human check` and `human merge`. Neither role implements the creator-owned steps.
- A freshness miss is a lookup result, not an eviction decision. Retention or deletion of expired internal records, capacity management, and race/concurrency policy are intentionally not specified by this topic.

## Status / Allowed Transitions

- **Current**: `publish-in-progress`
- **Re-review rework**: this is a non-semantic artifact-path correction. The planned new test path is now `tests/response_cache/test_response_cache_freshness_policy.py`, whose basename is unique; it replaces only the previously planned `tests/response_cache/test_freshness_policy.py` path because existing `tests/model_registry/test_freshness_policy.py` collides under the default pytest top-level module collection. Direct imports remain required; `pyproject.toml` and the existing model-registry test remain unchanged.
- **Plan-authoring completeness**: `INCOMPLETE` only for the explicitly absent optional analysis companions named in the routing warning; all executable paths and locked implementation decisions are otherwise frozen for independent review.
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

- `approved` requires the Reviewer-owned `plan/response-cache-freshness-policy/response-cache-freshness-policy.plan-review.json` with an `approved` verdict and the Human-owned `plan/response-cache-freshness-policy/response-cache-freshness-policy.human-check.json` before `implement-plan` begins.
- The existing `response-cache-freshness-policy.plan-review.json` and `response-cache-freshness-policy.human-check.json` record only the superseded test-path revision. They remain historical evidence and must not be edited by this rework, but cannot clear this revision; Reviewer and Human must regenerate their respective gate evidence after re-review.
- The absent analysis files are a semantic warning for the reviewer. If a reviewer determines they are required rather than optional, return to `creator-in-progress`; do not infer strict analysis mode.
- Historical completion: Tester already mechanically renamed
`tests/response_cache/test_freshness_policy.py` to
`tests/response_cache/test_response_cache_freshness_policy.py` under the
previous cleared gate, retained direct imports, and ran focused and full GREEN
validation. `response-cache-freshness-policy.red-tests.yaml` maps the old RED
evidence to the unchanged renamed-path requirements and records the later
GREEN validation. Renewed plan-review and human-check approve this
traceability interpretation only; they do not require repeating the rename or
creating post-implementation RED evidence.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Absent requirements companion | `analysis/response-cache-freshness-policy/requirements.md` | Analysis producer | Optional business-intent guardrail; absent at plan authoring and not created in this topic pass. |
| Absent technical-spec companion | `analysis/response-cache-freshness-policy/technical-spec.md` | Analysis producer | Optional execution source; absent at plan authoring and not created in this topic pass. |
| Topic plan | `plan/response-cache-freshness-policy/response-cache-freshness-policy.plan.md` | Planning actor | Canonical workflow contract plus the supplemental Python implementation contract. |
| Topic behavior spec | `plan/response-cache-freshness-policy/response-cache-freshness-policy.spec.md` | Planning actor | Required non-trivial behavioral contract for RED tests and review. |
| Topic step tracker | `plan/response-cache-freshness-policy/response-cache-freshness-policy.step.md` | Implementer | Repo-visible workflow-stage and implementation-progress record. |
| Plan review | `plan/response-cache-freshness-policy/response-cache-freshness-policy.plan-review.json` | Reviewer | Regenerated single-object planning verdict for this renamed-test-path revision; existing content is historical only. |
| Human check | `plan/response-cache-freshness-policy/response-cache-freshness-policy.human-check.json` | Human | Regenerated explicit repo-visible clearance for this revision after renewed plan approval; existing content is historical only. |
| RED-test evidence | `plan/response-cache-freshness-policy/response-cache-freshness-policy.red-tests.yaml` | Tester | Predecessor-path RED evidence captured before production implementation, explicit old-to-new test-path mapping, and renamed-path focused/full GREEN validation. `new_red_evidence_created: false` is expected; post-implementation RED evidence is prohibited. |
| Implementation review | `plan/response-cache-freshness-policy/response-cache-freshness-policy.implementation-review.yaml` | Reviewer | Plan-conformance evidence required before PR routing. |
| README summary | `README.md` | Implementer | Update only the current response-cache baseline wording to mention internal, injected TTL freshness; no new public API claim. |
| Architecture summary | `docs/architecture.md` | Implementer | Align response-cache responsibility wording with internal freshness decision and process-local storage. |
| Settings policy | `docs/settings-policy.md` | Implementer | Clarify this is developer-injected policy, not settings loading or an environment surface. |
| Response-cache boundary spec | `docs/specs/response-cache-boundary.md` | Implementer | Replace the now-obsolete “no concrete store/TTL” wording only to the bounded internal freshness/store extent. |
| Freshness protocol | `src/async_model_gateway/response_cache/freshness_policy.py` | Implementer | Internal typed policy contract with only `is_fresh(*, written_at, now) -> bool`. |
| TTL policy | `src/async_model_gateway/response_cache/ttl_freshness_policy.py` | Implementer | Positive-TTL implementation of the internal freshness contract. |
| Internal store | `src/async_model_gateway/response_cache/_in_memory_store.py` | Implementer | Process-local concrete `ResponseCacheStore` using injected freshness policy and internal write timestamps. |
| Package-surface tests | `tests/response_cache/test_response_cache_package_surface.py` | Tester | Preserve root/ports non-re-export guarantees for the policy and concrete store. |
| Policy tests | `tests/response_cache/test_response_cache_freshness_policy.py` | Tester | Unique-basename freshness-policy coverage; lock the sole policy signature and internal-only exposure constraints without colliding with `tests/model_registry/test_freshness_policy.py`. |
| TTL tests | `tests/response_cache/test_ttl_freshness_policy.py` | Tester | Cover positive TTL validation, before-boundary hit, exact-boundary miss, and post-boundary miss. |
| Store tests | `tests/response_cache/test_in_memory_store.py` | Tester | Cover timestamp-on-write, no read renewal, hit/miss, overwrite, and never-stale behavior. |
| Existing cache regressions | `tests/response_cache/test_cache.py`; `tests/response_cache/test_entry.py`; `tests/response_cache/test_key.py`; `tests/response_cache/test_key_factory.py` | Tester | Preserve the existing facade, entry, and key/hash contracts without source changes. |
| Validation configuration | `pyproject.toml`; `uv.lock`; `src/async_model_gateway/__version__.py` | Implementer / Reviewer | ReadOnly validation and no-version-bump evidence. |

Artifact path notes:

- `README.md` is a planned Modify path; `VERSION` has no standalone file, and the equivalent version metadata in `pyproject.toml`, `src/async_model_gateway/__version__.py`, and `uv.lock` is ReadOnly with no bump.
- `.github/copilot-instructions.md` is not modified.
- The listed paths are exhaustive. Any additional source, test, documentation, setting, or workflow artifact is plan drift and must be routed back through planning.

## Stable library metadata

- `README row`: modify the current-stage response-cache baseline paragraph only, documenting the internal injected-TTL freshness/store slice and explicitly retaining the existing public boundary.
- `VERSION bump`: no bump. `pyproject.toml` remains `0.7.0`; `src/async_model_gateway/__version__.py` and `uv.lock` remain synchronized to that unchanged version.
- `timing`: `publish-in-progress` for the README wording after implementation review; it does not create a release phase.
- `rationale`: the README is a stable-library summary surface, but this topic deliberately makes no public API, dependency, compatibility, or version change.
- `release notes`: none; do not create tags, publication, or release notes.

## Implementation Steps

1. Historical completed action: before production implementation, `tests/response_cache/test_freshness_policy.py` produced RED collection evidence for the approved freshness requirements. Under the prior cleared gate, it was mechanically renamed to `tests/response_cache/test_response_cache_freshness_policy.py`; the tester retained direct imports, recorded the old-to-new mapping in `plan/response-cache-freshness-policy/response-cache-freshness-policy.red-tests.yaml`, and ran focused/full GREEN validation. No post-implementation RED evidence is required or permitted. Retain `tests/model_registry/test_freshness_policy.py`, `tests/response_cache/test_cache.py`, `test_entry.py`, `test_key.py`, and `test_key_factory.py` unchanged.
2. Add `src/async_model_gateway/response_cache/freshness_policy.py` with the internal, fully typed `FreshnessPolicy.is_fresh(*, written_at, now) -> bool` contract; do not add a list, pipeline, generic cache-policy abstraction, or re-export.
3. Add `src/async_model_gateway/response_cache/ttl_freshness_policy.py` with injected `TtlFreshnessPolicy`, strict positive-`timedelta` validation, and strict-before-expiry freshness semantics; keep it synchronous and internal.
4. Add `src/async_model_gateway/response_cache/_in_memory_store.py` with internal `InMemoryResponseCacheStore` implementing the unchanged async `ResponseCacheStore` port, keyword-only `freshness_policy` injection, aware-UTC successful-write timestamps, non-renewing reads, overwrite timestamp replacement, and expired-as-`None` lookup behavior; do not add locks, lifecycle methods, eviction/deletion, or a public export.
5. Update only `README.md`, `docs/architecture.md`, `docs/settings-policy.md`, and `docs/specs/response-cache-boundary.md` to match the frozen internal-policy/store scope; leave every ReadOnly public-boundary and version path unchanged.
6. Run `uv run pytest tests/response_cache/test_response_cache_freshness_policy.py -v --no-cov`, `uv run pytest`, `uv run ruff check README.md docs src tests plan/response-cache-freshness-policy`, `uv run pyright`, and `uv run pre-commit run --all-files`; update `plan/response-cache-freshness-policy/response-cache-freshness-policy.step.md` with completed implementation work, while leaving Reviewer- and Human-owned artifacts for their owners.

## Validation / Acceptance Checks

- The canonical 11 sections, canonical status transitions, exact role-labelled paths, and single JSON reviewer-handoff schema remain compatible with `plan/topic-plan-contract.md` and `plan/agent-handoff-workflow.md`.
- The plan records the named semantic warning for both absent analysis companions; it does not fabricate analysis contents or claim strict mode.
- The `.spec.md` exists for D1 `non-trivial`, and `.step.md` contains all six workflow stages plus all six historically completed implementation steps marked `[X]`; only the renewed Reviewer and Human traceability gates remain pending.
- `FreshnessPolicy` has no contract beyond `is_fresh(*, written_at, now) -> bool`; neither it nor `TtlFreshnessPolicy` or `InMemoryResponseCacheStore` appears in root or `ports` exports.
- `TtlFreshnessPolicy` rejects non-positive TTLs, treats `now < written_at + ttl` as fresh, and returns false at and after the boundary.
- The internal store writes aware-UTC time only with a successful cache write, does not renew it on reads, uses the injected policy on each lookup, returns `None` for expired records, and never returns stale entries. This validation must not assert or introduce expired-record deletion, capacity, eviction, locking, lifecycle, timeout, cancellation, or external I/O behavior.
- Existing `ResponseCacheStore`, facade, entry, key, factory, package-root `__all__`, hash/key ownership, `project.version`, package `__version__`, and lockfile version remain unchanged.
- The predecessor path's pre-implementation RED evidence remains valid for the mechanically renamed `tests/response_cache/test_response_cache_freshness_policy.py`. The renamed path is validated with `uv run pytest tests/response_cache/test_response_cache_freshness_policy.py -v --no-cov` and the full declared validation suite; `new_red_evidence_created: false` is expected, and post-implementation RED evidence is prohibited. After implementation, the declared test, lint, type, and pre-commit commands pass and the Reviewer independently writes implementation-review evidence before PR routing.

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
- After merge, do not change `project.version`, package `__version__`, `uv.lock`, release notes, tags, or publication state for this topic.

## Open Questions / Unresolved Items

- None. The two absent optional analysis artifacts are a named routing warning rather than an unresolved implementation decision. If they appear later and disagree, planning must be reopened.

## Python implementation contract (supplemental)

### Goal

- Implement the locked internal freshness-policy/store slice without changing the public response-cache API or package exports.

### Non-goals

- No generic cache-policy framework, policy collection, or pipeline.
- No capacity, admission, eviction, invalidation, deletion, persistence, or settings system.
- No public concrete-store/policy import surface, orchestrator wiring, external I/O, lock, timeout, retry, cancellation wrapper, or version bump.

### Current Context

- `src/async_model_gateway/response_cache/ports/store.py` already defines the unchanged async `ResponseCacheStore.get(...)` and `set(...)` port. `cache.py` only delegates to that port; `entry.py` contains only `response: str`.
- `src/async_model_gateway/response_cache/__init__.py` exports only `ResponseCache`, `ResponseCacheEntry`, `ResponseCacheKey`, and `ResponseCacheKeyFactory`; `ports/__init__.py` exports only `FeatureHasher`.
- `docs/specs/response-cache-boundary.md` still states that concrete storage and TTL are not implemented, so it requires a bounded wording update after implementation.

### Requirements

1. An internal policy must expose exactly `is_fresh(*, written_at, now) -> bool` with aware datetime inputs and a boolean result.
2. A positive injected TTL must make a record fresh strictly before expiry and a miss exactly at or after expiry.
3. The internal store must implement the existing async port unchanged, associate writes with aware-UTC internal time, and consult the policy on reads without extending TTL.
4. No stale content may be returned, and no public export, key/hash owner, entry shape, port signature, dependency, or version metadata may change.
5. Tests must cover the happy path, invalid input, edge cases, regression guarantees, and backward compatibility listed below.

### Decisions

- Async-planning status: exempt — cite exemption evidence: the existing async `ResponseCacheStore` method boundary is implemented internally without adding an async resource lifecycle, lock/concurrency policy, timeout, cancellation ownership, retry, external I/O, task/worker, or sync-to-async conversion; the policy itself is synchronous, pure timestamp comparison.
- Module/package placement: add internal `freshness_policy.py`, `ttl_freshness_policy.py`, and `_in_memory_store.py` directly under `src/async_model_gateway/response_cache/`; add only the declared focused tests and documentation updates.
- New public API: no — `FreshnessPolicy`, `TtlFreshnessPolicy`, and `InMemoryResponseCacheStore` are internal implementation details with no root or `ports` re-export.
- Interface changes: no — preserve `ResponseCacheStore`, `ResponseCache`, entry, key, factory, and every existing root/ports export exactly.
- Breaking changes allowed: no — all existing public response-cache and package-version surfaces are preserved.
- New dependencies: no — use the standard library `datetime`; retain existing `typing_extensions` only if an override annotation is needed for the unchanged port.
- Error handling strategy: `TtlFreshnessPolicy` raises `ValueError` only for zero/negative TTL construction; normal expiry is `False` in the policy and `None` from the store; store-port exceptions are not introduced or translated.
- Typing strategy: strict Python 3.10 annotations using `datetime` / `timedelta`, explicit internal stored-record typing, and no `Any` or untyped callback/clock surface.

### Public Contract / API Changes

- No public API changes. The existing `ResponseCacheStore` signatures and all package exports remain unchanged.
- Internal-only contracts are frozen solely for implementation/review: `FreshnessPolicy.is_fresh(*, written_at, now) -> bool`, `TtlFreshnessPolicy(ttl: timedelta)`, and `InMemoryResponseCacheStore(*, freshness_policy: FreshnessPolicy)`.

### Affected Files / Modules

Likely affected files:
- `src/async_model_gateway/response_cache/freshness_policy.py`
- `src/async_model_gateway/response_cache/ttl_freshness_policy.py`
- `src/async_model_gateway/response_cache/_in_memory_store.py`
- `tests/response_cache/test_response_cache_freshness_policy.py`
- `tests/response_cache/test_ttl_freshness_policy.py`
- `tests/response_cache/test_in_memory_store.py`
- `tests/response_cache/test_response_cache_package_surface.py`
- `README.md`
- `docs/architecture.md`
- `docs/settings-policy.md`
- `docs/specs/response-cache-boundary.md`

Candidate files to inspect:
- `src/async_model_gateway/response_cache/ports/store.py`
- `src/async_model_gateway/response_cache/cache.py`
- `src/async_model_gateway/response_cache/entry.py`
- `src/async_model_gateway/response_cache/__init__.py`
- `src/async_model_gateway/response_cache/ports/__init__.py`
- `tests/response_cache/test_cache.py`
- `tests/response_cache/test_entry.py`
- `tests/response_cache/test_key.py`
- `tests/response_cache/test_key_factory.py`

### Implementation Steps

1. Historical completed action: before production implementation, the predecessor test path produced RED evidence for the approved requirements. After its mechanical rename to `tests/response_cache/test_response_cache_freshness_policy.py`, retain the old-to-new mapping and record focused/full GREEN validation in `response-cache-freshness-policy.red-tests.yaml`; do not create or claim new RED evidence after production implementation.
2. Add the internal policy protocol and TTL implementation in the two declared policy modules.
3. Add the internal in-memory port implementation with injected policy and timestamp-only freshness behavior.
4. Update only the four declared documentation files and preserve all public/cache-key/version paths.
5. Run the declared validation commands and update the step tracker; submit the resulting bounded change for implementation review.

### Test Plan

Test files: `tests/response_cache/test_response_cache_freshness_policy.py`, `tests/response_cache/test_ttl_freshness_policy.py`, `tests/response_cache/test_in_memory_store.py`, and `tests/response_cache/test_response_cache_package_surface.py`.

Test cases:
- Happy path: a successful write is returned while its injected TTL is still fresh.
- Invalid input: zero and negative `timedelta` values raise `ValueError` when constructing `TtlFreshnessPolicy`.
- Edge case: exact expiry and later reads return a miss; repeated reads retain the original write timestamp.
- Regression: existing facade, entry, key, factory, and store-port tests continue passing with unchanged public signatures and exports.
- Backward compatibility: package-root and `ports` surface tests prove the internal policy and concrete store do not leak publicly.

### Validation Commands

```text
uv run pytest tests/response_cache/test_response_cache_freshness_policy.py -v --no-cov
uv run pytest
uv run ruff check README.md docs src tests plan/response-cache-freshness-policy
uv run pyright
uv run pre-commit run --all-files
```

### Risks

- An equality mistake (`<=` rather than strict `<`) can return stale content at the TTL boundary.
- Adding a root/ports import or changing the entry/store port to carry timestamps would silently break the locked public boundary.
- Deleting expired records or adding locks while implementing a miss could smuggle eviction or concurrency policy into this bounded topic.

### Rollback Plan

- Revert the three new internal source modules, four focused test changes, four documentation updates, and the existing predecessor-path RED mapping plus renamed-path GREEN validation evidence; preserve the ReadOnly public-boundary and version files unchanged. No new post-implementation RED artifact exists or is created. No data migration or release rollback exists because storage is process-local and no release workflow runs.

### Open Questions

- None.
