> Semantic warning: `analysis/local-runtime-handle-ownership-clarification/requirements.md`
> 與 `analysis/local-runtime-handle-ownership-clarification/technical-spec.md` 均不存在。
> 本 plan 依 Human 已鎖定 contract 與 parent baseline
> `feat/andrew/onnx-local-runtime-acquisition` at `31a3d1d` 撰寫；analysis layer
> 為 incomplete-layer mode，不得據此擴張為 executable runtime model、provider
> adapter，或重新設計 invocation contract。

# local-runtime-handle-ownership-clarification

## Goal / Outcome

- 移除 `LocalModelLoader` 對 runtime-model module private factory 的跨 boundary
  依賴，並將 private `_LocalLoadedRuntimeModel` 的 concrete construction ownership
  收斂至 `model_pool/_local_model_loader.py`。
- 完成後 `LoadedRuntimeModel` 仍是 public、generic、opaque acquisition handle；
  `ModelPool.acquire(...) -> LoadedRuntimeModel[object]`、`ModelExecution` public
  API 與唯一 production `_provider_runtime()` consumption responsibility 都維持不變。

## Scope

### In scope

- 從 `runtime_model/loaded_runtime_model.py` 移除 private
  `_LocalLoadedRuntimeModel` 與 `_create_loaded_runtime_model(...)`，只保留 abstract
  `LoadedRuntimeModel[RuntimeT]`、`loader_family` 與 private provider handoff
  contract。
- 在 `_local_model_loader.py` 宣告 private
  `_LocalLoadedRuntimeModel(LoadedRuntimeModel[object])`，由 `_load_onnx(...)`
  direct instantiate；不使用 `reportPrivateUsage` suppression。
- 將既有 tests/type fixtures 改為 test-local concrete handles，並以 production-tree
  governance coverage 固定：`ModelExecution` 是唯一 `_provider_runtime()` caller，
  loader 不得 import/call已移除 factory。
- 更新 `docs/specs/model-side-boundary.md`，明確記錄 opaque acquisition-handle
  semantics、loader-local construction ownership，以及 `ModelExecution` invocation
  ownership。
- 建立本 topic 的 plan、spec、step、plan-review、human-check、RED、
  implementation-review、code-review 與 topic Pyright config artifacts。

### Out of scope

- 新增 `execute(...)`、`RuntimeModel` rename/alias/deprecation、`ExecuteRequest`、
  `ExecuteResult`、ONNX invoker、provider adapter/strategy、tensor schema、batching 或
  preprocessing。
- 改動 `ModelExecution` public API、generic injected-invoker/direct-await semantics、
  exception/cancellation propagation，或讓 consumer 直接取得 provider runtime。
- 變動 ONNX acquisition helper、optional dependencies、CPU provider policy、
  `ModelArtifact`、`LoaderFamily`、`ModelPool` API、package exports、PICKLE/TORCH
  fail-closed behavior、lifecycle/cache/remote/orchestrator behavior。
- README、`docs/architecture.md`、version、release、commit、push 或 PR。

## Locked Decisions

- `LoadedRuntimeModel` 是 acquisition layer 的 opaque provider handle，不是可執行
  的 application runtime model；本 topic 不新增 public execution abstraction。
- `LoadedRuntimeModel` 名稱、package import/export、covariant generic parameter、
  public `loader_family` property 和 non-public `_provider_runtime()` abstract handoff
  均保留。
- `_LocalLoadedRuntimeModel` 只存在於
  `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`，以
  `LoaderFamily` 與 erased `object` provider model 保存本地 acquisition 結果。
- `_load_onnx(...)` 在 provider session acquisition 後直接建構 loader-local handle；
  不再 import、call 或 suppress runtime-model private factory usage。
- `ModelExecution.execute(...)` 是唯一 production source 可呼叫
  `_provider_runtime()` 的位置；它仍只 direct-await caller supplied typed async
  invoker，沒有 provider-specific dispatch/inference semantics。
- Tests/type fixtures 可以定義 test-local concrete `LoadedRuntimeModel` subclass，
  但 production code 不得新增 consumer escape hatch 或 factory replacement。
- stable-library intent 明確缺席：不改 README/version，不 release；merge 後停止。
- D1 verdict: `non-trivial`。此 topic 改動跨 module private ownership、public opaque
  type contract、type fixtures、source-governance tests 與 model-side boundary docs。

## Boundaries / Exclusions

- Plan-Creator 只建立/更新 planning artifacts；Tester 只建立 RED tests/evidence；
  Implementer 只修改 declared source/docs paths；Reviewer 與 Plan-Reviewer 只提供
  independent verdict；Human 只關閉 human gates。
- `LoadedRuntimeModel` 的 executable redesign、provider-specific adapter 或 execution
  dispatch 另立 topic；不得在本 topic 以 rename、temporary `execute`、deprecated
  escape hatch 或 public factory 偷渡。
- tests 不得使用動態模組載入；完整 production-tree ownership assertion 必須以 static
  source/AST inspection 實作，且不可把 test-only `_provider_runtime()` overrides 誤判為
  production consumers。
- 所有 implementation/test/docs changes 必須限於 Artifact Paths；需要修改未列檔案、
  public contract、dependency 或 release intent 時，回到 `spec-and-plan-finalization`。

## Status / Allowed Transitions

- **Current**: `review-ready`；Plan-Creator 已建立 plan/spec/step，等待獨立
  Plan-Reviewer verdict。
- **Execution model**: `spec-and-plan-finalization -> implement-plan -> pr-comment ->
  pr-comment-review-pr-comments-and-fix`；本 topic 在 `merged` 停止，沒有
  `release` workflow。
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

- 進入 `implement-plan` 前，必須有 declared plan-review artifact 的 `approved`
  verdict 與 Human 寫入的 `human-check`；chat approval 或 green checks 不構成 gate。
- Python RED test authoring 是 `implement-plan` 的第一個 mandatory subphase；任何
  production/docs change 前，Tester 必須產出 fresh RED evidence。
- scope、private ownership placement、public contract、test governance、documentation
  wording、dependency 或 release intent 漂移，皆返回 `spec-and-plan-finalization`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.plan.md` | Plan-Creator | Repo-visible execution contract |
| Python spec | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.spec.md` | Plan-Creator | Non-trivial behavior contract |
| Step tracker | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.step.md` | Plan-Creator, then phase owner | Workflow and implementation progress |
| Plan review | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.plan-review.json` | Plan-Reviewer | Independent planning verdict |
| Human check | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.human-check.json` | Human | Explicit clearance for `implement-plan` |
| RED evidence | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.red-tests.yaml` | Tester | Fresh pre-production test/type evidence |
| Topic Pyright config | `plan/local-runtime-handle-ownership-clarification/pyrightconfig.json` | Tester | Strict static-fixture routing |
| Implementation review | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.implementation-review.yaml` | Reviewer | Plan-conformance verdict |
| Code review | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.code-review.yaml` | Reviewer | Independent quality and boundary verdict |
| Runtime-model contract | `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py` | Implementer | Abstract opaque handle and private handoff only |
| Local loader | `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` | Implementer | Loader-local concrete handle and ONNX handoff |
| Model-side spec | `docs/specs/model-side-boundary.md` | Implementer | Ownership and opaque-handle documentation |
| Runtime-model tests | `tests/model_runtime/runtime_model/test_loaded_runtime_model.py` | Tester | Abstract contract and removed-factory regression |
| Runtime-model package tests | `tests/model_runtime/runtime_model/test_runtime_model_package_surface.py` | Tester | Unchanged public import/export surface |
| Local-loader tests | `tests/model_runtime/model_pool/test_local_model_loader.py` | Tester | Local construction, routing, annotations, and no-factory regression |
| Model-pool tests | `tests/model_runtime/model_pool/test_model_pool.py` | Tester | Opaque acquisition compatibility with test-local handles |
| ONNX acquisition tests | `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py` | Tester | ONNX handle provenance and unchanged execution handoff |
| Model-execution package tests | `tests/model_runtime/model_execution/test_model_execution_package_surface.py` | Tester | Production-tree `_provider_runtime()` caller governance |
| Generic-erasure type fixture | `tests/typecheck/runtime_model_generic_erasure.py` | Tester | Static generic opaque-handle assertions without factory |
| Execution type fixture | `tests/typecheck/model_execution_minimal_consumption.py` | Tester | Static `ModelExecution` contract assertions without factory |

### ReadOnly

- `src/async_model_gateway/model_runtime/model_pool/pool.py`
- `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py`
- `src/async_model_gateway/model_runtime/model_execution/execution.py`
- `src/async_model_gateway/model_runtime/runtime_model/__init__.py`
- `src/async_model_gateway/model_runtime/model_artifact/artifact.py`
- `src/async_model_gateway/model_runtime/model_artifact/loader_family.py`
- `tests/model_runtime/model_execution/test_model_execution.py`
- `tests/typecheck/onnx_local_runtime_acquisition.py`
- `README.md`
- `docs/architecture.md`
- `src/async_model_gateway/__version__.py`
- all parent topic artifacts under `plan/onnx-local-runtime-acquisition-minimal-boundary/`

### Written

- The nine topic-local planning, review, human-gate, evidence, and Pyright artifacts
  listed above.

### Updated

- The eleven source/doc/test/type-fixture paths listed above from Runtime-model contract
  through Execution type fixture, excluding planning artifacts.

### Deleted

- None. `_LocalLoadedRuntimeModel` and `_create_loaded_runtime_model(...)` are removed
  symbols inside an updated file, not deleted paths. Any path deletion is plan drift.

Artifact path notes:

- 此 topic 不修改 README、package/root exports、version、dependencies、lockfile 或
  release artifacts。
- listed paths are the executable contract. A later need outside these paths stops work
  and returns to `spec-and-plan-finalization`.

## Implementation Steps

1. Tester first updates the six declared runtime-model/model-pool/model-execution test
   files and two type fixtures, adds the topic Pyright config, and records fresh focused
   pytest/Pyright RED evidence. Test doubles must be local concrete subclasses; no
   dynamic module loading or runtime-model private factory use is allowed.
2. Implementer narrows `loaded_runtime_model.py` to the abstract generic opaque-handle
   contract by removing its concrete local class and factory, while preserving the
   existing public export and abstract private handoff signature.
3. Implementer adds the private concrete `LoadedRuntimeModel[object]` implementation
   inside `_local_model_loader.py`; `_load_onnx(...)` directly instantiates it after the
   unchanged helper await. Explicit family routing, `assert_never`, ONNX semantics, and
   PICKLE/TORCH fail-closed behavior remain unchanged.
4. Implementer updates `docs/specs/model-side-boundary.md` to distinguish opaque local
   acquisition from `ModelExecution` invocation and record loader-local construction;
   it must not imply executable adapters or inference support.
5. Implementer runs declared validation, verifies only declared paths changed, updates
   actual step progress, and hands evidence to independent Reviewer. It must not author
   reviewer/human artifacts or close those gates.

## Validation / Acceptance Checks

- Plan/spec/step exist, use the exact topic name, record parent baseline
  `feat/andrew/onnx-local-runtime-acquisition` at `31a3d1d`, and expose the incomplete
  analysis-layer warning.
- `LoadedRuntimeModel` remains abstract and generic; package imports/exports and
  `ModelPool.acquire(...) -> LoadedRuntimeModel[object]` remain unchanged.
- The runtime-model source no longer defines `_LocalLoadedRuntimeModel` or
  `_create_loaded_runtime_model`; the local loader directly constructs its private
  erased concrete handle and contains no private-factory import/suppression.
- An AST/source-governance test scans production Python sources and proves the only
  `_provider_runtime()` call expression occurs in
  `model_execution/execution.py`; test-local subclasses are excluded from that claim.
- Existing ONNX acquisition still yields an opaque ONNX-family handle whose provider
  identity reaches the injected `ModelExecution` invoker, while no loader inference or
  provider dispatch is introduced.
- Picky static fixtures stay strict and do not import private production factories.
- Run:

```bash
uv run pytest --no-cov tests/model_runtime/runtime_model tests/model_runtime/model_pool tests/model_runtime/model_execution -v
uv run pyright --project plan/local-runtime-handle-ownership-clarification/pyrightconfig.json tests/typecheck/runtime_model_generic_erasure.py tests/typecheck/model_execution_minimal_consumption.py
uv run pytest -v
uv run ruff check src tests plan/local-runtime-handle-ownership-clarification
uv run pyright
git diff --check
```

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

No release workflow required. Merge 後停止；不得更新 README、version、tag、release
notes 或 package publication state。

## Open Questions / Unresolved Items

- None. Missing analysis artifacts are the declared semantic warning, not an implementer
  authorization to introduce new execution semantics.

## Python Implementation

### Goal

在不改變 public acquisition/execution contracts 的前提下，將 concrete local handle
的 private construction ownership 從 runtime-model contract module 移至 local loader。

### Non-Goal

- 不讓 `LoadedRuntimeModel` 變成 `RuntimeModel`，不新增 `execute(...)`。
- 不將 ONNX `InferenceSession`、provider-specific API 或 execution dispatch 暴露給
  consumer。
- 不改動 `ModelExecution` source、signature、injected invoker、failure/cancellation
  behavior，或 ONNX acquisition implementation。

### Current Context

- `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py` currently
  combines the public abstract `LoadedRuntimeModel[RuntimeT]` contract with private
  `_LocalLoadedRuntimeModel` storage and `_create_loaded_runtime_model(...)`.
- `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` currently
  imports that factory with `reportPrivateUsage` suppression after its unchanged ONNX
  helper await.
- `src/async_model_gateway/model_runtime/model_execution/execution.py` already owns the
  sole production `_provider_runtime()` call and direct-await injected-invoker seam;
  declared source changes do not modify that file.

### Requirements

1. `LoadedRuntimeModel` only defines the abstract opaque-consumption contract; it has no
   concrete local implementation/factory.
2. `LocalModelLoader` directly owns the sole production concrete local handle and
   returns it as `LoadedRuntimeModel[object]`.
3. `ModelExecution` remains the sole production `_provider_runtime()` caller and keeps
   provider identity/direct-await semantics.
4. Tests and strict fixtures prove ownership without any dynamic import or private
   factory dependency.
5. Documentation states the acquisition-handle model without claiming provider adapter
   or executable runtime-model capability.

### Decisions

- Async-planning status: exempt — cite exemption evidence: the declared changes move
  private construction only between `runtime_model/loaded_runtime_model.py` and
  `model_pool/_local_model_loader.py`; `model_execution/execution.py` and
  `_onnx_runtime_loader.py` remain ReadOnly, so no async boundary, task ownership,
  cancellation, timeout, retry, lifecycle, or concurrency behavior changes.
- Module/package placement: remove the concrete local implementation/factory from
  `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py`; place
  the sole production concrete local handle in
  `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` beside the
  family dispatch that constructs it.
- New public API: no.
- Interface changes: no. `LoadedRuntimeModel[RuntimeT]`, `ModelPool.acquire(...)`, and
  `ModelExecution` signatures remain as baseline.
- Breaking changes allowed: no; removed names were private module internals and must not
  be package exports.
- New dependencies: no.
- Error handling: no new translation; existing loader/provider/execution propagation is
  unchanged.
- Typing: concrete production loader state is deliberately `object`; strict test
  fixtures use test-local concrete types to validate generic handoff precision.

### Public Contract / API Changes

No public API changes. Public `LoadedRuntimeModel` remains the opaque acquired-model
contract, and `ModelPool.acquire(...)` remains typed as `LoadedRuntimeModel[object]`.

### Affected Files / Modules

Likely affected files:

- `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py`
- `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`
- `docs/specs/model-side-boundary.md`
- `tests/model_runtime/runtime_model/test_loaded_runtime_model.py`
- `tests/model_runtime/runtime_model/test_runtime_model_package_surface.py`
- `tests/model_runtime/model_pool/test_local_model_loader.py`
- `tests/model_runtime/model_pool/test_model_pool.py`
- `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`
- `tests/model_runtime/model_execution/test_model_execution_package_surface.py`
- `tests/typecheck/runtime_model_generic_erasure.py`
- `tests/typecheck/model_execution_minimal_consumption.py`
- `plan/local-runtime-handle-ownership-clarification/pyrightconfig.json`

Candidate files to inspect without modification:

- `src/async_model_gateway/model_runtime/model_execution/execution.py`
- `src/async_model_gateway/model_runtime/model_pool/pool.py`
- `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py`
- `tests/model_runtime/model_execution/test_model_execution.py`
- `tests/typecheck/onnx_local_runtime_acquisition.py`

### Implementation Steps

1. In `tests/model_runtime/runtime_model/test_loaded_runtime_model.py` and
   `tests/model_runtime/runtime_model/test_runtime_model_package_surface.py`, replace
   factory-dependent assertions with abstract-contract and non-export assertions; in
   `tests/typecheck/runtime_model_generic_erasure.py`, define a test-local concrete
   handle for generic handoff checks.
2. In `tests/model_runtime/model_pool/test_local_model_loader.py`,
   `tests/model_runtime/model_pool/test_model_pool.py`, and
   `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`, replace
   factory-created sentinels with test-local concrete handles while preserving existing
   ONNX provenance/routing and `ModelExecution` identity assertions. In
   `tests/typecheck/model_execution_minimal_consumption.py`, use the same test-local
   construction pattern; in
   `tests/model_runtime/model_execution/test_model_execution_package_surface.py`, add a
   production-tree AST/source assertion for the sole `_provider_runtime()` call.
3. Add `plan/local-runtime-handle-ownership-clarification/pyrightconfig.json`, run the
   focused pytest/Pyright commands, and record fresh RED evidence before production or
   documentation changes. Tests use static imports and must not introduce dynamic module
   loading.
4. In `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py`,
   delete only `_LocalLoadedRuntimeModel` and `_create_loaded_runtime_model(...)`; retain
   the covariant abstract `LoadedRuntimeModel[RuntimeT]`, `loader_family`, and
   `_provider_runtime()` signatures.
5. In `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`, define
   private `_LocalLoadedRuntimeModel(LoadedRuntimeModel[object])`, remove the private
   runtime-model factory import/suppression, and direct-instantiate the local handle in
   `_load_onnx(...)` after its unchanged `load_onnx_runtime(...)` await.
6. In `docs/specs/model-side-boundary.md`, document loader-local opaque-handle
   construction and unchanged `ModelExecution` invocation ownership; run validation and
   update only actual step/evidence state before independent review.

### Test Plan

- Happy path — `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`
  confirms existing ONNX acquisition returns an opaque ONNX-family handle and the exact
  provider identity reaches the injected `ModelExecution` invoker.
- Invalid input — `tests/model_runtime/runtime_model/test_loaded_runtime_model.py`
  confirms the abstract handle remains uninstantiable; runtime-model/local-loader tests
  confirm the removed factory is absent and cannot be depended on by production code.
- Edge case — `tests/model_runtime/model_execution/test_model_execution_package_surface.py`
  scans production call expressions so abstract/test-local `_provider_runtime()` method
  declarations are not false-positive callers, while `ModelExecution` remains exactly
  one caller.
- Regression — `tests/model_runtime/model_pool/test_local_model_loader.py` preserves
  explicit ONNX routing, `assert_never`, and PICKLE/TORCH `NotImplementedError`; no test
  permits loader inference or provider-specific execution.
- Backward compatibility — runtime-model package-surface tests, model-pool tests, and
  both type fixtures preserve the public `LoadedRuntimeModel` export, generic erasure,
  and `ModelPool.acquire(...) -> LoadedRuntimeModel[object]` / `ModelExecution` typing.

### Validation Commands

```bash
uv run --extra onnx pytest --no-cov tests/model_runtime/runtime_model tests/model_runtime/model_pool tests/model_runtime/model_execution -v
uv run --extra onnx pyright --project plan/local-runtime-handle-ownership-clarification/pyrightconfig.json tests/typecheck/runtime_model_generic_erasure.py tests/typecheck/model_execution_minimal_consumption.py
uv run --extra onnx pytest -v
uv run --extra onnx ruff check src tests plan/local-runtime-handle-ownership-clarification
uv run --extra onnx pyright
git diff --check
```

### Risks

- Moving the private concrete class can accidentally leave a hidden factory import,
  private-use suppression, or stale type fixture, which would preserve the ownership
  violation despite green behavioral tests.
- A raw-text ownership assertion can confuse abstract/test-local declarations with call
  expressions; the required production-tree AST/source test must distinguish them.
- Documentation can overstate the opaque handle as an executable provider adapter; its
  wording must remain bounded to acquisition and existing `ModelExecution` ownership.

### Rollback Plan

Revert this topic's changes to
`src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py`,
`src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`,
`docs/specs/model-side-boundary.md`, all eight declared test/type-fixture files, and
`plan/local-runtime-handle-ownership-clarification/pyrightconfig.json` through the topic
commit. This restores the parent baseline's private factory ownership without altering
ONNX acquisition, dependencies, or public APIs.

### Open Questions

None.
