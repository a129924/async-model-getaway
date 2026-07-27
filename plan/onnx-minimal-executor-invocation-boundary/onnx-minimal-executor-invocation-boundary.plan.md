# ONNX minimal executor invocation boundary

## Goal / Outcome

完成同一個 ONNX invocation topic：local composition 以精確的
`OnnxRuntimeSession -> dict[str, object] -> list[object]` binding 呼叫 private
`_OnnxModelExecutor`，而不新增 package public API、outer erasure 或流程外設計。

## Scope

- **In scope**：私有 session Protocol 的最小 `run(...)` capability、private executor、
  ONNX loader/binding/composition 的精確 generic pairing，以及直接對應的測試和 strict
  Pyright witness。
- **Out of scope**：release、版本、README、公開 runtime API、provider framework、timeout、
  retry、cache、pool lifecycle 與其他 loader family。

## Non-goals

- 本 topic 不會 package re-export `OnnxRuntimeSession`、`_OnnxModelExecutor` 或 executor factory。
- 本 topic 不會新增 `Any`、`cast`、inline suppression、dynamic import 或 monkeypatch。
- 本 topic 不會更改 cancellation 的直接傳播、fixture strategy、release contract、版本或 lockfile。
- 本 topic 不會保留 `RuntimeBinding[object, object, object]` outer erasure。

## Current Context

`model_execution/execution.py` 已有 private generic gate/timestamp lifecycle，
`_onnx_model_loader.py` 已有唯一 optional-provider lazy-import/typing boundary，
`_runtime_binding.py` 與 `_local_runtime_composition.py` 目前仍使用 erasure 與 fail-closed
ONNX executor。`model_execution/__init__.py` 已是無 re-export 的 internal package boundary。

## Requirements

1. `runtime_model/_onnx_runtime.py` 定義 `OnnxRuntimeSession` Protocol，僅供 internal
   modules 交叉 typing；它有 `get_providers() -> list[str]` 與
   `run(list[str] | None, dict[str, object], object | None) -> list[object]`，且無 package export。
2. 新增的 `_OnnxModelExecutor` 必須 private，在 provider thread 執行固定
   `runtime.run(None, invocation, None)`，並回傳同一個 `list[object]` 結果。
3. executor 只接受 `dict[str, object]`；非 dict 或非 `str` key 在 provider work 前
   raise `TypeError`。provider exception 與 `CancelledError` 原樣傳播；取消不等待 worker、
   不新增 task ownership、timeout 或 retry policy。
4. loader、executor、binding、composition 都維持
   `OnnxRuntimeSession -> dict[str, object] -> list[object]`；resolver 和 composition
   不可使用 `RuntimeBinding[object, object, object]`。
5. `_onnx_model_loader.py` 是唯一既有 exception：保留 optional `onnxruntime`
   lazy import 和其既有 session typing refinement；不得向其他路徑擴散。
6. focused/full pytest、兩個 strict Pyright witness、global Pyright、Ruff、lock check
   與 diff check 都必須通過。

## Locked Decisions

- 本 topic 是 non-stable internal implementation；不影響 stable-library surface，沒有 release。
- Analysis-layer warning：`analysis/onnx-minimal-executor-invocation-boundary/requirements.md`
  與 `analysis/onnx-minimal-executor-invocation-boundary/technical-spec.md` 都不存在；本 plan
  以使用者明確 frozen contract 與唯讀 audit 為依據，沒有覆寫任何 analysis artifact。
- `OnnxRuntimeSession` 是 private-module internal typing vocabulary，不是 package API。
- `_OnnxModelExecutor` 是唯一 provider invocation owner；generic `ModelExecutor` 保留 gate、
  timestamp 與 direct-await lifecycle。
- invocation 在 executor 內被驗證，`asyncio.to_thread` 僅 offload synchronous provider work；
  不建立由 executor 額外持有、join 或 shield 的 background task。
- 唯一容許的既有 typing/import exception 保持在
  `model_pool/loaders/_onnx_model_loader.py`；本 topic 不變更該例外的範圍。
- D1 verdict：`non-trivial`，因為它新增 provider invocation、修改四個 internal module
  contract 並需要 async/cancellation 與 type witness coverage。

## Boundaries / Exclusions

Planning actor 寫 plan/spec/step；Reviewer 只寫 review verdict；Human 只寫 clearance；
Implementer 只在已核准的 Artifact Paths 內工作。舊 plan review、human check、RED 與
implementation review evidence 一律不是本 topic 的 gate。超出列出路徑的工作必須回到
planning，而非在 implementation 擴張。

## Status / Allowed Transitions

- **Current**：`review-ready`（fresh plan review 尚未完成）。
- **Execution model**：`spec-and-plan-finalization -> implement-plan -> pr-comment ->
  pr-comment-review-pr-comments-and-fix`；此 topic 在 merge 後結束，不進入 release。
- **Gate order**：fresh plan review approved -> fresh Human implementation clearance ->
  fresh RED -> implementation -> validations -> implementation review approved -> code review approved ->
  single commit -> push -> Ready PR -> `@codex review`。
- **Allowed transitions**：
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
| Topic plan | `plan/onnx-minimal-executor-invocation-boundary/onnx-minimal-executor-invocation-boundary.plan.md` | Planning actor | Frozen recovery contract |
| Behavior spec | `plan/onnx-minimal-executor-invocation-boundary/onnx-minimal-executor-invocation-boundary.spec.md` | Planning actor | Non-trivial behavior contract |
| Step tracker | `plan/onnx-minimal-executor-invocation-boundary/onnx-minimal-executor-invocation-boundary.step.md` | Planning actor | Fresh workflow state |
| Plan review | `plan/onnx-minimal-executor-invocation-boundary/onnx-minimal-executor-invocation-boundary.plan-review.json` | Reviewer | Fresh planning verdict |
| Human clearance | `plan/onnx-minimal-executor-invocation-boundary/onnx-minimal-executor-invocation-boundary.human-check.json` | Human | Explicit implementation clearance |
| RED evidence | `plan/onnx-minimal-executor-invocation-boundary/onnx-minimal-executor-invocation-boundary.red-tests.yaml` | Tester | Fresh pre-implementation evidence |
| Implementation review | `plan/onnx-minimal-executor-invocation-boundary/onnx-minimal-executor-invocation-boundary.implementation-review.yaml` | Reviewer | Plan-conformance verdict |
| Code review | `plan/onnx-minimal-executor-invocation-boundary/onnx-minimal-executor-invocation-boundary.code-review.yaml` | Reviewer | Quality verdict |
| Session protocol | `src/async_model_gateway/model_runtime/runtime_model/_onnx_runtime.py` | Implementer | Internal precise runtime capability |
| ONNX executor | `src/async_model_gateway/model_runtime/model_execution/_onnx_model_executor.py` | Implementer | Private invocation owner |
| Generic executor | `src/async_model_gateway/model_runtime/model_execution/execution.py` | Implementer | Remove obsolete fail-closed ONNX specialization |
| Binding resolver | `src/async_model_gateway/model_runtime/model_pool/_runtime_binding.py` | Implementer | Precise ONNX binding without erasure |
| Local composition | `src/async_model_gateway/model_runtime/_local_runtime_composition.py` | Implementer | Exact invocation/result path |
| ONNX loader | `src/async_model_gateway/model_runtime/model_pool/loaders/_onnx_model_loader.py` | Implementer | Retain the sole existing optional-provider boundary |
| Executor tests | `tests/model_runtime/model_execution/test_model_execution.py` | Tester | Invocation, error, cancellation and lifecycle coverage |
| Executor surface tests | `tests/model_runtime/model_execution/test_model_execution_package_surface.py` | Tester | Private/package/AST boundary coverage |
| ONNX regression tests | `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py` | Tester | Real CPU-only invocation regression |
| Loader tests | `tests/model_runtime/model_pool/test_onnx_model_loader.py` | Tester | Sole exception and no-erasure witness |
| Composition tests | `tests/model_runtime/test_local_runtime_composition.py` | Tester | Exact typed composition contract |
| Type witness | `tests/typecheck/onnx_minimal_executor_invocation_boundary.py` | Tester | Strict generic pairing witness |
| Witness config | `plan/onnx-minimal-executor-invocation-boundary/pyrightconfig.json` | Tester | Strict config for only this topic's two witnesses |

`README.md`、version、lockfile、CI config 與 global Pyright config 不會修改。topic-local
witness config 保持 strict、只 include 兩個 witness、且不放寬 diagnostics。任何其他路徑都是
plan alignment failure。

## Decisions

- Async-planning status: triggered — cite trigger evidence: existing `ModelExecutor.execute`,
  ONNX `asyncio.to_thread` acquisition, Semaphore lifecycle, and this topic's provider invocation
  must preserve direct cancellation propagation.
- Module/package placement: session Protocol 在 `runtime_model/_onnx_runtime.py`；provider call
  在新的 private `model_execution/_onnx_model_executor.py`。
- New public API: no；private-module symbols 不得 package re-export。
- Interface changes: yes；internal ONNX generic pairing 從 `object` 收斂為 frozen exact chain。
- Breaking changes allowed: no public break；internal fail-closed ONNX invocation 依本 topic 啟用。
- New dependencies: no；使用既有 `asyncio`、onnx optional dependency 與 test dependencies。
- Error handling strategy: invalid invocation raise `TypeError`；provider failures、
  `NotImplementedError` for other families 和 `CancelledError` 原樣傳播。
- Typing strategy: strict Protocol、generic `ModelExecutor`/`RuntimeBinding`，不用 `Any`；
  不新增 `cast` 或 suppressions，僅維持 loader 既有 optional-provider boundary。

### Async boundary decision

`ModelExecutor.execute` 與 `_OnnxModelExecutor._invoke` 保持 async，因為 session `run` 是
synchronous provider work，必須以 `asyncio.to_thread` offload；驗證與 generic gate lifecycle
保持在 event loop。

### Resource lifecycle decision

`ModelPool` 仍擁有 loaded runtime 與 Semaphore；executor 不擁有 session、thread pool 或
background task，且不新增 cleanup surface。

### Concurrency model

每個 loaded model 仍由既有 Semaphore 限制；executor 對一次 invocation direct-await
一個 `asyncio.to_thread` result，不 fan-out、不 create task、不 join detached work。

### Failure model

validation 在 provider call 前失敗；provider exception identity 原樣向 caller 傳播。沒有
provider error translation、retry 或 timeout。

### Cancellation / timeout policy

caller 擁有 cancellation；`CancelledError` 不 catch、不 delay、不轉譯。沒有 timeout；底層
thread 的既有 Python cancellation semantics 不被本 topic 改寫。

### Validation plan

RED 先證明 invocation/surface/typing requirement 缺失；GREEN 後執行 focused/full pytest、
topic strict witness、existing loader witness、global Pyright、Ruff、lock 與 diff checks。

### Handoff notes for the implementer

只移植符合 frozen contract 的 feature candidate；不要移植 cancellation worker-drain logic、
舊 evidence、其他 topic config，或 object erasure。若 typing 需要新的 exception，停止並回到 plan。

### Async contradiction log

- contradiction: 舊 feature candidate 在 cancellation 後等待 worker 與 gate release；
  frozen contract 要求 direct propagation。
  source A: feature candidate executor/tests；source B: recovery request 和 generic lifecycle。
  risk impact: cancellation latency 與 Semaphore ownership 改變。
  decision owner / next action: Planning actor；採 direct-await 並不移植 worker-drain code。
  classification: blocking until plan is approved, then resolved by this plan.

## Public Contract / API Changes

無 public API changes。`OnnxRuntimeSession` 雖以 non-underscore 名稱供 internal modules
typing，檔案本身是 private module，且所有 package initializer 維持無 re-export。

## Affected Files / Modules

Likely affected files are exactly the source and test paths in `Artifact Paths` above。候選 feature
中的其他 plan/config/evidence 檔不在範圍內，也不可移植。

## Implementation Steps

1. Tester 在 `tests/model_runtime/model_execution/test_model_execution.py`、
   `test_model_execution_package_surface.py`、`test_onnx_local_runtime_acquisition.py`、
   `test_onnx_model_loader.py`、`test_local_runtime_composition.py` 和新 type witness 寫 fresh RED
   coverage，並記錄 `red-tests.yaml`；production source 必須尚未修改。
2. Implementer 更新 `runtime_model/_onnx_runtime.py`，新增 minimal `run` Protocol capability；
   新增 private `_onnx_model_executor.py`，以 direct `await asyncio.to_thread(...)` 做固定 invocation。
3. Implementer 更新 `model_execution/execution.py` 移除 obsolete fail-closed ONNX class；更新
   `_runtime_binding.py`、`_local_runtime_composition.py` 與 `_onnx_model_loader.py` 保持 exact
   pairing，且不留 outer erasure。
4. Implementer/Tester 在列出的 source/tests/type witness 範圍內完成 GREEN，更新 step tracker；
   不修改 config、package exports 或 release files。

## Test Plan

- **Happy path**：fake session 和 committed identity ONNX fixture 都以固定 call shape 回傳原 list。
- **Invalid input**：non-dict 和 non-string key 在 provider work 前 raise `TypeError`。
- **Edge case**：cancelled invocation 立即保留 `CancelledError` identity、gate 依 generic lifecycle
  release，且 executor 不建立 managed background task。
- **Regression**：CPU-only loader session 仍可由 private executor 執行 identity model；unsupported
  loader families 維持 fail-closed。
- **Backward compatibility**：root/model-runtime/model-execution package 不 re-export 新 internal
  types；loader 的 optional-provider error/CPU-only contract 與 fixture strategy 不變。

## Validation Commands

1. `uv run pytest tests/model_runtime/model_execution tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py tests/model_runtime/model_pool/test_onnx_model_loader.py tests/model_runtime/test_local_runtime_composition.py`
2. `uv run pytest`
3. `uv run pyright --project plan/onnx-minimal-executor-invocation-boundary/pyrightconfig.json`
5. `uv run pyright`
6. `uv run ruff check .`
7. `uv lock --check`
8. `git diff --check`

## Validation / Acceptance Checks

驗收必須確認 exact chain、無 outer erasure、private surface、direct cancellation propagation、
sole loader exception、所有列出的 validation 命令與兩個 fresh review artifacts approved。任何
test dynamic import 或 monkeypatch 都是 rejection。

## Reviewer Handoff

```json
{
  "verdict": "approved|needs-rework",
  "blocking_issues": [],
  "copilot_feedback_triage": {"ADDRESS": [], "DISCUSS": [], "SKIP": []}
}
```

## Risks

- Provider `run` signature 與 Protocol 不相容會在 strict witness 或 real ONNX regression 被發現。
- 將 cancellation handler 從舊 candidate 帶入會改變 caller cancellation latency 與 gate semantics。

## Rollback Plan

若 validation/review 失敗，僅回退本 recovery branch 的未提交 topic diff 至乾淨 dev，保留舊
feature worktree 供唯讀 audit；不修改 dev、release 或既有 topic artifacts。

## Post-merge / release actions

No release workflow required。不得 merge、建立 release commit/tag、改版本或發布套件。

## Open Questions / Unresolved Items

無阻塞設計問題；fresh Human implementation clearance 是 workflow gate，不是待猜測的設計決策。
