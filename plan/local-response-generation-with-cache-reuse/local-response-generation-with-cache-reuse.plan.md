> Analysis routing — explicit human override: `analysis/local-response-generation-with-cache-reuse/requirements.md` and `analysis/local-response-generation-with-cache-reuse/technical-spec.md` do not exist. The human-locked snapshot correction below is the execution-facing source of truth. This incomplete optional analysis layer does not expand the locked scope.

# local-response-generation-with-cache-reuse

## Goal / Outcome

Make one top-level snapshot of `LocalResponseRequest.invocation` in
`LocalResponseGateway.generate()` after the existing local/ONNX guards and
before the first await. The private cache-key deriver and local executor must
both receive that same snapshot, so a caller mutation during registry freshness
cannot make cache identity diverge from execution input.

## Scope

### In scope

- Amend only the private gateway flow to materialize
  `invocation_snapshot = dict(request.invocation)` after both guards and before
  `resolve_freshness()` is first awaited.
- Pass that exact snapshot object to both `_CacheKeyDeriver` and
  `_LocalResponseExecutor`; preserve all other identity inputs and opaque-key
  handoff behavior.
- Add focused gateway, package-surface, and strict type-witness coverage,
  including a deterministic suspend-point race regression.
- Produce fresh snapshot plan/RED evidence and aggregate implementation/code
  review evidence under the declared paths. Those aggregate reviews cover every
  cumulative topic path from the actual PR baseline through the review head.

### Out of scope

- Any change to `ModelRegistry`, `ResponseCache`, `CacheKey`,
  `ModelPayloadHasher`, `ModelArtifact`, cache-key policy, local composition,
  default executor, package exports, request DTO, or model-source semantics.
- Deep copying, recursive freezing, serialization, validation, or mutation
  detection for invocation leaf objects.
- Remote/non-ONNX execution, task creation, locks, singleflight, retries,
  timeouts, lifecycle, persistence, invalidation, dependencies, or release work.

## Locked Decisions

- D1 remains `non-trivial`; the spec and step tracker remain required. Async
  planning is triggered because this changes an async call ordering boundary and
  a caller-visible mutation race while preserving established failure and
  cancellation semantics.
- After the existing local and `LoaderFamily.ONNX` guards, but before the first
  await of registry freshness, `generate()` must execute exactly
  `invocation_snapshot = dict(request.invocation)`. It must not use
  `request.invocation` after that point.
- `_CacheKeyDeriver` and `_LocalResponseExecutor` keep their existing private
  callable protocols and their `invocation: dict[str, object]` parameter. The
  gateway gives both collaborators the one same `invocation_snapshot` object:
  `deriver(model_name=request.model_name,
  model_payload_hash=freshness.entry.payload_hash, features=request.features,
  model_artifact=request.model_artifact, invocation=invocation_snapshot)`;
  the executor receives `artifact=request.model_artifact,
  invocation=invocation_snapshot`, whose invocation container has the same
  identity as the deriver argument. The deriver's returned opaque `CacheKey`
  remains unchanged when passed to both cache `lookup` and miss `remember`.
- Snapshot semantics are shallow: top-level key/value associations are frozen at
  materialization; unknown nested leaf objects are not deep-copied and retain
  identity. Callers must not mutate the leaf object graph while `generate()` is
  in progress. This topic adds no defensive leaf-graph policy.
- Any `dict(request.invocation)` materialization failure propagates unchanged
  before registry, deriver, cache, executor, converter, or remember observation.
  It creates no await, task, retry, timeout, catch, or fallback.
- Existing identity, privacy, context, exhaustive `match/case`, fail-open write,
  direct-await, exception, cancellation, and independent-miss behavior remains
  unchanged. `ModelRegistry`, `ResponseCache`, `CacheKey`, and
  `ModelPayloadHasher` remain ReadOnly.
- The deterministic race test must suspend registry freshness after snapshot
  materialization, mutate the original request mapping, then resume freshness;
  it proves deriver and executor receive the same original top-level snapshot
  and cache identity/result stay aligned.
- `README.md` and `docs/architecture.md` public-API documentation are deferred
  by locked scope and time to the post-merge `0.8.0` release phase. This is a
  deliberate deferral, not ignored documentation work; neither file nor version
  metadata is changed in this PR.
- The old `addfdb3`-baseline implementation and code reviews are historical and
  non-gating. Do not rewrite them. Formal current review evidence uses actual
  PR baseline `d5c5b329fec43f1d46fabdb87e1afb55573eb424`; its head is recorded
  as `mutable-at-review` until the post-commit review artifact records the exact
  commit SHA and cumulative diff.

## Boundaries / Exclusions

- The Planning actor may amend only this plan, its spec, and its tracker. Tester
  owns new test/RED artifacts; Implementer owns gateway-only code; Reviewer owns
  fresh aggregate reviews; Human alone owns clearance and merge decisions.
- Historical P1 review artifacts remain immutable historical truth. They may be
  cited only as non-gating context, never as snapshot approval evidence.
- Any request to alter a ReadOnly owner, public export, request shape, cache-key
  algorithm, documentation timing, version, or an unlisted path returns to
  `spec-and-plan-finalization`.

## Status / Allowed Transitions

- **Current**: `pr-open`; the fresh snapshot plan review, Human clearance,
  RED evidence, implementation review, and aggregate code review are recorded
  as complete. PR comment handling and Human merge approval remain separate
  uncompleted gates; no thread resolution or merge clearance is claimed.
- **Execution model**: `spec-and-plan-finalization -> plan-review -> human-check
  -> tdd-test-authoring -> implement-plan -> aggregate implementation-review ->
  aggregate code-review -> pr-open`. The tracker records the workflow phase
  separately. No release phase is part of this topic.
- **Review baseline rule**: each aggregate review starts from
  `d5c5b329fec43f1d46fabdb87e1afb55573eb424`, names the exact current review
  head after the snapshot change is committed, and covers all cumulative paths
  in `Artifact Paths`, not just the new gateway hunk.
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

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.plan.md` | Planning actor | Current snapshot execution and aggregate-review contract |
| Python spec | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.spec.md` | Planning actor | Non-trivial behavior contract |
| Step tracker | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.step.md` | Planning actor, then phase owners | Pending finalization and truthful progress |
| Snapshot plan review | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.snapshot.plan-review.json` | Plan-Reviewer | Fresh plan verdict; no historic approval reuse |
| Snapshot Human check | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.human-check.json` | Human | Fresh execution clearance, if granted |
| Snapshot RED evidence | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.snapshot.red-tests.yaml` | Tester | Fresh RED/type evidence for the snapshot contract |
| Aggregate implementation review | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.snapshot-aggregate-implementation-review.yaml` | Reviewer | Current-baseline implementation conformance review |
| Aggregate code review | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.snapshot-aggregate-code-review.yaml` | Reviewer | Current-baseline quality review |
| Gateway source | `src/async_model_gateway/local_response/gateway.py` | Implementer | Shallow snapshot materialization and same-object handoff |
| Gateway tests | `tests/local_response/test_gateway.py` | Tester | Order, identity/result alignment, race, privacy, and failures |
| Package tests | `tests/local_response/test_local_response_package_surface.py` | Tester | Private protocol and unchanged package surface coverage |
| Type witness | `tests/typecheck/local_response_generation_with_cache_reuse.py` | Tester | Strict construction and invocation typing witness |
| Cumulative local package paths | `src/async_model_gateway/local_response/__init__.py`, `src/async_model_gateway/local_response/_local_onnx_executor.py`, `src/async_model_gateway/local_response/request.py` | Reviewer | Read-only cumulative review coverage from the actual PR baseline |
| Cumulative historical topic evidence | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.plan-review.json`, `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.human-check.json`, `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.red-tests.yaml`, `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.implementation-review.yaml`, `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.code-review.yaml`, `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.validation-governance.yaml`, `plan/local-response-generation-with-cache-reuse/pyrightconfig.json` | Reviewer | Immutable, cumulative baseline context; old `addfdb3` reviews are historical/non-gating |
| ReadOnly owners | `src/async_model_gateway/model_registry/registry.py`, `src/async_model_gateway/model_registry/model_payload/canonical_hash.py`, `src/async_model_gateway/response_cache/cache.py`, `src/async_model_gateway/response_cache/key.py`, `src/async_model_gateway/model_runtime/model_artifact/artifact.py` | No change | Preserve established boundary owners |
| Deferred public documentation | `README.md`, `docs/architecture.md` | No change | Deferred to `0.8.0` release phase by locked scope/time |
| Version metadata | `pyproject.toml` | No change | No version bump in this PR |

No deletion or modification outside the listed Written implementation/test/topic
paths is authorized. The Reviewer checks the actual cumulative diff against the
baseline; all unlisted paths are plan drift.

## Stable library metadata

- `README row`: no change in this PR; public-API documentation is deferred to
  the post-merge `0.8.0` release phase.
- `VERSION bump`: no bump; `pyproject.toml` is ReadOnly for this topic.
- `timing`: deferred by locked scope/time to the `0.8.0` release phase after
  merge; it is not silently dropped.
- `rationale`: the snapshot correction is an unmerged bounded implementation
  amendment and does not widen this PR into release documentation work.

## Implementation Steps

1. Tester updates only the declared gateway/package/type-witness paths with RED
   tests for pre-await shallow snapshotting, same-object deriver/executor handoff,
   materialization failure ordering, and the deterministic registry-suspend
   mutation race; tests use static imports only.
2. Implementer updates only `src/async_model_gateway/local_response/gateway.py`:
   make the one shallow snapshot immediately after both guards and before
   registry freshness, then supply that object to the existing deriver and
   executor paths without changing cache key/context/outcome behavior.
3. Implementer runs focused/static/diff validation, verifies the written and
   ReadOnly path contract, and updates the tracker truthfully. Reviewer then
   creates the declared aggregate implementation/code review artifacts from the
   actual baseline to the exact post-commit head.

## Validation / Acceptance Checks

- Guards precede snapshot materialization and all collaborator observation.
  A materialization exception propagates unchanged before registry and leaves no
  later call, await, task, retry, timeout, cache entry, or execution.
- Registry suspension after materialization allows a deterministic mutation of
  the caller's original top-level mapping; deriver and executor receive the one
  same snapshot whose top-level association remains original, and the opaque key
  and execution result therefore remain aligned.
- Nested leaf values are not deep-copied; tests do not authorize mutation of the
  leaf graph during generation.
- Cache hit/miss, fresh contexts, opaque same-key lookup/remember, exhaustive
  outcome matching, privacy, direct awaits, exception/cancellation propagation,
  and independent same-key misses retain their current behavior.
- Focused pytest, topic Pyright witness, Ruff, and `git diff --check` pass. Topic
  tests use no dynamic module loading.
- Fresh snapshot plan review and Human clearance, if any, precede RED and
  implementation. Aggregate implementation/code reviews record baseline
  `d5c5b329fec43f1d46fabdb87e1afb55573eb424`, exact review head, full cumulative
  path coverage, and an independent verdict. Old `addfdb3`-baseline reviews do
  not satisfy these checks.

## Reviewer Handoff

```json
{
  "verdict": "approved",
  "blocking_issues": [],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

No release workflow is executed by this topic. The public documentation and any
version work remain deferred, explicitly, to the post-merge `0.8.0` release
phase.

## Open Questions / Unresolved Items

None. The human decisions lock snapshot timing, shallow semantics, mutation
responsibility, failure ordering, review baseline, and documentation timing.

## Python Implementation Extension

### Goal

Keep cache identity and local execution aligned by reusing one shallow
pre-await invocation snapshot through the existing async gateway flow.

### Non-goals

- No public API, package export, request DTO, or cache-key algorithm change.
- No deep-copy/recursive-freeze or caller leaf-mutation protection.
- No registry/cache/model-artifact/default-executor/documentation/version edit.

### Current Context

The gateway currently invokes the private deriver after `await`ing registry
freshness and invokes the executor later with `request.invocation`; the caller
can mutate the request mapping during that await. The injected deriver already
owns opaque cache identity, while the executor owns invocation behavior.

### Requirements

1. The sole `dict(request.invocation)` materialization is after both guards and
   before registry freshness is awaited.
2. The same shallow snapshot object is passed to deriver and executor; the
   original request mapping is unused afterwards.
3. Materialization failures propagate unchanged before every async collaborator.
4. A deterministic registry suspend-point regression proves a top-level caller
   mutation cannot split derived cache identity from execution input.
5. Existing cache, privacy, failure, cancellation, and direct-await behavior is
   preserved; declared validation and aggregate reviews provide current evidence.

### Decisions

- Async-planning status: triggered — cite trigger evidence: `generate()` awaits
  registry/cache/executor, and this amendment fixes state capture across its
  first suspension while retaining cancellation and no-task policy.
- Module/package placement: only existing `local_response/gateway.py` changes.
- New public API: no; private protocols retain their existing callable surface.
- Interface changes: no signature change; both existing private consumers now
  receive the gateway-owned snapshot instead of separate request-map reads.
- Breaking changes allowed: no public break; shallow snapshot behavior is the
  locked correction within the unmerged topic.
- New dependencies: no.
- Error handling strategy: snapshot materialization and established collaborator
  exceptions propagate unchanged; no translation or catch is added.
- Typing strategy: retain strict `dict[str, object]` callable contracts; no
  `Any`, cast, or dynamic import is introduced.

### Async boundary decision

Only the new synchronous snapshot occurs before the established first async
registry boundary. Registry, cache, and executor remain the same direct awaits.

### Resource lifecycle decision

The snapshot is local call state retained only by the active coroutine. The
gateway adds no owned task, pool, session, semaphore, or cleanup responsibility.

### Concurrency model

Each call snapshots independently before its first await and otherwise preserves
independent direct-await misses. No sharing, lock, queue, or singleflight is
introduced.

### Failure model

`dict()` failure and existing collaborator failures pass through unchanged.
Snapshot failure prevents every later collaborator and cache action.

### Cancellation / timeout policy

No timeout/retry/task is added. Existing cancellation can occur only at existing
awaits and still prevents later work; snapshot materialization itself is sync.

### Validation plan

Focused async tests control registry suspension with deterministic events, mutate
the original mapping only while the coroutine is suspended, then inspect exact
deriver/executor argument identity and cache/result alignment. Run declared
pytest, Pyright, Ruff, and diff checks before aggregate review.

### Handoff notes for the implementer

Do not use `request.invocation` after creating the snapshot. Do not deep-copy
leaves, alter deriver/executor signatures, or add awaits/tasks/catches. Preserve
the existing guards, key handoff, contexts, and match/case blocks.

### Public Contract / API Changes

No public contract changes. `LocalResponseGateway`, `LocalResponseRequest`, and
the existing private protocol signatures stay unchanged.

### Affected Files / Modules

Likely affected files:

- `src/async_model_gateway/local_response/gateway.py`
- `tests/local_response/test_gateway.py`
- `tests/local_response/test_local_response_package_surface.py`
- `tests/typecheck/local_response_generation_with_cache_reuse.py`

Candidate files to inspect:

- `src/async_model_gateway/local_response/request.py`
- `src/async_model_gateway/response_cache/key.py`

### Implementation Steps

The canonical three steps above are the creator-owned executable work for this
extension.

### Test Plan

Happy path: cache hit/miss order and same opaque key behavior. Invalid input:
guards remain first. Edge case: materialization error and shallow leaf identity.
Test Case — deterministic registry suspension verifies that, after both guards
and before the first registry await, the gateway has made the one shallow
snapshot; a top-level caller mutation cannot affect the same snapshot seen by
deriver/executor. The regression test records the exact
calls: `deriver(model_name=request.model_name,
model_payload_hash=freshness.entry.payload_hash, features=request.features,
model_artifact=request.model_artifact, invocation=invocation_snapshot)` and
executor inputs `artifact=request.model_artifact,
invocation=invocation_snapshot`; it asserts the two invocation arguments have
the same container identity and that the returned opaque `CacheKey` reaches
lookup and miss remember unchanged. Backward compatibility: unchanged
package/request/type surface and ReadOnly owners. Failures and cancellation keep
their existing propagation; static imports only.

### Validation Commands

```bash
uv run pytest --no-cov tests/local_response -v
uv run --no-sync --locked -- pyright --project plan/local-response-generation-with-cache-reuse/pyrightconfig.json
uv run --no-sync --locked -- ruff check src/async_model_gateway/local_response tests/local_response tests/typecheck/local_response_generation_with_cache_reuse.py
git diff --check
```

### Risks

Implementing the snapshot after the first await, passing two different copies, or
deep-copying leaf objects would violate the race and ownership contract. Narrow
argument-identity and suspend-point tests must catch these regressions.

### Rollback Plan

Revert only the declared gateway/test/witness and snapshot topic artifact paths.
Do not alter the ReadOnly owners or historical P1 review evidence.

### Open Questions

None.
