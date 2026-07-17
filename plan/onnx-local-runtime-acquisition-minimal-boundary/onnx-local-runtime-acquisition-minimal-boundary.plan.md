> Semantic warning: `analysis/onnx-local-runtime-acquisition-minimal-boundary/requirements.md`
> 與 `analysis/onnx-local-runtime-acquisition-minimal-boundary/technical-spec.md`
> 均不存在。本 plan 依據 repo exploration 與已鎖定的人類決策撰寫；analysis
> layer 為 incomplete-layer mode，不得被當成擴張 scope、重開 contract，或加入
> release 工作的依據。

# onnx-local-runtime-acquisition-minimal-boundary

## Goal / Outcome

- 讓 `ModelArtifact(loader_family=LoaderFamily.ONNX)` 經由既有的
  `ModelPool.acquire()`、private `LocalModelLoader._load_onnx()`，建立一個
  CPU-only `onnxruntime.InferenceSession`，並回傳
  `LoadedRuntimeModel[object]`。
- 此 topic 完成時只提供真實 local runtime acquisition；session 的 invocation
  仍由既有 `ModelExecution` 的 injected invoker seam 消費，並非本 topic 的行為。

## Scope

### In-Scope

- 在 private `_onnx_runtime_loader.py` 建立 ONNX session acquisition helper，並由
  `_load_onnx(...)` direct-await 該 helper。
- 對 `onnxruntime` 採 lazy import；session construction 必須使用
  `asyncio.to_thread(...)`，且固定 CPU provider。
- 使用既有 `_create_loaded_runtime_model(...)` 將 provider session 擦除為
  `LoadedRuntimeModel[object]`。
- 將 `onnxruntime>=1.22.0,<1.22.1` 加入 published `onnx` optional extra，並將
  `onnx>=1.16.2,<1.17` 加入 dev dependency group，以動態生成暫存 test model。
- 新增 ONNX acquisition、strict Pyright fixture 與必要的既有 loader regression
  coverage；tests 不得使用動態模組載入。
- 建立並使用本 topic 的 plan、spec、step、plan-review、human-check、RED、
  implementation-review 與 code-review evidence paths。

### Out-Of-Scope

- 真實 ONNX inference、ONNX invoker、`ModelExecution` contract 或 execution
  behavior 的改動。
- PICKLE/TORCH loader 實作、GPU/CUDA/TensorRT/provider allowlist、provider
  registry 或 adapter redesign。
- 依副檔名、path、檔案內容推導 loader family，或預先檢查 path existence。
- pool cache/reuse/close/unload/eviction、timeout、retry、background task ownership、
  remote `ModelGateway` 或 orchestrator wiring。
- public API、package exports、`ModelArtifact`、`LoaderFamily`、`ModelPool` 或
  `ModelExecution` public contract 的改動。
- README、architecture docs、版本、tag、release、commit、push 或 PR。

## Locked Decisions

- D1 verdict: `non-trivial`；此 topic 跨 async boundary、optional dependency、
  provider acquisition、tests、strict typing 與 workflow evidence。
- `LoaderFamily.ONNX` 是唯一 routing authority。`artifact.artifact_path` 不得用於
  family inference，且不做額外 path existence check。
- 新增 private module
  `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py`，其
  `load_onnx_runtime(artifact: ModelArtifact) -> object` 是唯一 ONNX-specific
  acquisition helper。它以 private lazy-import helper 取得 `InferenceSession`，
  驗證 options 後使用
  `await asyncio.to_thread(InferenceSession, artifact.artifact_path,
  providers=["CPUExecutionProvider"])` 建構 session。
- `_load_onnx(...)` 保持 `LoadedRuntimeModel[object]` return annotation，direct-await
  `load_onnx_runtime(...)`，並以
  `_create_loaded_runtime_model(loader_family=LoaderFamily.ONNX, provider_model=session)`
  回傳。不改變 PICKLE/TORCH 的 `NotImplementedError` policy。
- `artifact.loader_options` 只允許空 mapping；非空值必須在 import 或 provider
  construction 前拋出 exact
  `ValueError("ONNX loader_options are not supported")`。
- 僅 top-level `ModuleNotFoundError` 且 `name == "onnxruntime"` 轉譯成 chained
  `RuntimeError("ONNX runtime support requires installing async-model-gateway[onnx]")`。
  nested import failure、無效模型、缺檔與 provider initialization failure 原樣傳播。
- cancellation 原樣傳播；不加 timeout/retry，且不得宣稱取消可中止已開始的 native
  session construction。
- stable-library intent 明確缺席：本 topic merge 後停止，沒有版本 bump 或 release
  workflow；`## Stable library metadata` 因此刻意省略。
- analysis layer 缺件是已知 warning，不是實作授權的缺口；若 reviewer 判定它造成
  contract ambiguity，必須回到 `spec-and-plan-finalization`，不能由 implementer
  補設計。

## Boundaries / Exclusions

- Plan-Creator 只建立/更新 planning artifacts；Tester 只建立 RED tests/evidence；
  Implementer 只處理已宣告 source/test/dependency paths；Reviewer 與
  Plan-Reviewer 只給獨立 verdict；Human 只關閉 human gates。
- 本 topic 的 `ReadOnly` paths 僅供理解/回歸驗證，不授權修改。任何新增 public
  surface、GPU support、options allowlist、loader-family/path semantics 或 release
  intent 都必須回到 `spec-and-plan-finalization`。
- `ModelExecution` 只可作 provider identity handoff 的驗證 consumer；loader
  不得呼叫 invoker 或執行 inference。

## Status / Allowed Transitions

- **Current**: `review-ready`；Plan-Creator 已完成 plan/spec/step authoring，等待
  獨立 Plan-Reviewer verdict。analysis-layer warning 仍為未完成的語意限制。
- **Execution model**: `spec-and-plan-finalization -> implement-plan -> pr-comment ->
  pr-comment-review-pr-comments-and-fix`；本 topic 在 `merged` 停止，沒有
  conditional `release` workflow。
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

- `approved` 需要 declared plan-review artifact 的 `approved` verdict 與 Human
  寫入的 `human-check`；聊天同意、green tests 或 reviewer silence 都不是 gate。
- Python RED test authoring 是 `implement-plan` 的第一個強制 subphase。未先完成
  RED evidence 前不得改 production code、dependency 或 lockfile。
- scope、artifact path、public contract、dependency policy、CPU-only policy 或 release
  intent 漂移必須回到 `spec-and-plan-finalization`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/onnx-local-runtime-acquisition-minimal-boundary/onnx-local-runtime-acquisition-minimal-boundary.plan.md` | Plan-Creator | Repo-visible execution contract |
| Python spec | `plan/onnx-local-runtime-acquisition-minimal-boundary/onnx-local-runtime-acquisition-minimal-boundary.spec.md` | Plan-Creator | Non-trivial behavior contract |
| Step tracker | `plan/onnx-local-runtime-acquisition-minimal-boundary/onnx-local-runtime-acquisition-minimal-boundary.step.md` | Plan-Creator, then phase owner | Workflow state and actual implementation progress |
| Plan review | `plan/onnx-local-runtime-acquisition-minimal-boundary/onnx-local-runtime-acquisition-minimal-boundary.plan-review.json` | Plan-Reviewer | Independent planning verdict |
| Human check | `plan/onnx-local-runtime-acquisition-minimal-boundary/onnx-local-runtime-acquisition-minimal-boundary.human-check.json` | Human | Explicit clearance for `implement-plan` |
| RED evidence | `plan/onnx-local-runtime-acquisition-minimal-boundary/onnx-local-runtime-acquisition-minimal-boundary.red-tests.yaml` | Tester | Fresh pre-production test/type evidence |
| Topic Pyright config | `plan/onnx-local-runtime-acquisition-minimal-boundary/pyrightconfig.json` | Tester | Strict static-fixture routing |
| Implementation review | `plan/onnx-local-runtime-acquisition-minimal-boundary/onnx-local-runtime-acquisition-minimal-boundary.implementation-review.yaml` | Reviewer | Plan-conformance verdict |
| Code review | `plan/onnx-local-runtime-acquisition-minimal-boundary/onnx-local-runtime-acquisition-minimal-boundary.code-review.yaml` | Reviewer | Independent quality/boundary verdict |
| ONNX runtime helper | `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py` | Implementer | Private lazy-import and thread-offloaded session acquisition |
| Local loader | `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` | Implementer | ONNX helper handoff and opaque wrapping |
| Acquisition tests | `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py` | Tester | Real ONNX acquisition and async/error behavior |
| Existing loader tests | `tests/model_runtime/model_pool/test_local_model_loader.py` | Tester | Narrow fail-closed regression for only PICKLE/TORCH |
| Typecheck fixture | `tests/typecheck/onnx_local_runtime_acquisition.py` | Tester | Public acquisition erasure assertion |
| Dependency manifest | `pyproject.toml` | Implementer | ONNX extra and dev fixture dependency |
| Lockfile | `uv.lock` | Implementer | Resolved dependency metadata |

### ReadOnly

- `src/async_model_gateway/model_runtime/model_artifact/artifact.py`
- `src/async_model_gateway/model_runtime/model_artifact/loader_family.py`
- `src/async_model_gateway/model_runtime/model_pool/pool.py`
- `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py`
- `src/async_model_gateway/model_runtime/model_execution/execution.py`
- `src/async_model_gateway/model_runtime/model_pool/__init__.py`
- `README.md`, `docs/architecture.md`, `src/async_model_gateway/__version__.py`

### Written

- All topic-local plan/spec/step files listed above, plus later phase-owned
  plan-review, human-check, RED, implementation-review, code-review, and Pyright
  artifacts.
- `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py`
- `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`
- `tests/typecheck/onnx_local_runtime_acquisition.py`

### Updated

- `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`
- `tests/model_runtime/model_pool/test_local_model_loader.py`
- `pyproject.toml`
- `uv.lock`

### Deleted

- None. Any deletion or path outside this table is plan drift.

Artifact path notes:

- 本 topic 不修改 `README.md`、版本 source、public exports 或 release artifacts。
- listed paths 是 executable contract；若 later phase 需要其他 source/test/docs path，
  必須停止並回到 `spec-and-plan-finalization`。

## Implementation Steps

1. Tester 在 `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`、
   `tests/model_runtime/model_pool/test_local_model_loader.py`、
   `tests/typecheck/onnx_local_runtime_acquisition.py` 與 topic-local
   `pyrightconfig.json` 建立 fresh RED coverage，並在 production/dependency edits 前
   記錄 `onnx-local-runtime-acquisition-minimal-boundary.red-tests.yaml`。
2. Implementer 更新 `pyproject.toml` 與 `uv.lock`：發布用
   `[project.optional-dependencies].onnx` 固定
   `onnxruntime>=1.22.0,<1.22.1`，dev group 固定
   `onnx>=1.16.2,<1.17`；不更新 package version 或任何 release file。
3. Implementer 新增
   `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py`，實作
   private lazy import、exact options/error policy，以及 CPU-only
   `asyncio.to_thread(...)` session construction。
4. Implementer 更新 `_local_model_loader.py` 的 `_load_onnx(...)`：direct-await
   helper，並以 existing `_create_loaded_runtime_model(...)` 包裝 session；
   PICKLE/TORCH handlers、explicit dispatch 與 `assert_never` 不變。
5. Implementer 執行 declared validation、確認 diff 僅涉及 `Written`/`Updated`
   paths、只更新實際完成的 step progress，並將 validation 結果交接給獨立
   Reviewer；不得自行關閉 reviewer 或 human gate。

## Validation / Acceptance Checks

- plan/spec/step 都存在；step mirrors five numbered implementation steps，並保留六個
  canonical workflow stages。
- `onnx` extra、dev `onnx` fixture dependency、locked versions、CPU-only provider、
  exact options/error strings 與 no-release decision 可從 plan text 直接驗證。
- later tests 證明 session construction 不阻塞 event loop、runtime identity 能交給
  `ModelExecution`、且 loader 未執行 inference。
- later validation 不得修改 `ReadOnly` paths；PICKLE/TORCH fail closed，且 explicit
  loader family continues to outrank path appearance。
- future review evidence 必須落在 declared exact paths；plan-review handoff shape
  必須是單一 JSON object。

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

- None. 缺少 analysis artifacts 已在開頭 semantic warning 與 Locked Decisions
  記錄，並非 implementer 可自行補齊的開放設計問題。

## Python Implementation

### Goal

建立最小的 private ONNX runtime acquisition path，保留既有
`ModelPool.acquire(...) -> LoadedRuntimeModel[object]` 的 public erasure boundary。

### Non-Goal

- 不新增 inference 或 ONNX invoker。
- 不增加 GPU/provider configuration、non-empty options support 或 provider registry。
- 不改變 ModelArtifact/LoaderFamily validation、ModelPool API、ModelExecution API 或
  package exports。
- 不處理 session lifecycle/cache/close/unload、timeout/retry、remote loading 或 release。

### Current Context

- `LocalModelLoader.load(...)` 已依 explicit `LoaderFamily` 分派；ONNX handler 現在
  fail closed，PICKLE/TORCH 也各自 fail closed。
- `ModelPool.acquire(...)` 已將 public result 固定為 `LoadedRuntimeModel[object]`。
- `_create_loaded_runtime_model(...)` 在 runtime-model module 的 private boundary
  保存 provider object，`ModelExecution` 只透過 private handoff 傳給 injected
  async invoker。
- project 目前沒有 `onnx` optional extra 或 dev `onnx` fixture dependency。

### Requirements

1. valid ONNX artifact 必須產生真實 `onnxruntime.InferenceSession`，並以
   `LoaderFamily.ONNX` 包裝成 `LoadedRuntimeModel[object]`。
2. session factory 必須只收到 `artifact.artifact_path` 與
   `providers=["CPUExecutionProvider"]`，並在 worker thread 執行。
3. non-empty `loader_options`、missing optional dependency、provider failure 與
   cancellation 必須符合 Locked Decisions 的 exact propagation contract。
4. test fixture 必須用 dev `onnx` 動態寫入 temporary model；repository 不新增
   binary `.onnx` fixture，也不以 file suffix 決定 family。
5. package imports、public exports、static acquisition return annotation 與
   PICKLE/TORCH fail-closed behavior 必須維持相容。

### Decisions

- Async-planning status: triggered — cite trigger evidence:
  `LocalModelLoader.load()`/`_load_onnx()` already form an async acquisition path,
  while `onnxruntime.InferenceSession` construction is synchronous native work that
  must be moved to `asyncio.to_thread(...)`; cancellation behavior therefore needs
  an explicit contract.
- Module/package placement: ONNX-specific code lives only in private
  `model_pool/_onnx_runtime_loader.py`; `_local_model_loader.py` remains the dispatch
  and opaque-wrapper boundary.
- New public API: no.
- Interface changes: no public signature changes; only the private ONNX handler changes
  from `NotImplementedError` to acquisition.
- Breaking changes allowed: no; existing imports and erased public return type remain.
- New dependencies: yes — published optional
  `onnxruntime>=1.22.0,<1.22.1` and dev-only fixture generator
  `onnx>=1.16.2,<1.17`.
- Error handling strategy: exact non-empty-options `ValueError`; only missing top-level
  `onnxruntime` becomes chained install-guidance `RuntimeError`; all other provider
  exceptions/cancellation propagate unchanged.
- Typing strategy: keep provider session as `object` across the private loader/public
  boundary; no `Any`, provider type export, dynamic import, or file-wide private-use
  suppression is allowed.

#### Async boundary decision

`LocalModelLoader.load()` and `_load_onnx()` remain async. The helper imports lazily
on the caller thread, then offloads exactly one synchronous `InferenceSession`
construction via `asyncio.to_thread(...)`.

#### Resource lifecycle decision

The topic creates and hands off a session only. It adds no retained session cache,
close API, unload behavior, ownership transfer policy, or cleanup task.

#### Concurrency model

Each `acquire()` causes one independent worker-thread factory call. There is no
fan-out, batch, semaphore, task spawning, deduplication, or internal sharing.

#### Failure model

Options validation occurs before import/provider construction. Only the exact missing
top-level dependency case is translated; invalid model, missing path, invalid provider,
and nested import failures preserve original exception identity and traceback chain.

#### Cancellation / timeout policy

Caller cancellation propagates untouched. No timeout or retry is introduced. Once the
worker starts native session construction, cancellation of the awaiting task need not
stop the underlying thread; tests must not claim otherwise.

#### Validation plan

Run the declared focused pytest/Pyright commands with `--extra onnx`, then full pytest,
Ruff, Pyright, `uv lock --check`, and `git diff --check`. The focused test proves the
thread-offload behavior through a deliberately blocking session factory while another
event-loop task still advances.

#### Handoff notes for the implementer

Keep lazy import confined to the new private module. Do not add a public ONNX class or
export. Use a private import seam only for static-import tests that simulate missing
dependency; do not use `importlib` or dynamic module loading in tests.

#### Async contradiction log

No async contradictions. The topic deliberately offloads synchronous native work but
does not introduce lifecycle, timeout, retry, or cancellation ownership.

### Public Contract / API Changes

No public API changes. `ModelPool.acquire(self, artifact: ModelArtifact) ->
LoadedRuntimeModel[object]` remains unchanged. `LoadedRuntimeModel[object]` continues
to expose only `loader_family` publicly; session identity crosses to `ModelExecution`
solely through the existing private internal handoff.

### Affected Files / Modules

Likely affected files:

- `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py`
- `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`
- `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`
- `tests/model_runtime/model_pool/test_local_model_loader.py`
- `tests/typecheck/onnx_local_runtime_acquisition.py`
- `plan/onnx-local-runtime-acquisition-minimal-boundary/pyrightconfig.json`
- `pyproject.toml`
- `uv.lock`

Candidate files to inspect:

- `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py`
- `src/async_model_gateway/model_runtime/model_execution/execution.py`
- `tests/model_runtime/model_pool/test_model_pool.py`

### Implementation Steps

1. Tester creates `test_onnx_local_runtime_acquisition.py` with a temporary ONNX model
   built by static `onnx` imports, updates `test_local_model_loader.py` so only
   PICKLE/TORCH default handlers remain fail-closed, adds the static type fixture and
   `pyrightconfig.json`, then records fresh RED evidence before production edits.
2. Implementer updates `pyproject.toml` and `uv.lock` with the locked `onnx` optional
   extra and dev `onnx` fixture dependency; no version/release metadata changes.
3. Implementer adds `_onnx_runtime_loader.py` with private lazy import, pre-load empty
   options validation, exact missing-extra translation, and CPU-only
   `asyncio.to_thread(...)` session creation.
4. Implementer updates `_local_model_loader.py` so `_load_onnx(...)` awaits the helper
   and calls `_create_loaded_runtime_model(...)`; it does not alter PICKLE/TORCH,
   explicit match/case routing, `assert_never`, or public annotations.
5. Implementer runs validation, verifies only `Written`/`Updated` paths changed, updates
   the actual step state, and hands the topic to independent implementation/code review.

### Test Plan

Test files: `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`,
`tests/model_runtime/model_pool/test_local_model_loader.py`, and
`tests/typecheck/onnx_local_runtime_acquisition.py`.

#### TestCase

- Happy path: dynamically generate a valid temporary ONNX model; acquire it through
  `ModelPool`; assert a real `InferenceSession`, `LoadedRuntimeModel[object]`, and
  exact `LoaderFamily.ONNX`.
- Invalid input: non-empty options raise the exact `ValueError` before provider
  construction; a simulated top-level missing `onnxruntime` import raises the exact
  chained `RuntimeError` install guidance.
- Edge case: a valid ONNX model with no `.onnx` suffix still loads when family is ONNX;
  a blocking factory does not block a concurrent event-loop task; caller cancellation
  is re-raised unchanged while the test releases its worker fixture.
- Regression: PICKLE/TORCH still raise `NotImplementedError`; a PICKLE artifact with an
  `.onnx`-looking path remains in its PICKLE route; invalid path/model/provider failures
  are not translated.
- Backward compatibility: `ModelExecution` receives the identical session object through
  the existing private handoff without inference; strict Pyright asserts
  `ModelPool.acquire(...) -> LoadedRuntimeModel[object]`; no package export changes.

### Validation Commands

```bash
uv lock --check
uv run --extra onnx pytest --no-cov tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py tests/model_runtime/model_pool/test_local_model_loader.py -v
uv run --extra onnx pyright --project plan/onnx-local-runtime-acquisition-minimal-boundary/pyrightconfig.json tests/typecheck/onnx_local_runtime_acquisition.py
uv run --extra onnx pytest -v
uv run --extra onnx ruff check src tests plan/onnx-local-runtime-acquisition-minimal-boundary
uv run --extra onnx pyright
git diff --check
```

### Risks

- `onnx`-generated model IR/opset compatibility may drift relative to the locked
  `onnxruntime` version; fixture generation must select a model compatible with that
  runtime.
- `asyncio.to_thread(...)` cancellation cannot forcibly stop a session creation already
  executing in a native worker thread.
- Catching broad import/provider errors would hide provider diagnostics, so translation
  must remain limited to the exact missing top-level dependency condition.

### Rollback Plan

Revert the declared `Written`/`Updated` source, test, dependency, lockfile, and topic
artifact paths. Do not alter `ReadOnly` paths or unrelated historical workflow evidence.

### Open Questions

None. All dependency placement, CPU provider, options, error, typing, async, and
release decisions are locked above.
