> Analysis routing — explicit human override: `analysis/local-response-generation-with-cache-reuse/requirements.md` and `analysis/local-response-generation-with-cache-reuse/technical-spec.md` do not exist. The approved, frozen chat contract is the execution-facing source of truth for this topic. This absence must not expand scope or block plan review.

# local-response-generation-with-cache-reuse

## Goal / Outcome

### Goal

Add the bounded public `async_model_gateway.local_response` entrypoint. Its
`LocalResponseGateway.generate()` accepts a caller-supplied local ONNX artifact,
reuses an existing response-cache hit, and otherwise delegates one invocation to
the existing internal local composition before remembering the converted string.

After a verified merge, promote only the declared documentation and version
metadata to `0.8.0` and create lightweight tag `v0.8.0`; this does not create a
GitHub Release or publish a package.

## Scope

### In-Scope

- A frozen, slotted `LocalResponseRequest` and public `LocalResponseGateway` in
  `async_model_gateway.local_response`.
- Local + `LoaderFamily.ONNX` validation before every collaborator call.
- Registry freshness, injected feature hashing, existing `ResponseCache` reuse,
  one internal local execution through the declared private ONNX adapter,
  ONNX-result conversion, and fail-open cache write handling in the locked order.
- Fresh RED tests, strict type witness, review gates, and bounded post-merge
  `0.8.0` documentation/version/tag work.

### Out-Of-Scope

- Remote execution, `ModelGateway`, or a remote fallback; non-local requests fail
  closed with `NotImplementedError`.
- PICKLE/TORCH execution, loader-family inference, provider adapters, result
  schemas beyond the injected ONNX converter, or changes to `ModelArtifact`.
- Cache-policy, store, codec, invalidation, persistence, TTL, eviction,
  singleflight, deduplication, lock, task, retry, timeout, background, close, or
  unload behavior.
- Changes to registry identity/freshness semantics, `ResponseCache` outcomes,
  `ModelPool`, internal executor/composition behavior, or existing source/tests
  outside the exact path contract.
- GitHub Release, PyPI/TestPyPI publication, annotated tags, tag retargeting, or
  release work before merge.

### Non-Goal

- Do not make `ModelPool`, the internal executor, or local composition public.
- Do not place a new export on `async_model_gateway` root or alter its current
  `__all__` contract.
- Do not catch or translate registry, feature-hasher, executor, converter, or
  cancellation failures.
- Do not make concurrent same-key misses share work.

## Locked Decisions

- D1 verdict: `non-trivial`; the Python planning extension and its required spec
  and step tracker are mandatory.
- The only public package is `async_model_gateway.local_response`; its package
  root exports exactly `LocalResponseGateway` and `LocalResponseRequest`.
- The public request contract is frozen as:

  ```python
  @dataclass(frozen=True, slots=True)
  class LocalResponseRequest:
      model_name: str
      model_source_kind: ModelSourceKind
      model_payload: dict[str, ModelPayloadValue]
      features: Mapping[str, str]
      model_artifact: ModelArtifact
      invocation: dict[str, object]
  ```

  `request.py` defines, but neither its `__all__` nor the package re-exports,
  this exact Python-3.10 alias:

  ```python
  ModelPayloadValue: TypeAlias = None | bool | int | float | str | list["ModelPayloadValue"] | dict[str, "ModelPayloadValue"]
  ```

  It remains compatible with the existing registry model-payload contract; it
  is not an additional public package export or a second hashing owner.
- `gateway.py` defines the following non-exported private protocols exactly;
  they are implementation typing seams, not package surface:

  ```python
  class _FeatureHasher(Protocol):
      def __call__(self, features: Mapping[str, str]) -> str: ...

  class _OnnxResultConverter(Protocol):
      def __call__(self, result: list[object]) -> str: ...

  class _LocalResponseExecutor(Protocol):
      async def __call__(
          self, artifact: ModelArtifact, invocation: dict[str, object]
      ) -> list[object]: ...
  ```

- `LocalResponseGateway.generate(*, request: LocalResponseRequest) -> str` is
  async. Its exact keyword-only constructor contract is:

  ```python
  def __init__(
      self,
      *,
      registry: ModelRegistry,
      response_cache: ResponseCache,
      hash_features: _FeatureHasher,
      convert_onnx_result: _OnnxResultConverter,
      executor: _LocalResponseExecutor | None = None,
  ) -> None: ...
  ```

  No new dependency is introduced. When `executor is None`, the constructor
  binds `src/async_model_gateway/local_response/_local_onnx_executor.py`'s
  private default adapter with the `_LocalResponseExecutor` callable shape; that
  adapter delegates only to existing `_create_local_runtime_composition()`
  behavior and introduces no export or lifecycle change.
- `generate()` first rejects `model_source_kind is not ModelSourceKind.LOCAL`,
  then rejects `model_artifact.loader_family is not LoaderFamily.ONNX`, both with
  `NotImplementedError`. These guards occur before registry, hashing, cache,
  executor, or converter use.
- The exact miss sequence is Registry -> feature hash -> cache lookup ->
  execution -> converter -> remember -> return. Registry is called with the
  request identity and `CacheKey` is built as
  `CacheKey(namespace="local-response-v1", model_payload_hash=freshness.entry.payload_hash, feature_hash=...)`.
- Each cache facade call creates its private context at the call site:
  `lookup` receives `context=object()` and a miss's later `remember` receives a
  separate `context=object()`. Each expression creates a fresh object, including
  across calls; the two contexts for one miss are distinct. The gateway must not
  retain, compare, export, or reuse either sentinel; it must never pass
  `LocalResponseRequest` or any request field as context. Context stays outside
  cache identity and stored records.
- Cache lookup uses the existing closed outcome types and exactly this shape:

  ```python
  match lookup_outcome:
      case CacheHit(value=value):
          return value
      case CacheMiss():
          pass
      case _:
          assert_never(lookup_outcome)
  ```

  No lookup `try/except` is added: existing facade operational failures already
  become `CacheMiss`.
- A miss direct-awaits the configured executor once, passes its `list[object]`
  result once to the configured converter, then calls `remember` with its fresh
  call-site context sentinel. Its outcome match is `Remembered() | Skipped() |
  Failed()` -> the converted response; an unexpected closed-union value uses
  `assert_never`. No broad catch is allowed.
- Registry, hasher, executor, converter, and cancellation failures propagate
  unchanged. A failure before completion of conversion performs no cache write;
  `remember`'s closed failed/skipped outcomes are deliberately fail-open.
- Each same-key miss performs its own direct awaited sequence. There is no
  singleflight task, shared lock, retry, timeout, queue, or background owner.
- Registry, response-cache, pool, internal executor, local composition,
  model-artifact, and loader-family source boundaries remain read-only.
- Stable-library intent is declared: release is conditional after merge, uses
  `0.7.0 -> 0.8.0`, and lightweight `v0.8.0` targets the post-merge release
  documentation/version commit.

## Boundaries / Exclusions

- Plan-Creator creates only this topic's plan/spec/step. Plan-Reviewer writes the
  planning verdict; Tester writes fresh tests/type evidence; Implementer changes
  only approved source paths; Reviewer writes implementation/code verdicts; Human
  owns both clearance gates and merge approval.
- The public gateway consumes existing boundaries but does not transfer ownership
  of payload hashing, registry freshness, cache identity, local runtime loading,
  execution lifecycle, or cache record policy.
- Scope, path, API, outcome-match, async, test, version, or release drift returns
  to `spec-and-plan-finalization`; no actor may rewrite historical evidence.

## Status / Allowed Transitions

- **Current**: `review-ready`.
- **Execution model**: `spec-and-plan-finalization -> implement-plan -> pr-comment
  -> pr-comment-review-pr-comments-and-fix -> release`.
- **Gate order**: plan review approved -> Human implementation clearance -> fresh
  RED -> implementation -> implementation review approved -> code review approved
  -> PR -> Human merge -> release clearance -> bounded `0.8.0` release.
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
  - `merged` -> `released`

## Artifact Paths

### ReadOnly

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Registry owner | `src/async_model_gateway/model_registry/registry.py` | No change | Freshness/payload-hash authority |
| Registry identity | `src/async_model_gateway/model_registry/entry.py` | No change | `ModelSourceKind` and registry entry contract |
| Cache facade | `src/async_model_gateway/response_cache/cache.py` | No change | Existing operational miss/write-outcome behavior |
| Cache identity/outcomes | `src/async_model_gateway/response_cache/key.py` | No change | Existing `CacheKey` contract |
| Cache outcomes | `src/async_model_gateway/response_cache/outcomes.py` | No change | Existing closed match cases |
| Model artifact | `src/async_model_gateway/model_runtime/model_artifact/artifact.py` | No change | Caller-provided read contract |
| Loader family | `src/async_model_gateway/model_runtime/model_artifact/loader_family.py` | No change | Explicit ONNX vocabulary |
| Local composition | `src/async_model_gateway/model_runtime/_local_runtime_composition.py` | No change | Private default execution delegation |
| Model pool | `src/async_model_gateway/model_runtime/model_pool/pool.py` | No change | Internal acquisition boundary |
| Internal executor | `src/async_model_gateway/model_runtime/model_execution/execution.py` | No change | Existing invocation lifecycle |
| Root package | `src/async_model_gateway/__init__.py` | No change | Preserve root public surface |

### Written

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.plan.md` | Plan-Creator | Frozen implementation/release contract |
| Python spec | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.spec.md` | Plan-Creator | Non-trivial behavior contract |
| Step tracker | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.step.md` | Plan-Creator, then phase owners | Canonical progress state |
| Plan review | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.plan-review.json` | Plan-Reviewer | Independent planning verdict |
| Human check | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.human-check.json` | Human | `implement-plan` clearance |
| RED evidence | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.red-tests.yaml` | Tester | Fresh RED/type-analysis evidence |
| Type config | `plan/local-response-generation-with-cache-reuse/pyrightconfig.json` | Tester | Strict analysis of the topic witness |
| Implementation review | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.implementation-review.yaml` | Reviewer | Plan-conformance verdict |
| Code review | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.code-review.yaml` | Reviewer | Independent quality verdict |
| Human merge | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.human-merge.json` | Human | Explicit merge gate |
| Release human check | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.release-human-check.json` | Human | Release clearance |
| Release evidence | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.release.yaml` | Release Implementer | Release/tag evidence |
| Release review | `plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.release-review.yaml` | Reviewer | Release-conformance verdict |
| Public package | `src/async_model_gateway/local_response/__init__.py` | Implementer | Exact two-symbol public surface |
| Request source | `src/async_model_gateway/local_response/request.py` | Implementer | Frozen request/value typing contract |
| Gateway source | `src/async_model_gateway/local_response/gateway.py` | Implementer | Guarded cache-reuse generation flow |
| Private ONNX adapter | `src/async_model_gateway/local_response/_local_onnx_executor.py` | Implementer | Private default-executor delegation to existing composition; no public surface or lifecycle ownership |
| Gateway tests | `tests/local_response/test_gateway.py` | Tester | Behavior/order/failure/concurrency coverage |
| Package tests | `tests/local_response/test_local_response_package_surface.py` | Tester | Export/signature/default-adapter boundary |
| Type witness | `tests/typecheck/local_response_generation_with_cache_reuse.py` | Tester | Strict public typing evidence |

### Deleted

None. Any deletion is plan drift.

### Modify

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Release README | `README.md` | Release Implementer | First-read local response/cache-reuse truth |
| Release architecture | `docs/architecture.md` | Release Implementer | Bounded implemented local flow status |
| Release core spec | `docs/specs/core-abstractions-boundary.md` | Release Implementer | Shared dependency-direction update |
| Release orchestrator spec | `docs/specs/orchestrator-boundary.md` | Release Implementer | Limited local gateway coordination wording |
| Release response-cache spec | `docs/specs/response-cache-boundary.md` | Release Implementer | Document one consumer without changing cache authority |
| Release model-side spec | `docs/specs/model-side-boundary.md` | Release Implementer | Preserve internal owner boundaries while naming public caller |
| Runtime version | `src/async_model_gateway/__version__.py` | Release Implementer | `0.8.0` runtime version |
| Package metadata | `pyproject.toml` | Release Implementer | `0.8.0` package version |
| Lockfile | `uv.lock` | Release Implementer | Synchronized `0.8.0` metadata |

No path appears in more than one state table. All unlisted paths are outside this
topic; pre-merge work must not modify any `Modify` path.

## Stable library metadata

- `README row`: describe only the public local ONNX response-generation entrypoint,
  registry-derived cache identity, reuse on `CacheHit`, and deferred remote/broader
  orchestration behavior.
- `VERSION bump`: `0.7.0 -> 0.8.0` in runtime version, packaging metadata, and
  synchronized lockfile metadata.
- `timing`: `release`, only after Human merge and a fresh release Human check.
- `tag`: create and push lightweight `v0.8.0` at the post-merge release
  documentation/version commit; never retarget it.
- `rationale`: a new public subpackage needs first-read/version promotion, without
  implying a general remote or full orchestrator implementation.
- No GitHub Release and no package publication.

## Implementation Steps

1. Tester creates the declared gateway, package-surface, and strict type-witness
   tests plus topic Pyright config; with production unchanged, records fresh RED
   evidence that maps every locked behavior and verifies no dynamic module loading.
2. Implementer creates `src/async_model_gateway/local_response/request.py` and
   `src/async_model_gateway/local_response/__init__.py` with the exact frozen,
   slotted request, non-exported recursive `ModelPayloadValue: TypeAlias`, and
   two-symbol package surface.
3. Implementer creates `src/async_model_gateway/local_response/gateway.py` and
   `src/async_model_gateway/local_response/_local_onnx_executor.py`. `gateway.py`
   owns the exact private callable protocols, constructor injection,
   guard-before-collaborator ordering, fresh distinct call-site cache-context
   sentinels, exact `match/case` outcomes, direct-await miss flow, and unchanged
   failure/cancellation propagation. The private adapter only delegates one
   supported ONNX invocation to existing composition; it creates no export or
   lifecycle ownership.
4. Implementer runs the declared pre-merge validation, confirms only `Written`
   pre-merge paths changed and every `ReadOnly`/`Modify` path is untouched, then
   truthfully updates implementation entries in the step tracker.

## Validation / Acceptance Checks

### TestCase

- **Happy path**: a cache hit returns its `str` without executor/converter/remember;
  a miss follows the exact registry-to-return sequence and remembers the converted
  response.
- **Cache-context witness**: every fake `lookup` observes a call-site-created
  `object()` context; every subsequent miss `remember` observes its own newly
  created `object()` context. Captured contexts are identity-distinct (including
  lookup versus remember and across calls), are not the request or any request
  field, and are neither compared nor retained by the gateway.
- **Invalid input**: remote source and each non-ONNX family raise
  `NotImplementedError` before any collaborator observation.
- **Edge case**: `Remembered`, `Skipped`, and `Failed` each return the generated
  response; unexpected closed outcomes use `assert_never` rather than a broad
  fallback.
- **Regression**: existing cache facade operational failures remain misses;
  `src/async_model_gateway/local_response/_local_onnx_executor.py` delegates only
  to existing private composition; and package-root exports remain unchanged.
- **Backward compatibility**: `local_response` exports only its two public types;
  `ModelPayloadValue` and the three callable protocols stay non-exported; no
  registry/cache/pool/executor source or public API changes.
- **Failure/cancellation/concurrency**: registry, hasher, executor, converter, and
  `CancelledError` propagate unchanged with no later write; concurrent same-key
  misses perform separate direct-awaited executions with no shared task/lock.

Acceptance also requires plan-review and Human-clearance gates before RED, fresh RED
before implementation, approved implementation/code review before PR routing, Human
merge before release, and the bounded release review/evidence before `released`.

## Reviewer Handoff

```json
{
  "verdict": "needs-rework",
  "blocking_issues": [
    {
      "issue": "Awaiting independent Plan-Reviewer verdict.",
      "file": "plan/local-response-generation-with-cache-reuse/local-response-generation-with-cache-reuse.plan.md",
      "fix": "Replace this review-contract skeleton with the reviewer’s actual verdict."
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

After explicit Human merge and fresh release clearance, modify only the declared
release documentation/version/lockfile paths, validate every version is `0.8.0`,
create the release commit, then create/push lightweight `v0.8.0` at that exact
commit. Record the declared release evidence and review. Do not create a GitHub
Release or publish packages.

## Open Questions / Unresolved Items

None. The explicit human override supplies the absent optional analysis layer, and
all implementation, async, artifact, gate, and release decisions are frozen.

## Python Implementation Extension

### Goal

Implement the one public local ONNX response path and no broader orchestration.

### Non-goals

See `Out-Of-Scope` and `Non-Goal`: no remote path, source-boundary change,
singleflight/lifecycle policy, broad exception handling, or pre-merge release work.

### Current Context

`ModelRegistry.resolve_freshness()` already owns payload hashing and returns an
entry with `payload_hash`. `ResponseCache.lookup()` converts known operational
failures to `CacheMiss`, while `remember()` returns closed write outcomes.
`_LocalRuntimeComposition.execute()` already executes a caller-supplied
`ModelArtifact` and invocation through the private ONNX binding. No public local
response entrypoint currently exists.

### Requirements

1. The package exports exactly `LocalResponseGateway` and `LocalResponseRequest`.
2. Request fields, frozen/slotted behavior, non-exported recursive payload alias,
   method signature, exact constructor/callable seams, local/ONNX guards,
   namespace, fresh cache-context sentinel policy, and operation order match
   `Locked Decisions`.
3. A cache hit returns before execution/conversion/write; a miss performs exactly
   one direct executor await, conversion, and outcome-matched remember call.
4. All specified failures/cancellation propagate unchanged and concurrent misses
   remain independent.
5. Focused/full tests, strict Pyright, Ruff, lock check, and diff check pass;
   release validation later proves all version sources say `0.8.0`.

### Decisions

- Async-planning status: triggered — cite trigger evidence: new async
  `generate()`, async registry/cache/executor collaborators, response-cache
  failure behavior, caller-owned cancellation, and concurrent miss policy.
- Module/package placement: new `local_response/request.py`, `gateway.py`,
  `_local_onnx_executor.py`, and package initializer only. The private adapter
  consumes existing private composition without moving its ownership, exposing a
  public surface, or adding lifecycle behavior.
- New public API: yes — `LocalResponseRequest` and
  `LocalResponseGateway.generate(*, request: LocalResponseRequest) -> str`.
- Interface changes: no existing interface changes; a new direct-import
  subpackage is added and root package remains unchanged.
- Breaking changes allowed: no; all current public boundaries remain compatible.
- New dependencies: no; use existing standard-library typing/dataclasses,
  `typing_extensions.assert_never`, and existing project dependencies.
- Error handling strategy: source/family guard raises `NotImplementedError`; known
  cache facade outcomes are matched; all other specified exceptions and
  cancellation propagate without translation.
- Typing strategy: strict annotations, `Mapping[str, str]`, the exact three
  private callable protocols, the exact non-exported recursive
  `ModelPayloadValue: TypeAlias`, no `Any`, and only a line-local named private-
  usage suppression if strict Pyright reports the intentional default-composition
  import.

#### Async boundary decision

Only `generate()` and collaborator calls are async. Request construction, guards,
feature hashing, key construction, and conversion remain synchronous; no domain
boundary is converted to async beyond the gateway coordinator.

#### Resource lifecycle decision

The gateway owns no pool, session, task, semaphore, close, or unload lifecycle.
The optional executor seam is caller-owned; the private adapter in
`_local_onnx_executor.py` delegates to the existing composition owner only and
does not add a cleanup surface.

#### Concurrency model

Every call directly awaits registry, lookup, executor, and remember in sequence.
Same-key callers intentionally execute independent misses. No task creation,
gather, lock, queue, retry, batching, streaming, or background work is allowed.

#### Failure model

The existing cache facade alone classifies cache operational lookup/write cases.
The gateway only matches its closed outcomes; registry, hasher, executor, converter,
unexpected defects, and cancellation retain their original exception identity.

#### Cancellation / timeout policy

The caller owns cancellation. `CancelledError` is not caught, shielded, delayed, or
written through; there is no timeout or retry policy.

#### Validation plan

Fresh async pytest coverage records ordering and non-calls, failure/cancellation
cutoffs, and independent concurrent misses. Strict type witness proves request and
constructor seams; GREEN includes focused/full pytest, topic/global Pyright, Ruff,
lock, and diff checks.

#### Handoff notes for the implementer

Keep both guards above every collaborator call. Preserve the two explicit
`match/case` blocks and their `assert_never` fallback. Put a fresh literal
`context=object()` at each lookup and post-miss remember call; do not retain,
compare, export, or substitute request data for either sentinel. Never turn cache
misses into a catch-all policy or add singleflight/timeout/retry behavior.

#### Async contradiction log

No async contradictions. The approved contract explicitly selects direct awaits,
caller-owned cancellation, and independent concurrent misses.

### Public Contract / API Changes

New direct-import package only:

```python
class LocalResponseGateway:
    def __init__(
        self,
        *,
        registry: ModelRegistry,
        response_cache: ResponseCache,
        hash_features: _FeatureHasher,
        convert_onnx_result: _OnnxResultConverter,
        executor: _LocalResponseExecutor | None = None,
    ) -> None: ...

    async def generate(self, *, request: LocalResponseRequest) -> str: ...
```

`LocalResponseRequest` has the exact fields shown in `Locked Decisions`, including
the request.py-local `ModelPayloadValue` alias. Constructor collaborators are
keyword-only, and its three callable annotations are the non-exported private
protocols frozen above. There is no root re-export, remote method, compatibility
adapter, or change to any existing signature.

### Affected Files / Modules

Likely affected files are exactly the `Written` and `Modify` rows in `Artifact
Paths`. `ReadOnly` rows are inspected as integration inputs only; all other paths
are out of contract.

### Implementation Steps

Use the four canonical pre-merge steps above. RED test authoring occurs before
production code; release actions remain only under `Post-merge / release actions`.

### Test Plan

Use every `TestCase` category above. The focused behavior suite must additionally
assert call order, exact cache key fields, fresh distinct lookup/remember context
sentinels that are not request data, hit short-circuiting, every remember outcome,
the `_local_onnx_executor.py` private adapter's delegation-only behavior, original
exception/cancellation identity, and two independent concurrent same-key miss
executions. The strict witness uses direct static imports:

```python
from async_model_gateway.local_response import LocalResponseGateway, LocalResponseRequest
```

It supplies typed callable collaborators to prove the constructor seams and a
nested payload to prove the request alias, without importing or exporting the
private protocols or `ModelPayloadValue`. Tests use ordinary static imports only;
dynamic module loading is prohibited.

### Validation Commands

```bash
uv run pytest --no-cov tests/local_response -v
uv run pytest -v
uv run pyright --project plan/local-response-generation-with-cache-reuse/pyrightconfig.json
uv run pyright
uv run ruff check src tests plan/local-response-generation-with-cache-reuse
uv lock --check
git diff --check
```

Release-only:

```bash
rg -n '0\.8\.0' README.md docs/architecture.md docs/specs/core-abstractions-boundary.md docs/specs/orchestrator-boundary.md docs/specs/response-cache-boundary.md docs/specs/model-side-boundary.md pyproject.toml src/async_model_gateway/__version__.py uv.lock
uv lock --check
```

### Risks

Reordering registry/hash/cache operations can create incorrect cache identity;
catching facade or cancellation failures would obscure the frozen failure model;
adding shared-miss coordination would silently change execution cost/lifecycle;
release wording could overstate remote or broader orchestration support.

### Rollback Plan

Before merge, revert only the declared `Written` pre-merge sources/tests/type/gate
artifacts and leave every `ReadOnly` path untouched. After `v0.8.0` exists, never
retarget or delete it; correct release wording or behavior in a new bounded topic.

### Open Questions

None.
