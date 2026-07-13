> Semantic warning: authoring 時找不到
> `analysis/model-pool-local-loader-minimal-boundary/requirements.md` 與
> `analysis/model-pool-local-loader-minimal-boundary/technical-spec.md`。
> 本 plan 依據已鎖定的人類決策、現有 `model_runtime` 與
> `model_artifact` contract 撰寫；analysis layer 為 incomplete-layer mode，
> 不得被當作擴張 scope 或重開已鎖定決策的授權。

# model-pool-local-loader-minimal-boundary

## Goal / Outcome

- 在 `async_model_gateway.model_runtime.model_pool` 建立最小、可測試的
  public `ModelPool` boundary：`async ModelPool.acquire(ModelArtifact) -> object`。
- `ModelPool` 是唯一 public local runtime-model provider / lifecycle owner；
  private `LocalModelLoader` 只負責以既有 `LoaderFamily` 做 explicit routing。
  此 slice 不讀 artifact、所有預設 route 都 fail closed，且不改變
  `model_artifact` shared read contract。

## Scope

- **In scope**:
  - 新增 `model_pool` package、public `ModelPool` 與 private
    `LocalModelLoader` collaborator。
  - 以 direct-await acquire path 消費 `ModelArtifact`，並針對
    `pickle`、`torch`、`onnx` 建立可觀測的 explicit internal routing。
  - 新增該 package 的 pytest coverage，以及 Python workflow 的 RED-test、
    step、spec 與 implementation-review evidence artifacts。

- **Out of scope**:
  - 實體 artifact read、任何 serialization / framework import、provider adapter，
    以及 runtime model 的具體型別。
  - cache/reuse、close/unload、timeout、retry、background task、fan-out 或
    broader lifecycle policy。
  - `ModelGateway`、`ModelExecution`、`model_registry`、`response_cache`、
    `model_artifact` 的欄位 / vocabulary / validation 語意，及任何 README、
    version、release、tag 變更。

## Locked Decisions

- D1 verdict: `non-trivial`；此 topic 新增 public async API、private
  collaborator wiring、三個 `LoaderFamily` route 與跨多個 source/test files。
- public owner 固定為
  `async_model_gateway.model_runtime.model_pool.ModelPool`；package root 的
  `__all__` 只可列 `ModelPool`。`async_model_gateway` 與
  `async_model_gateway.model_runtime` 都不得 re-export 它。
- public method 固定為
  `async def acquire(self, artifact: ModelArtifact) -> object`。不新增第二個
  public method、factory、Protocol、constructor injection 或 configuration API。
- `pool.py` 固定定義 private factory
  `def _create_local_model_loader() -> LocalModelLoader`，它零參數並回傳一個
  `LocalModelLoader`。`ModelPool.__init__` 每次 construction 恰呼叫此 factory
  一次，保存該次回傳的同一個 loader 至 pool instance lifetime；`acquire(...)`
  不得重建或替換它。本 topic 不提供 close、unload、sharing、cache 或 reuse
  semantics。
- private collaborator 固定置於
  `async_model_gateway.model_runtime.model_pool._local_model_loader`，不在任何
  package root re-export。其唯一 test-only mapping construction seam 固定為
  `LocalModelLoader(*, _route_mapping: Mapping[LoaderFamily, Callable[[ModelArtifact], Awaitable[object]]] | None = None)`；
  production `ModelPool` 只呼叫無參數 factory，絕不暴露此 seam。當
  `_route_mapping` 非 `None` 時，constructor 在任何 route 被 await 前驗證：
  key set 必須恰為 `set(LoaderFamily)`（不得遺漏、額外或使用非 family key），
  否則 raise `ValueError`；傳入非 `Mapping` 或任一 value 非 callable 則 raise
  `TypeError`。`pool.py` factory 是 pool-wiring test seam，僅允許 tests 以
  `async_model_gateway.model_runtime.model_pool.pool._create_local_model_loader`
  monkeypatch，不構成 public API。
- `LocalModelLoader.load(...)` 必須只讀取 `artifact.loader_family`，以明確 map
  dispatch 到對應 family route；不得從 `artifact_path`、content、options 或
  object shape 推論 family。每個 starter family 都必須有獨立且可觀測 route。
- 預設三個 family route 都在不開檔、不 import provider、不中介執行緒的前提下
  raise `NotImplementedError`；這是本 slice 的 no-I/O fail-closed outcome，
  不是 fallback 或 partial load。未來真正 loader 行為必須另開 topic。
- `acquire(...)` 對非 `ModelArtifact` input 在 routing 前 raise `TypeError`；
  route 的 `NotImplementedError`、其他 exception 與 `asyncio.CancelledError`
  都原樣傳遞，不包裝、不吞掉、不轉成 `None`。
- `ModelArtifact` / `LoaderFamily` 只被 consumed：不修改其 source、tests、
  package exports、fields、vocabulary 或 validation rules。
- 本 topic 採 Python planning extension path。stable-library metadata 是
  explicit no-promotion：README、version 與 release routing 均不變；不得因
  metadata section 存在而把它們加入 implementation paths。

## Boundaries / Exclusions

- Planning actor 僅 author planning artifacts；Tester 先產生 RED-test evidence；
  Implementer 只在 approved path contract 內實作；Reviewer 產生獨立 verdict；
  Human 單獨關閉 `human check` 與 `human merge`。
- 任何需要公開 `LocalModelLoader`、加入 loader configuration、實際 artifact I/O、
  resource cleanup、remote provider、execution 或 gateway semantics 的需求，必須
  回到 `spec-and-plan-finalization` 並另開 bounded topic。
- 若實作需要修改未列出的 source、tests、docs 或 metadata path，必須停止；不得
  用臨時 re-export、compatibility shim 或 README wording sweep 擴張本 topic。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow
  `spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix`；
  this topic stops at `merged` and does not enter `release`.
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

- `implement-plan` 只可在 plan-review artifact 為 `approved` 且 human check
  artifact 明確 cleared 後開始；Python RED test authoring 是其第一個 mandatory
  subphase。
- Reviewer 不得在 review artifact 外以聊天文字取代 verdict；Human check 和
  human merge 都不得由任何 agent 預填或推定。
- `needs-rework` 若改變 public contract、artifact paths、async baseline 或
  stable-library intent，必須回到 `spec-and-plan-finalization`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.plan.md` | Planning actor | repo-visible execution contract |
| Python spec | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.spec.md` | Planning actor | non-trivial behavior contract |
| Step tracking | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.step.md` | Implementer | Python workflow progress / gate tracking |
| Plan review | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.plan-review.json` | Plan-Reviewer | independent planning verdict |
| Human check | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.human-check.json` | Human | explicit clearance into `implement-plan` |
| RED-test evidence | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.red-tests.yaml` | Tester | mandatory first implementation subphase evidence |
| Implementation review | `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.implementation-review.yaml` | Reviewer | implementation-plan conformance gate before PR routing |
| Public package root | `src/async_model_gateway/model_runtime/model_pool/__init__.py` | Implementer | re-export only `ModelPool` |
| Public pool owner | `src/async_model_gateway/model_runtime/model_pool/pool.py` | Implementer | `ModelPool` acquire boundary and private collaborator wiring |
| Private loader collaborator | `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` | Implementer | explicit family routing and no-I/O default routes |
| Package-surface tests | `tests/model_runtime/model_pool/test_model_pool_package_surface.py` | Tester | locks exports and non-re-export boundaries |
| Pool tests | `tests/model_runtime/model_pool/test_model_pool.py` | Tester | locks acquire delegation, lifetime/wiring, failures and cancellation |
| Private-loader tests | `tests/model_runtime/model_pool/test_local_model_loader.py` | Tester | locks explicit family route matrix and no-I/O fail-closed behavior |

Artifact path notes:

- `README.md`, `pyproject.toml`, `src/async_model_gateway/__version__.py`, `uv.lock`,
  `docs/architecture.md`, all `model_artifact` files, root package files,
  `model_registry`, and `response_cache` are explicit no-change paths.
- Reviewer-owned and human-owned evidence paths are declared for routing but must not
  be pre-created or written by the planning actor or Implementer.
- Any path outside this table is a plan-alignment failure and must return to
  `spec-and-plan-finalization`.

## Stable library metadata

- `README row`: no change. This no-I/O minimal boundary does not promote README
  feature wording in this topic.
- `VERSION bump`: no bump; `pyproject.toml`, `src/async_model_gateway/__version__.py`,
  and `uv.lock` remain untouched.
- `timing`: no `publish-in-progress` metadata promotion and no release action.
- `rationale`: public API scope is deliberately bounded to the initialization-stage
  minimal boundary; versioning, README promotion, and release policy require a
  separate release-facing topic.

## Implementation Steps

1. Tester adds RED coverage in `tests/model_runtime/model_pool/test_model_pool_package_surface.py`, `test_model_pool.py`, and `test_local_model_loader.py`, then records the failing contract in `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.red-tests.yaml`: only `ModelPool` is package-public; construct `LocalModelLoader(_route_mapping=...)` with a complete mapping containing exactly the three `LoaderFamily` keys and unique async sentinel routes; monkeypatch `async_model_gateway.model_runtime.model_pool.pool._create_local_model_loader` before `ModelPool()` construction with a zero-argument callable returning that loader; assert factory-once retention, direct family routing, no-I/O default failures, and the locked invalid-input, mapping-validation, route-failure, and cancellation surfaces.
2. Implementer adds `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` with private `LocalModelLoader(*, _route_mapping=...)`: a supplied mapping must have all and only `LoaderFamily` keys before any route is awaited (`ValueError` otherwise), while a non-`Mapping` or non-callable route value raises `TypeError`; it dispatches explicitly and supplies no-I/O defaults that raise `NotImplementedError`.
3. Implementer adds `src/async_model_gateway/model_runtime/model_pool/pool.py` and `__init__.py`: define `def _create_local_model_loader() -> LocalModelLoader`, have each `ModelPool.__init__` call it exactly once and retain that returned instance, have `acquire(...)` validate `ModelArtifact` then directly await the retained loader, and re-export only `ModelPool` from the topic package root.
4. Implementer runs `uv run pytest --no-cov tests/model_runtime/model_pool -v` for targeted behavior validation, `uv run pytest -v` as the repository-wide coverage gate, `uv run ruff check src tests plan/model-pool-local-loader-minimal-boundary`, and `uv run pyright`; after all pass, update only the Implementer-owned progress in `plan/model-pool-local-loader-minimal-boundary/model-pool-local-loader-minimal-boundary.step.md`.

## Validation / Acceptance Checks

- All canonical topic-plan sections, status transitions, declared artifact paths, and
  reviewer handoff JSON match `plan/agent-handoff-workflow.md` and
  `plan/topic-plan-contract.md`.
- Package root re-exports exactly `ModelPool`; root package, `model_runtime` umbrella,
  and `model_artifact` do not re-export `ModelPool` or `LocalModelLoader`.
- `inspect.signature(ModelPool.acquire)` is exactly async
  `acquire(self, artifact: ModelArtifact) -> object`; no extra public acquire options
  or lifecycle methods are added.
- `pool.py` defines exactly `def _create_local_model_loader() -> LocalModelLoader`.
  Tests monkeypatch exactly
  `async_model_gateway.model_runtime.model_pool.pool._create_local_model_loader`
  with a zero-argument callable before construction; each `ModelPool.__init__`
  calls it once and retains its exact returned loader for that pool lifetime.
- `acquire` delegates the same `ModelArtifact` object to that retained loader and
  returns the route's object unchanged.
- Each `LoaderFamily` value follows its own injected route; explicit family wins even
  when `artifact_path` suggests a different serialization format. No route performs
  filesystem or provider I/O in this slice.
- `LocalModelLoader(*, _route_mapping=...)` is the sole test-only mapping seam.
  A supplied mapping is validated before any route await: it has all and only the
  current `LoaderFamily` keys or raises `ValueError`; a non-`Mapping` argument or
  non-callable route value raises `TypeError`.
- Default routes raise `NotImplementedError`; non-`ModelArtifact` input raises
  `TypeError`; route exceptions and cancellation propagate unchanged. No `None`,
  fallback, cache, retry, timeout, or wrapper semantics are introduced.
- Targeted behavior validation runs `uv run pytest --no-cov
  tests/model_runtime/model_pool -v` so the package-level test result is not
  coupled to the repository-wide coverage threshold. `uv run pytest -v` then
  passes as the repository-wide coverage gate; ruff and pyright also pass.
  Tests use ordinary imports and monkeypatch only private seams; they do not use
  dynamic module loading.
- Before PR routing, independent implementation review records plan conformance in
  the declared `.implementation-review.yaml`; it does not replace the later code
  review or human merge gate.

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
- Merge 後停止；README、version、tag、release note 與 broader local-loader behavior
  都必須另開 topic。

## Open Questions / Unresolved Items

- None.

## Non-goals

- 不實作任何 artifact file read、pickle / torch / onnx provider integration 或
  runtime model concrete type。
- 不實作 pool cache/reuse、close/unload、resource sharing、timeout、retry、
  batching、fan-out 或 background ownership。
- 不新增 `ModelGateway`、`ModelExecution`、provider framework、registry/cache
  integration，亦不修改 `ModelArtifact` shared read contract。
- 不修改 README、version、release metadata、tag 或 release workflow。

## Current Context

- `src/async_model_gateway/model_runtime/__init__.py` 是無 re-export 的 umbrella
  root；唯一已落地 child module 是 `model_artifact`。
- `src/async_model_gateway/model_runtime/model_artifact/` 已公開 immutable
  `ModelArtifact` 與 explicit `LoaderFamily` (`pickle`、`torch`、`onnx`)。
  `ModelArtifact` 已保證 `artifact_path` 與 `loader_options` 的 read contract；
  本 topic 只能消費這個 contract。
- `pyproject.toml` 已啟用 strict pytest asyncio mode、ruff 與 strict pyright；
  沒有可重用的 `ModelPool`、`LocalModelLoader` 或 provider adapter implementation。

## Requirements

1. `ModelPool.acquire` 是唯一新增 public local acquisition method，並只接收
   `ModelArtifact`、回傳 `object`。
2. `LocalModelLoader` 必須保持 private，且每個 locked `LoaderFamily` 都經由
   explicit mapping route 處理，不允許 path inference。
3. 沒有 injected test route 時，三個 default route 都不得 I/O，且必須
   `NotImplementedError` fail closed。
4. async boundary 只允許 direct await；cancellation 與 route failure 必須原樣
   傳播。
5. 所有新增 tests 必須覆蓋 happy path、invalid input、edge case、regression 與
   backward compatibility，且不得使用 dynamic module loading。

## Decisions

- Async-planning status: triggered — cite trigger evidence: the locked public API is `async ModelPool.acquire(...)`, it owns an async collaborator boundary, and cancellation/failure propagation must be frozen before implementation.
- Module/package placement: add `src/async_model_gateway/model_runtime/model_pool/` with public `pool.py`, private `_local_model_loader.py`, and narrow `__init__.py`.
- New public API: yes — `class ModelPool` with `async def acquire(self, artifact: ModelArtifact) -> object`; constructor remains `ModelPool()` with no public injection parameters.
- Interface changes: no existing interface changes; `ModelArtifact` and `LoaderFamily` are imported and consumed unchanged.
- Breaking changes allowed: no; existing public surfaces remain unchanged, while `ModelPool` is a new package-local public surface only.
- New dependencies: no; use the standard library and existing project dependencies only.
- Error handling strategy: non-`ModelArtifact` input raises `TypeError`; no-I/O default routes raise `NotImplementedError`; route failures and cancellation propagate unchanged without wrapping, fallback, or `None` conversion.
- Typing strategy: strict typed annotations; `ModelArtifact` is the public argument type, `object` is the intentionally opaque return type, `_create_local_model_loader() -> LocalModelLoader` is the private pool factory contract, and `_route_mapping` uses `Mapping[LoaderFamily, Callable[[ModelArtifact], Awaitable[object]]] | None` without `Any`, public Protocols, or generic runtime-model abstraction.

### Async boundary decision

`ModelPool.acquire(...)` and private `LocalModelLoader.load(...)` are async so the
public local acquisition seam is fixed now. This slice performs one direct await
into an in-memory private route; it introduces no file, network, thread, process,
or provider async I/O.

### Resource lifecycle decision

Each `ModelPool.__init__` calls `_create_local_model_loader()` exactly once and owns
the returned `LocalModelLoader` for that pool's lifetime. The loader owns no external
resource in this slice, so neither class exposes `close`, `aclose`, unload, reset,
or context-manager behavior.

### Concurrency model

Each `acquire(...)` directly awaits one loader call. No task creation, fan-out,
locking, queue, semaphore, cache, reuse, batching, or coalescing is permitted;
concurrent-call behavior is deliberately not established.

### Failure model

The boundary validates the public argument before dispatch. After dispatch begins,
the selected route's result or exception is returned/raised unchanged. Default
routes fail closed with `NotImplementedError`; this is not a retryable fallback and
does not imply support for any serialized artifact.

### Cancellation / timeout policy

The caller owns cancellation. `ModelPool` and `LocalModelLoader` must not catch or
translate `asyncio.CancelledError`, and this slice introduces no timeout or retry
wrapper. Cleanup requirements are absent because no external resource is acquired.

### Validation plan

Async pytest tests create `LocalModelLoader(_route_mapping=...)` with a distinct
async route for each family, then monkeypatch
`async_model_gateway.model_runtime.model_pool.pool._create_local_model_loader` before
`ModelPool()` construction. They assert zero-argument factory-once retention, direct
await delegation, unchanged sentinel return, cancellation and generic route failure
propagation, plus `ValueError` for missing/extra/non-family mapping keys and
`TypeError` for non-`Mapping` or non-callable mapping input. Default-route tests prove
all families fail closed without using a file or provider seam.

Targeted behavior validation uses `uv run pytest --no-cov
tests/model_runtime/model_pool -v` so its result is independent of the
repository-wide coverage threshold. `uv run pytest -v` remains the required
full-suite coverage gate, followed by the declared ruff and pyright checks.

### Handoff notes for the implementer

Keep `_create_local_model_loader()` and `_route_mapping` private and exact; do not
rename either seam or add public injection. Do not replace the opaque `object` return
type with a runtime-model abstraction, add lifecycle methods, or make default routes
load artifacts. If a required change needs any excluded behavior, stop and return to
planning.

### Async contradiction log

No async contradictions: the locked acquire-only scope, no-I/O fail-closed routes,
direct await, caller-owned cancellation, and absence of timeout/retry are consistent
with the existing `model_runtime` umbrella and `model_artifact` read contract.

## Public Contract / API Changes

- Add `async_model_gateway.model_runtime.model_pool.ModelPool`.
- `ModelPool()` has no public configuration or lifecycle surface.
- `async def acquire(self, artifact: ModelArtifact) -> object` returns exactly the
  selected internal route's opaque object. It raises `TypeError` before routing for a
  non-`ModelArtifact`, otherwise preserves the selected route's result, exception,
  or cancellation unchanged.
- `LocalModelLoader`, `LocalModelLoader(*, _route_mapping=...)`,
  `_create_local_model_loader()`, and individual family handlers are private
  implementation details. No existing API changes and no compatibility layer are
  required.

## Affected Files / Modules

Likely affected files:
- `src/async_model_gateway/model_runtime/model_pool/__init__.py`
- `src/async_model_gateway/model_runtime/model_pool/pool.py`
- `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`
- `tests/model_runtime/model_pool/test_model_pool_package_surface.py`
- `tests/model_runtime/model_pool/test_model_pool.py`
- `tests/model_runtime/model_pool/test_local_model_loader.py`

Candidate files to inspect:
- `src/async_model_gateway/model_runtime/model_artifact/artifact.py`
- `src/async_model_gateway/model_runtime/model_artifact/loader_family.py`
- `pyproject.toml`

## Test Plan

Test files: `tests/model_runtime/model_pool/test_model_pool_package_surface.py`,
`tests/model_runtime/model_pool/test_model_pool.py`, and
`tests/model_runtime/model_pool/test_local_model_loader.py`.

Test cases:
- Happy path: construct `LocalModelLoader(_route_mapping=...)` with exactly all three
  `LoaderFamily` keys and unique async routes; monkeypatch
  `async_model_gateway.model_runtime.model_pool.pool._create_local_model_loader` with
  a zero-argument callable returning it before `ModelPool()`; `await acquire(...)`
  returns the exact corresponding sentinel and passes the same artifact object.
- Invalid input: `await acquire(object())` raises `TypeError` before the loader route;
  `_route_mapping` with a missing, extra, or non-family key raises `ValueError` before
  any route is awaited, while a non-`Mapping` input or non-callable route value raises
  `TypeError`.
- Edge case: a `PICKLE` artifact whose path ends in `.onnx` still selects the PICKLE
  route; every default family route raises `NotImplementedError` without I/O.
- Regression: monkeypatch target
  `async_model_gateway.model_runtime.model_pool.pool._create_local_model_loader` is
  called exactly once per `ModelPool()` construction; repeated calls use its same
  returned collaborator rather than creating a new loader or cache.
- Backward compatibility: only `model_pool` package re-exports `ModelPool`; root,
  umbrella, and `model_artifact` package surfaces stay unchanged, and
  `LocalModelLoader` is absent from package exports.
- Async safety: an injected generic exception and `asyncio.CancelledError` each
  propagate unchanged; no timeout, retry, or cancellation wrapper exists.

## Validation Commands

```bash
uv run pytest --no-cov tests/model_runtime/model_pool -v
uv run pytest -v
uv run ruff check src tests plan/model-pool-local-loader-minimal-boundary
uv run pyright
```

## Risks

- A seemingly harmless test injection or package re-export could expose
  `LocalModelLoader` as a second public owner, weakening the `ModelPool` boundary.
- Catching `CancelledError` or adding a fallback while making default routes more
  convenient would silently change the frozen failure and cancellation contract.
- Adding artifact I/O to satisfy a route test would broaden this minimal boundary
  into provider behavior and invalidate the no-I/O scope.

## Rollback Plan

- Revert `src/async_model_gateway/model_runtime/model_pool/__init__.py`, `pool.py`,
  `_local_model_loader.py`, the three matching test files, and this topic's
  plan/spec/step/RED-test evidence artifacts. Do not alter `model_artifact` to roll
  back this additive boundary.
