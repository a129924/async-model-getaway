> Analysis routing — explicit human override: `analysis/local-response-generation-with-cache-reuse/requirements.md` and `analysis/local-response-generation-with-cache-reuse/technical-spec.md` do not exist. The human-locked P1 correction contract below is the execution-facing source of truth. This absence does not expand scope or block the new plan review.

# local-response-generation-with-cache-reuse

## Goal / Outcome

Amend the local-response cache identity seam so `LocalResponseGateway` privately
injects `_CacheKeyDeriver`, delegates the complete identity inputs to it after
registry freshness, and passes its resulting `CacheKey` unchanged to the existing
cache facade. The amendment must prevent cache cross-hits when either invocation
or model name differs, while preserving the existing local/ONNX guards, context,
outcome, and async policies.

## Scope

### In scope

- Replace the gateway-only `hash_features` injection seam with the frozen private
  `_CacheKeyDeriver` protocol and constructor parameter.
- Update the gateway, its focused behavior and package-surface tests, strict type
  witness, and the listed topic artifacts for this P1 correction.
- Re-open the plan, Human-check, RED, implementation-review, and code-review
  gates. Historical evidence stays repo-visible but is explicitly superseded.

### Out of scope

- Any change to `ModelRegistry`, `ResponseCache`, `CacheKey`,
  `ModelPayloadHasher`, `ModelArtifact`, local composition, executor, package
  exports, request DTO, or model-source semantics.
- Any cache algorithm owned by the gateway, including feature hashing, canonical
  serialization, digest selection, collision handling, or namespace construction.
- Remote execution, non-ONNX execution, singleflight, lock, retry, timeout,
  lifecycle, persistence, invalidation, version/documentation/release work, or
  a new dependency.

### Non-goal

- Do not expose `_CacheKeyDeriver` from the package or root package.
- Do not store, log, or place raw prompts, model names, or artifact paths in a
  cache namespace, cache context, or cache record.
- Do not manufacture replacement reviewer or Human approvals while amending this
  plan.

## Locked Decisions

- D1 remains `non-trivial`; the Python spec and step tracker remain required.
- `LocalResponseRequest`, package exports, default executor seam, local-source
  guard, and `LoaderFamily.ONNX` guard remain unchanged. Local source is a
  guarded constant and is not an input to cache identity.
- `gateway.py` defines this private, non-exported callable protocol exactly:

  ```python
  class _CacheKeyDeriver(Protocol):
      def __call__(
          self,
          *,
          model_name: str,
          model_payload_hash: str,
          features: Mapping[str, str],
          model_artifact: ModelArtifact,
          invocation: dict[str, object],
      ) -> CacheKey: ...
  ```

  It is a caller-defined stable, collision-controlled canonical-identity and
  domain-separation owner. The gateway does not inspect, modify, recreate, or
  derive any part of its returned key.
- `LocalResponseGateway.__init__` keeps its keyword-only shape and is amended
  exactly as follows. `_OnnxResultConverter` and `_LocalResponseExecutor` keep
  their existing private protocols and exact call contracts.

  ```python
  def __init__(
      self,
      *,
      registry: ModelRegistry,
      response_cache: ResponseCache,
      cache_key_deriver: _CacheKeyDeriver,
      convert_onnx_result: _OnnxResultConverter,
      executor: _LocalResponseExecutor | None = None,
  ) -> None: ...
  ```

  `hash_features` is removed from this constructor and from gateway state. This
  is a bounded correction to an unmerged topic implementation, not a new package
  export or a change to the request DTO.
- After the existing guards, `generate()` awaits registry freshness, calls the
  deriver with `request.model_name`, `freshness.entry.payload_hash`,
  `request.features`, `request.model_artifact`, and `request.invocation`, then
  calls cache `lookup(key=key, context=object())`. It passes the key returned by
  the deriver unchanged to both `lookup` and a miss's `remember`.
- Identity coverage is mandatory: model name, payload hash, features, invocation,
  and model artifact must participate in the deriver's identity policy. A change
  to invocation or model name must derive a different key and cannot cross-hit.
  Tests also prove that the artifact is supplied to the deriver. The gateway may
  pass raw inputs only to this injected collaborator; raw prompt data, model name,
  and artifact path must never be copied into cache namespace, context, or record.
- The existing fresh context policy is unchanged: `lookup` receives a new
  call-site `object()` and a miss's `remember` receives another new `object()`.
  The gateway does not retain, compare, export, or use request data as context.
- Existing exhaustive `match/case` handling remains unchanged: `CacheHit` returns;
  `CacheMiss` proceeds; `Remembered | Skipped | Failed` returns the converted
  response; unexpected closed-union values reach `assert_never`. No gateway cache
  catch is added.
- Deriver failure propagates unchanged, occurs before lookup, and prevents lookup,
  execution, conversion, and `remember`. Registry, executor, converter, and
  cancellation propagation remain unchanged. Same-key misses remain independent
  direct awaits with no task, lock, retry, timeout, queue, or background owner.
- `ModelRegistry`, `ResponseCache`, `CacheKey`, and `ModelPayloadHasher` remain
  ReadOnly owners. Stable-library intent is absent for this correction: it has no
  documentation, version, tag, or release action.
- `local-response-generation-with-cache-reuse.validation-governance.yaml` records
  only the locked topic Pyright validation command and its result. It does not
  change plan phase status and cannot grant any Reviewer or Human approval.

## Boundaries / Exclusions

- Planning actor changes only the declared plan/spec/step and marks obsolete gate
  evidence. Tester owns fresh tests and RED evidence; Implementer owns the
  approved gateway-only correction; Reviewer and Human alone issue new gates.
- The cache-key deriver defines identity policy, not the gateway, registry, cache,
  artifact, or request DTO. The gateway remains a coordinator.
- Any request to alter public exports, cache/registry owners, artifact structure,
  canonicalization policy, release intent, or an unlisted path returns to
  `spec-and-plan-finalization`.

## Status / Allowed Transitions

- **Current**: `review-ready`. The next transition is an independent
  implementation review. This plan does not declare, replace, or mirror any gate
  verdict. The concrete state of plan review, Human check, and P1 implementation
  progress is determined only by their latest independent repo-visible evidence
  artifacts and the step tracker.
- **Execution model**: `spec-and-plan-finalization -> implement-plan ->
  pr-comment -> pr-comment-review-pr-comments-and-fix`; no `release` phase is
  declared for this correction.
- **Gate evidence**: historical review and validation artifacts remain
  repo-visible with their own recorded supersession or gate state. This plan
  neither overwrites nor interprets those records; later routing reads their
  declared artifacts and the step tracker.
- **Validation-governance routing**: the declared validation-governance artifact
  records only the topic Pyright command/result. Its stated independent
  verification cannot close a Reviewer or Human gate or change topic status.
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

### ReadOnly

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Registry owner | `src/async_model_gateway/model_registry/registry.py` | No change | Supplies authoritative freshness payload hash |
| Cache facade | `src/async_model_gateway/response_cache/cache.py` | No change | Consumes the opaque derived key and preserves outcomes |
| Cache key | `src/async_model_gateway/response_cache/key.py` | No change | Existing key value contract |
| Payload hasher | `src/async_model_gateway/model_registry/model_payload/canonical_hash.py` | No change | Existing payload-hash owner |
| Model artifact | `src/async_model_gateway/model_runtime/model_artifact/artifact.py` | No change | Read-only identity input contract |
| Request/package/default executor | `src/async_model_gateway/local_response/request.py`, `src/async_model_gateway/local_response/__init__.py`, `src/async_model_gateway/local_response/_local_onnx_executor.py` | No change | Preserve current DTO, exports, and executor ownership |

### Written

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.plan.md` | Planning actor | Amended execution and gate-reset contract |
| Python spec | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.spec.md` | Planning actor | Amended non-trivial behavior contract |
| Step tracker | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.step.md` | Planning actor, then phase owners | Reset progress and phase gates |
| Plan review | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.plan-review.json` | Plan-Reviewer | Historical supersession marker, then replacement review verdict |
| Human check | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.human-check.json` | Human | Historical supersession marker, then replacement clearance |
| RED evidence | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.red-tests.yaml` | Tester | Historical supersession marker, then fresh RED/type evidence |
| Validation governance | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.validation-governance.yaml` | Validator; Reviewer verifies its stated next gate | Records only the authoritative topic Pyright command/result; cannot itself grant any review or Human approval |
| Implementation review | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.implementation-review.yaml` | Reviewer | Historical supersession marker, then replacement conformance verdict |
| Code review | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.code-review.yaml` | Reviewer | Historical supersession marker, then replacement quality verdict |
| Gateway source | `src/async_model_gateway/local_response/gateway.py` | Implementer | Private deriver injection and unchanged-key cache flow |
| Gateway tests | `tests/local_response/test_gateway.py` | Tester | Identity, order, privacy, failure, and preserved flow coverage |
| Package tests | `tests/local_response/test_local_response_package_surface.py` | Tester | Constructor/private protocol/package-surface coverage |
| Type witness | `tests/typecheck/local_response_generation_with_cache_reuse.py` | Tester | Strict typed construction with the private deriver seam |

### Deleted

None. Any deletion is plan drift.

### Modify

None. No existing owner, documentation, version, release, or unrelated test path
is authorized by this P1 correction.

All unlisted paths are outside this topic. A later request that needs an unlisted
path is a plan-alignment problem and must return to plan finalization.

## Implementation Steps

1. Tester updates only the declared gateway/package/type-witness tests to express
   the `_CacheKeyDeriver` constructor and protocol; adds RED regressions proving
   changed invocation and changed model name derive separate keys with no
   cross-hit, verifies artifact is passed into identity derivation, and records
   privacy/failure/order/context coverage without dynamic module loading.
2. Implementer updates only `src/async_model_gateway/local_response/gateway.py`:
   replace `_FeatureHasher` and `hash_features` state/parameter with the exact
   `_CacheKeyDeriver` protocol/parameter; after freshness, invoke it with all
   locked inputs, hand its key unchanged to cache calls, and preserve all guards,
   fresh contexts, outcome matches, direct-await behavior, and propagation.
3. Implementer runs the declared focused and static validation, confirms only the
   Written code/test paths changed beyond necessary topic artifacts and every
   ReadOnly/Modify path is untouched, then updates the tracker truthfully.

## Validation / Acceptance Checks

- **Happy path / regressions**: cache hit returns before executor/converter/write;
  cache miss follows Registry -> deriver -> lookup -> executor -> converter ->
  remember -> return. Different invocation and different model name produce
  different keys and receive no cross-hit.
- **Identity / privacy**: the deriver receives model name, payload hash, features,
  invocation, and the exact artifact. The returned `CacheKey` is passed unchanged;
  raw prompts, model names, and artifact paths do not appear in cache namespace,
  context, or record inputs.
- **Invalid input / edge cases**: local and ONNX guards remain before every
  collaborator; cache outcomes retain exhaustive matching and fail-open write
  behavior; fresh lookup/remember contexts remain distinct private objects.
- **Failure / cancellation / concurrency**: deriver failure is identical and
  precedes all later collaborators with no remember; registry/executor/converter
  failure and cancellation policy remain unchanged; same-key misses stay
  independent.
- **Backward compatibility**: package exports, request DTO, cache/registry/key/
  payload-hasher/artifact sources, and default executor remain unchanged. The
  only constructor change is replacement of the old private seam.
- Fresh plan review and Human clearance must precede fresh RED; fresh RED,
  implementation review, and code review must replace—not rely upon—the marked
  historical artifacts before PR routing.
- **Topic Pyright validation**: the command and result are recorded only in
  `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.validation-governance.yaml`:

  ```bash
  uv run --no-sync --locked -- pyright --project plan/local-response-generation-with-cache-reuse/pyrightconfig.json
  ```

  The artifact is validation evidence only. Its stated independent verification
  does not grant plan-review, implementation-review, code-review, or Human
  approval.

## Reviewer Handoff

```json
{
  "verdict": "needs-rework",
  "blocking_issues": [
    {
      "issue": "Awaiting independent review of the P1 cache-key-deriver amendment.",
      "file": "plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.plan.md",
      "fix": "Issue a new repo-visible verdict before any replacement Human check or implementation work."
    }
  ],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

No release workflow required. This correction declares no documentation, version,
tag, package publication, or release action.

## Open Questions / Unresolved Items

None. The human-locked P1 contract freezes the constructor, identity inputs,
privacy policy, failure behavior, paths, and gate reset.

## Python Implementation Extension

### Goal

Correct the private cache-key derivation seam without changing the async gateway's
ownership boundaries.

### Non-goals

No new public export, cache key algorithm, registry/cache/artifact change, remote
path, lifecycle policy, or release work.

### Current Context

The existing gateway currently calls `hash_features` after registry freshness and
constructs a key itself. `ModelRegistry` already supplies
`freshness.entry.payload_hash`; `ResponseCache` owns lookup/write outcomes. The
correction moves only complete response-identity derivation to the injected
private collaborator.

### Requirements

1. The exact protocol and constructor use `cache_key_deriver`, not `hash_features`.
2. The gateway passes every locked identity input to the deriver and uses the
   returned key unchanged for lookup and remember.
3. Different invocation and model-name inputs cannot cross-hit under the test
   deriver; the artifact participates in the deriver call contract.
4. Privacy, failure, context, outcome, cancellation, and independent-miss policy
   remain as locked above.
5. Focused pytest, the topic Pyright witness, Ruff, and `git diff --check` pass.

### Decisions

- Async-planning status: triggered — cite trigger evidence: existing async
  `generate()`, async registry/cache/executor calls, failure/cancellation
  propagation, and independent concurrent miss policy remain behaviorally locked.
- Module/package placement: only existing `local_response/gateway.py` changes;
  protocol remains private there.
- New public API: no new export; the public gateway constructor replaces an
  implementation collaborator parameter before publication.
- Interface changes: yes, the constructor parameter changes from `hash_features`
  to `cache_key_deriver`; request and package interfaces do not change.
- Breaking changes allowed: yes, only for the unmerged topic's superseded private
  injection seam, to correct P1 identity behavior before a new approval.
- New dependencies: no.
- Error handling strategy: all deriver failures propagate unchanged before cache
  lookup; existing guarded and cache-outcome behavior remains unchanged.
- Typing strategy: strict typed private `Protocol`, `Mapping[str, str]`,
  `ModelArtifact`, `dict[str, object]`, and `CacheKey`; no `Any`.

#### Async boundary decision

Only the established registry, cache, executor, and `generate()` calls are async.
The deriver is synchronous and runs after freshness but before lookup.

#### Resource lifecycle decision

The gateway owns no task, pool, session, semaphore, or cleanup lifecycle. The
deriver is caller-owned and introduces no retained resources.

#### Concurrency model

Each call invokes its own synchronous deriver and directly awaits the established
sequence. Same-key calls do not share work.

#### Failure model

Deriver exceptions pass through unchanged and stop the flow before lookup. No
catch, cache write, translation, or fallback is added.

#### Cancellation / timeout policy

No timeout is introduced. Cancellation from existing async collaborators still
propagates unchanged and prevents later cache write.

#### Validation plan

Focused tests prove identity separation, artifact input, unchanged-key handoff,
privacy, and deriver-stop-before-lookup; package/type tests prove the frozen
private signature. Static and diff validation must pass.

#### Handoff notes for the implementer

Do not calculate a namespace, hash, canonical representation, or key field in the
gateway. Preserve the existing guards, contexts, match/case blocks, and default
executor behavior exactly.

### Public Contract / API Changes

`LocalResponseGateway` remains public with the exact amended keyword-only
constructor in `Locked Decisions`. `_CacheKeyDeriver` is private and non-exported;
no package/root export or request DTO changes occur.

### Affected Files / Modules

Likely affected files:

- `src/async_model_gateway/local_response/gateway.py`
- `tests/local_response/test_gateway.py`
- `tests/local_response/test_local_response_package_surface.py`
- `tests/typecheck/local_response_generation_with_cache_reuse.py`

Candidate files to inspect:

- `src/async_model_gateway/response_cache/key.py`
- `src/async_model_gateway/model_registry/registry.py`

### Implementation Steps

See the canonical `Implementation Steps`; its three numbered items are the
creator-owned executable work for this Python extension.

### Test Plan

Happy path: hit and miss retain the locked sequence. Invalid input: existing
local/ONNX guards remain first. Edge case: all closed outcomes and fresh contexts
remain correct. Regression: changed invocation and changed model name receive
different derived keys/no cross-hit; artifact is passed to deriver. Backward
compatibility: package/request/default executor and ReadOnly owners do not change.
Failure tests cover deriver propagation/no lookup or remember; concurrency tests
retain independent misses.

### Validation Commands

```bash
uv run pytest --no-cov tests/local_response -v
uv run --no-sync --locked -- pyright --project plan/local-response-generation-with-cache-reuse/pyrightconfig.json
uv run ruff check src/async_model_gateway/local_response tests/local_response tests/typecheck/local_response_generation_with_cache_reuse.py
git diff --check
```

### Risks

An implementer might reconstruct or alter the returned key, omit an identity
input, or leak a raw value through cache-facing fields; the focused regressions
and privacy witnesses must catch each case.

### Rollback Plan

Revert only `src/async_model_gateway/local_response/gateway.py`, the three
declared test/witness files, and the topic artifacts in this plan if the amended
contract is rejected. Do not revert or alter ReadOnly owners.

### Open Questions

None.
