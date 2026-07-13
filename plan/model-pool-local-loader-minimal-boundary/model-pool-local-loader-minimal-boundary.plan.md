> Semantic warning: `analysis/model-pool-local-loader-minimal-boundary/requirements.md`
> 與 `analysis/model-pool-local-loader-minimal-boundary/technical-spec.md` 均不存在。
> 本 revision 依據人類明確鎖定的 internal-seam correction 與現有
> `model_runtime` / `model_artifact` contract；不得以此補齊 broader runtime scope。

# model-pool-local-loader-minimal-boundary

## Goal / Outcome

- 維持 `async_model_gateway.model_runtime.model_pool.ModelPool` 的最小 public
  local runtime-model acquisition boundary，將 private `LocalModelLoader` 改為
  由 type-checker-aware `assert_never(...)` 收束的 explicit `match/case`
  family-dispatch structure。
- `model_artifact` 僅被消費；`LocalModelLoader.load(...) -> object` 只加註已鎖定
  future contract TODO，不建立 `LoadedRuntimeModel` 或任何 abstraction。

## Scope

- **In scope**:
  - 移除 private loader 的 `_route_mapping` construction/test seam 與所有
    production mapping-lookup dispatch。
  - 以 `artifact.loader_family` 的 explicit `match/case` 呼叫並 `await` 各
    `_load_<family>` private handler；目前 `PICKLE`、`TORCH`、`ONNX` 各有一個 case，
    並以 `typing_extensions.assert_never(...)` 表示 enum 窮舉後不可達的 fallback。
  - 測試 monkeypatch private family handlers，逐 branch 驗證 route，而非注入 mapping。
  - 在 `LocalModelLoader.load(self, artifact: ModelArtifact) -> object` 加入精確
    two-line TODO；重建本 revision 的 plan、RED-test、implementation-review 與
    code-review gates。
- **Out of scope**:
  - artifact I/O、serialization/framework imports、provider adapter、runtime-model
    concrete type、Protocol、provider abstraction。
  - cache/reuse、close/unload、timeout、retry、background task、fan-out、broader
    lifecycle policy。
  - `ModelGateway`、`ModelExecution`、`model_registry`、`response_cache`、
    `model_artifact` source/tests/exports/fields/vocabulary/validation，及 README、
    version、release、tag。

## Locked Decisions

- D1 verdict: `non-trivial`；此 revision changes an internal test seam and async
  dispatch structure across source, tests, spec, and workflow evidence.
- `ModelPool` remains the only `model_pool` package-root public export. Its public
  signature remains exactly `async def acquire(self, artifact: ModelArtifact) -> object`.
  No constructor injection, factory API, lifecycle method, root re-export, or
  `model_runtime` umbrella re-export is added.
- `pool.py` retains private `def _create_local_model_loader() -> LocalModelLoader`.
  `ModelPool.__init__` calls it exactly once and retains its result; `acquire(...)`
  validates `ModelArtifact` and directly awaits that loader.
- `LocalModelLoader` stays private at
  `async_model_gateway.model_runtime.model_pool._local_model_loader`; it accepts no
  `_route_mapping` or replacement injection seam. The pool factory remains a
  pool-wiring test seam only.
- `LocalModelLoader.load(self, artifact: ModelArtifact) -> object` contains exactly:

  ```python
  # TODO: Replace `object` with the agreed runtime-model contract
  # (tentatively `LoadedRuntimeModel`) once that boundary is defined.
  ```

  This is documentation only: do not create `LoadedRuntimeModel`, a Protocol, or a
  provider abstraction.
- `load(...)` reads only `artifact.loader_family` and uses explicit `match/case`:
  `LoaderFamily.PICKLE -> await self._load_pickle(artifact)`,
  `LoaderFamily.TORCH -> await self._load_torch(artifact)`, and
  `LoaderFamily.ONNX -> await self._load_onnx(artifact)`. No mapping lookup, path
  inference, content/options inference, fallback, or `KeyError` dispatch is allowed.
  `case _` must call `typing_extensions.assert_never(artifact.loader_family)`;
  it is the type-checker-aware unreachable path for the closed `LoaderFamily` enum,
  not input validation and not a new domain exception. `typing_extensions` is an
  existing runtime dependency required by the Python 3.10 baseline; do not add a
  dependency or use `typing.assert_never`.
- Known family handlers remain no-I/O and raise `NotImplementedError`. Invalid public
  `ModelPool.acquire` input remains `TypeError`; existing invalid `ModelArtifact`
  construction remains `ValueError`; route failures and `asyncio.CancelledError`
  propagate unchanged. No test or behavior contract is added for a fabricated
  non-`LoaderFamily` value at the unreachable fallback. Do not add
  `UnsupportedLocalModelLoaderError`.
- `ModelArtifact` / `LoaderFamily` are consumed-only shared read contracts; no source,
  test, export, field, vocabulary, or validation change is authorized.
- Async-planning is a focused retrofit, not a new lifecycle design: direct await,
  caller-owned cancellation, no timeout/retry, and no external resource ownership
  remain locked.
- Stable-library intent is explicit no-promotion: README, version, and release paths
  remain excluded.
- Existing plan-review, human-check, RED-test, implementation-review, and code-review
  evidence describe the superseded ValueError-fallback revision.
  They must not be treated as approval for this revision; their respective owners must
  revalidate them after plan review. The sole code-review evidence location for this
  topic is the declared `*.code-review.yaml` path below.
- A fresh code-review artifact is produced only after this revision's fresh
  implementation-review artifact is `approved`, and before `pr-comment` routing. It
  is stale if any reviewed source/test change, or any planning/spec/RED/step revision
  that changes the implementation contract, occurs after its verdict. A stale artifact
  cannot satisfy the quality gate; the Reviewer must issue a new verdict at the same
  declared path.

## Boundaries / Exclusions

- Planning actor edits only planning artifacts; Tester authors fresh RED evidence;
  Implementer changes only approved source/tests/step progress; independent reviewers
  issue plan-, implementation-, and code-review verdicts; Human alone clears human
  check and human merge gates.
- If any change needs public `LocalModelLoader`, actual artifact loading, different
  runtime-model typing, provider behavior, a new exception hierarchy, or an adjacent
  model runtime owner, stop and return to `spec-and-plan-finalization`.
- No implementation path outside the exact table below is authorized.

## Status / Allowed Transitions

- **Current**: `review-ready` — explicit-dispatch rework revision; prior approval and
  human clearance are stale and require revalidation.
- **Execution model**: `spec-and-plan-finalization -> implement-plan -> pr-comment ->
  pr-comment-review-pr-comments-and-fix`; stop at `merged`, with no `release` phase.
- **Allowed transitions**:
  - `planned` -> `creator-in-progress`
  - `creator-in-progress` -> `review-ready`
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved` | `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `creator-in-progress` | `publish-in-progress`
  - `publish-in-progress` -> `pr-open` | `merged`
  - `pr-open` -> `needs-rework` | `merged`

  `implement-plan` may start only after a fresh approved plan-review artifact and
  fresh human-check clearance. RED tests are the mandatory first Python subphase. A
  fresh approved implementation-review artifact is required before the independent
  code review; only a fresh `approved` code-review artifact permits `pr-comment`
  routing. Any covered revision after either reviewer verdict resets that verdict and
  returns routing to the applicable earlier gate.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.plan.md` | Planning actor | execution contract |
| Python spec | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.spec.md` | Planning actor | behavior contract |
| Step tracking | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.step.md` | Implementer | progress/gate tracking |
| Plan review | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.plan-review.json` | Plan-Reviewer | fresh planning verdict |
| Human check | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.human-check.json` | Human | fresh clearance into implement-plan |
| RED-test evidence | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.red-tests.yaml` | Tester | fresh first-subphase evidence |
| Implementation review | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.implementation-review.yaml` | Reviewer | fresh plan-conformance gate |
| Code review | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.code-review.yaml` | Reviewer | sole fresh Python-quality verdict after implementation review, before PR routing |
| Package root | `src/async_model_gateway/model_runtime/model_pool/__init__.py` | Implementer | `ModelPool` re-export only |
| Public pool | `src/async_model_gateway/model_runtime/model_pool/pool.py` | Implementer | public acquisition / retained loader |
| Private loader | `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` | Implementer | explicit family dispatch |
| Package tests | `tests/model_runtime/model_pool/test_model_pool_package_surface.py` | Tester | public surface / TODO regression |
| Pool tests | `tests/model_runtime/model_pool/test_model_pool.py` | Tester | acquire wiring/failures/cancellation |
| Loader tests | `tests/model_runtime/model_pool/test_local_model_loader.py` | Tester | every `match/case` branch / default handlers |

`README.md`, `pyproject.toml`, `src/async_model_gateway/__version__.py`, `uv.lock`,
`docs/architecture.md`, all `model_artifact` paths, root package paths,
`model_registry`, and `response_cache` are explicit no-change paths. Evidence rows
are routing declarations only; the planning actor does not write reviewer or Human
artifacts.

## Implementation Steps

1. Tester replaces `_route_mapping`-based tests in the three declared test files and
   writes fresh RED evidence: assert the exact two-line TODO, monkeypatch each private
   `_load_pickle`, `_load_torch`, and `_load_onnx` handler with distinct async results,
   and prove each `LoaderFamily` follows only its own explicit branch. Retain package
   surface, pool-factory retention, applicable TypeError/ValueError validation, default
   NotImplementedError, route-failure, cancellation, and path-appearance coverage.
   Remove the fabricated unforeseen-family `ValueError` expectation; tests must not
   reference `_route_mapping` or use dynamic module loading.
2. Implementer revises `_local_model_loader.py`: remove mapping types, construction
   parameter, helper validation, stored mapping, and lookup dispatch; add the exact
   TODO; implement the three explicit `match/case` branches with `await`ed matching
   private handlers; retain no-I/O handler `NotImplementedError`; import
   `assert_never` from `typing_extensions` and make `case _` call
   `assert_never(artifact.loader_family)`.
3. Implementer updates `pool.py` and `__init__.py` only as needed to conform to the
   removed private constructor seam, preserving ModelPool's locked public contract,
   factory-once retention, TypeError validation, direct await, and package-root export.
4. Implementer runs the declared targeted pytest, full pytest, ruff, and pyright
   commands and marks only the completed implementation steps in the step artifact.

## Validation / Acceptance Checks

- `LocalModelLoader.load` has exactly the specified signature and two-line TODO;
  neither `LoadedRuntimeModel` nor a Protocol/provider abstraction exists.
- Production dispatch contains explicit `match artifact.loader_family` cases for all
  three current families. Each case directly awaits only its matching private handler;
  no `_route_mapping`, mapping lookup, or `KeyError` dispatch remains. The only
  fallback is `typing_extensions.assert_never(artifact.loader_family)`, preserving
  static enum exhaustiveness rather than defining a runtime invalid-family policy.
- Tests monkeypatch the three private handler methods and demonstrate every branch,
  path-independent family choice, default `NotImplementedError`, TypeError/ValueError
  surfaces that remain applicable, unchanged route failures, and unchanged cancellation;
  they do not fabricate an unforeseen family or expect `ValueError` from the
  unreachable fallback.
- `ModelPool` public API, one-time factory retention, public exports, direct await,
  `model_artifact` consumed-only contract, and all scope exclusions remain unchanged.
- Before `pr-comment`, the Reviewer records an independent code-quality verdict at
  `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.code-review.yaml`
  only after the fresh implementation-review artifact is `approved`. Acceptance
  requires that sole artifact to contain `verdict: approved`, the seven
  `python-code-review` finding dimensions, and evidence that no covered revision has
  occurred since review; `needs-rework`, absence, or staleness returns to the
  applicable rework gate and cannot enter PR routing.
- Targeted validation: `uv run pytest --no-cov tests/model_runtime/model_pool -v`.
  Full coverage gate: `uv run pytest -v`. Static gates: `uv run ruff check src tests
  plan/model-pool-local-loader-minimal-boundary` and `uv run pyright`.

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

Plan-Reviewer must treat the existing reviewer/human evidence as stale, verify the
explicit-dispatch contract and paths above, including the sole future code-review
evidence path, and emit a new verdict before any fresh human check or RED-test phase.
After fresh implementation review is `approved`, hand off to an independent Reviewer
for `python-code-review`; that Reviewer writes only
`plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.code-review.yaml`
with `verdict: approved|needs-rework`, `tooling_detected`, and all seven findings
dimensions. Only its fresh `approved` verdict hands the topic to `pr-comment`; a
`needs-rework` verdict or later covered revision returns the topic to rework and
requires a replacement verdict at that same path.

## Post-merge / release actions

- No release workflow required. After merge, stop; all wider local-loader behavior is
  a separate topic.

## Open Questions / Unresolved Items

- None.

## Non-goals

- No artifact file read, pickle/torch/onnx integration, concrete runtime-model type,
  Protocol, or provider abstraction.
- No cache/reuse, close/unload, sharing, timeout, retry, batching, fan-out, or
  background ownership.
- No ModelGateway, ModelExecution, registry/cache integration, model_artifact change,
  new domain exception, README/version/release/tag change.

## Requirements

1. `ModelPool.acquire` remains the sole new public local acquisition method.
2. `LocalModelLoader` remains private and dispatches each current family through its
   matching explicit `match/case` branch only.
3. The exact TODO records future typing without creating the deferred contract.
4. Default handlers remain no-I/O `NotImplementedError`; applicable invalid input uses
   existing TypeError/ValueError validation, the enum fallback is `assert_never(...)`,
   and async failures/cancellation are unwrapped.
5. Tests cover happy path, invalid input, edge case, regression, backward
   compatibility, and async safety without dynamic loading.

## Decisions

- Async-planning status: triggered — cite trigger evidence: the existing public
  `async ModelPool.acquire(...)` directly awaits a private loader and this revision
  preserves cancellation/failure routing.
- Module/package placement: only the three declared `model_pool` source paths and
  three declared test paths may change.
- New public API: none; existing `ModelPool.acquire(...) -> object` is preserved.
- Interface changes: private mapping seam removed; no public contract expansion.
- Breaking changes allowed: no public breaking change; the locked internal test seam
  is deliberately replaced and must be re-reviewed.
- New dependencies: none.
- Error handling strategy: TypeError for non-ModelArtifact acquire input, existing
  ValueError validation for invalid artifact construction, NotImplementedError for
  known no-I/O families, `assert_never(...)` for the statically unreachable enum
  fallback, and unwrapped route exceptions/cancellation; no domain exception.
- Typing strategy: keep `object`; record only the exact deferred-contract TODO.

### Async boundary decision

`ModelPool.acquire` and `LocalModelLoader.load` stay async. `load` performs one direct
await of its selected private handler; no external I/O is introduced.

### Resource lifecycle decision

`ModelPool` owns one retained in-memory loader returned by its private factory. No
external resource exists, so no close/unload/context-manager surface is added.

### Concurrency model

One acquisition directly awaits one matching handler. No task creation, fan-out,
locks, queue, semaphore, batching, cache, or coalescing is established.

### Failure model

Known selected family handlers raise `NotImplementedError` until later I/O work. The
closed enum's fallback calls `assert_never(...)`; it does not define support or
validation behavior for fabricated family values. Route result and exception surfaces
remain unwrapped.

### Cancellation / timeout policy

Caller owns cancellation. Neither boundary catches `asyncio.CancelledError`; no timeout
or retry wrapper is introduced.

### Validation plan

Monkeypatch each private family handler and assert every explicit branch independently,
then validate retained loader wiring and unchanged error/cancellation behavior. Run all
four declared commands before fresh implementation review.

### Handoff notes for the implementer

Use the exact TODO, direct `match/case`, and matching `_load_<family>` awaits. Do not
replace the removed mapping seam with another injection mechanism or add deferred
types/exceptions. Stop if a required edit is outside declared paths.

### Async contradiction log

None: user-locked direct-await/no-I/O/caller-cancellation baseline is unchanged; only
the internal dispatch/test seam is corrected.

## Public Contract / API Changes

- No new public API or public signature change.
- `ModelPool` remains package-root public; `LocalModelLoader` and family handlers stay
  private. Removal of `_route_mapping` is an intentional internal seam change only.

## Affected Files / Modules

- `src/async_model_gateway/model_runtime/model_pool/__init__.py`
- `src/async_model_gateway/model_runtime/model_pool/pool.py`
- `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`
- `tests/model_runtime/model_pool/test_model_pool_package_surface.py`
- `tests/model_runtime/model_pool/test_model_pool.py`
- `tests/model_runtime/model_pool/test_local_model_loader.py`

## Test Plan

- Happy path: monkeypatch each private family handler with distinct async sentinel
  result and verify its corresponding `LoaderFamily` case only.
- Invalid input: non-artifact acquire input is TypeError; existing invalid artifact
  construction remains ValueError without a new exception class. Tests do not
  manufacture a non-`LoaderFamily` fallback input.
- Edge case: a PICKLE artifact path ending in `.onnx` still reaches `_load_pickle`.
- Regression: exact TODO remains; `_route_mapping` is absent; factory retention and
  ModelPool-only package export remain locked.
- Backward compatibility: root, umbrella, and model_artifact exports remain unchanged.
- Async safety: known default handlers raise NotImplementedError and generic failure /
  `asyncio.CancelledError` propagate unchanged.

## Validation Commands

```bash
uv run pytest --no-cov tests/model_runtime/model_pool -v
uv run pytest -v
uv run ruff check src tests plan/model-pool-local-loader-minimal-boundary
uv run pyright
```

## Risks

- A replacement injection seam or mapping lookup would make test and production
  dispatch diverge again.
- A catch, runtime fallback policy, or replacement exception around a handler would
  alter failure/cancellation semantics and undermine closed-enum exhaustiveness.
- Actual loading or typing abstraction would widen this bounded topic.

## Rollback Plan

- Revert the three declared model_pool source files, three test files, and this topic's
  plan/spec/step/evidence artifacts as applicable. Do not alter `model_artifact`.
