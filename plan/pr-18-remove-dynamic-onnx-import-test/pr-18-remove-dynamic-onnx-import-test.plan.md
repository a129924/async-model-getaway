> Semantic warning: `analysis/pr-18-remove-dynamic-onnx-import-test/requirements.md`
> 與 `analysis/pr-18-remove-dynamic-onnx-import-test/technical-spec.md` 均不存在。
> 本 plan 依 PR #18 thread `PRRT_kwDOS7D3Es6TIo9V`、Human 已鎖定範圍與現有
> ONNX acquisition baseline 撰寫；analysis layer 為 incomplete-layer mode，不得據此
> 重開 loader/provider/execution/dependency/CI 或既有 architecture decisions。

# pr-18-remove-dynamic-onnx-import-test

## Goal / Outcome

- 移除 ONNX local-runtime acquisition 測試對 `ModuleType`、`sys.modules` 與 module-table
  mutation 的依賴，改以 private、fully typed lazy-importer callable seam 模擬 top-level
  與 nested `ModuleNotFoundError`。
- 完成後 production 仍以真實 lazy import 建立 ONNX session；既有 acquisition、錯誤
  translation、thread offload 與 cancellation contract 不變。

## Scope

### In scope

- 處理 PR #18 thread `PRRT_kwDOS7D3Es6TIo9V` 的單一測試治理 finding。
- 僅在 `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py` 加入
  private typed lazy-importer injection seam，並保留 production path 的實際 lazy import。
- 僅在 `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py` 改用普通
  static imports 與 callable injection，移除 `ModuleType`、`sys.modules`、module-table
  mutation 與其相關 ignore。
- 以 injected callable 覆蓋 missing top-level `onnxruntime` 與 nested
  `onnxruntime.capi` 的 `ModuleNotFoundError` 行為；其餘既有 ONNX acquisition coverage
  必須保留。
- 建立此 topic 的 repo-visible plan/spec/step，並在實作前取得 fresh independent
  plan review 與 Human `cleared_for: implement-plan` gate。

### Out of scope

- `LocalModelLoader`、`ModelPool`、`LoadedRuntimeModel`、`ModelExecution`、provider
  routing、opaque-handle ownership 或任何 public API/typed boundary 的變更。
- ONNX optional extra、dev dependency、`uv.lock`、CI workflow、README、architecture
  documentation、version、release、commit、push、PR state 或其他 PR thread 的修改。
- ONNX provider behavior、CPU provider policy、loader options policy、error messages、
  thread offload、timeout、retry、cancellation 或 lifecycle policy 的改動。
- `importlib`、dynamic module loading、runtime module fabrication，或任何新的 test-only
  exception to root `AGENTS.md` governance。

## Locked Decisions

- D1 verdict: `non-trivial`。本 topic 同時改動 private provider-loader seam 與其
  async acquisition tests，並必須以 spec、fresh RED evidence、implementation review 與
  code review 驗證不變的 provider/error semantics。
- `load_onnx_runtime(...)` remains private. Its production invocation receives no
  test override and continues through a private callable that directly performs the
  real lazy `onnxruntime.InferenceSession` import.
- The private seam is fully typed as a zero-argument callable returning the erased
  inference-session constructor. Tests may pass or monkeypatch a private callable
  seam only; no public constructor parameter, provider getter, package export, `Any`,
  broad suppression, `ModuleType`, `sys.modules`, or module-table mutation is allowed.
- Missing-dependency translation is still limited to `ModuleNotFoundError` whose
  `name == "onnxruntime"`; an injected nested error with name
  `"onnxruntime.capi"` propagates unchanged. The exact install-guidance RuntimeError
  and exception chaining remain unchanged.
- Existing direct static `onnx` and `onnxruntime` imports that create the real
  fixture/assert a real session remain valid; only simulated optional-import failures
  move to callable injection.
- Async-planning status: exempt — cite exemption evidence: this topic does not alter
  the existing async acquisition boundary, `asyncio.to_thread(...)` offload,
  resource lifecycle, concurrency model, failure ownership, cancellation, timeout, or
  retry policy; it only substitutes the private test seam for import-failure setup.
- Stable-library and release intent are explicitly absent. No README or version change
  is permitted; merge ends the topic.

## Boundaries / Exclusions

- Plan-Creator writes planning artifacts only; Tester authors fresh RED tests/evidence;
  Implementer changes only the two declared source/test paths; independent Reviewer
  writes review verdicts; Human alone writes the declared human-check gate.
- All parent ONNX and local-runtime-handle planning/review artifacts are historical
  ReadOnly context. This topic neither invalidates nor rewrites their locked
  architecture decisions.
- Any need to change a path outside `Artifact Paths`, change a public contract, alter
  dependency/CI policy, or modify async semantics returns to
  `spec-and-plan-finalization`.
- The private seam is a testability boundary for import failures, not a general
  provider injection interface; it must not leak to `LocalModelLoader`, `ModelPool`,
  application consumers, or package exports.

## Status / Allowed Transitions

- **Current**: `review-ready`; plan/spec/step are authored and await an independent
  Plan-Reviewer verdict.
- **Execution model**: `spec-and-plan-finalization -> implement-plan -> pr-comment ->
  pr-comment-review-pr-comments-and-fix`; this topic stops at `merged` and has no
  `release` workflow.
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

- `implement-plan` requires both the fresh `approved` plan-review verdict and the
  Human-owned `cleared_for: implement-plan` gate. Chat authorization, a green CI run,
  or resolved PR thread alone is not a substitute.
- This topic begins as the bounded response to the named PR thread. New actionable PR
  feedback must be triaged independently and may not be silently folded into this
  plan.
- PR reply/resolve, commit, push, and PR update require separate explicit Human
  authorization after all implementation/review gates; they are not creator work.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/pr-18-remove-dynamic-onnx-import-test/pr-18-remove-dynamic-onnx-import-test.plan.md` | Plan-Creator | Repo-visible execution contract |
| Behavior specification | `plan/pr-18-remove-dynamic-onnx-import-test/pr-18-remove-dynamic-onnx-import-test.spec.md` | Plan-Creator | D1 non-trivial behavior contract |
| Step tracker | `plan/pr-18-remove-dynamic-onnx-import-test/pr-18-remove-dynamic-onnx-import-test.step.md` | Plan-Creator, then phase owner | Workflow and implementation progress |
| Plan review | `plan/pr-18-remove-dynamic-onnx-import-test/pr-18-remove-dynamic-onnx-import-test.plan-review.json` | Plan-Reviewer | Fresh independent planning verdict |
| Human check | `plan/pr-18-remove-dynamic-onnx-import-test/pr-18-remove-dynamic-onnx-import-test.human-check.json` | Human | Repo-visible gate that clears approved plan for implementation |
| RED evidence | `plan/pr-18-remove-dynamic-onnx-import-test/pr-18-remove-dynamic-onnx-import-test.red-tests.yaml` | Tester | Fresh failing-test evidence before source implementation |
| Implementation review | `plan/pr-18-remove-dynamic-onnx-import-test/pr-18-remove-dynamic-onnx-import-test.implementation-review.yaml` | Reviewer | Plan/contract/scope verification after implementation |
| Code review | `plan/pr-18-remove-dynamic-onnx-import-test/pr-18-remove-dynamic-onnx-import-test.code-review.yaml` | Reviewer | Independent Python quality verdict before PR routing |
| ONNX runtime helper | `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py` | Implementer | Sole production change: private typed lazy-import seam |
| ONNX acquisition tests | `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py` | Tester, Implementer | Sole test change: static-import callable-injection coverage |

Artifact path notes:

- `README.md`, version, `.github/workflows/ci.yml`, `pyproject.toml`, and `uv.lock` are
  not modified by this topic.
- `*.plan-review.json`, `*.human-check.json`, review YAML artifacts are reserved for
  their named owners and must not be pre-filled by Plan-Creator or Implementer.
- A proposed edit outside this table is scope drift and returns to
  `spec-and-plan-finalization`.

### ReadOnly

- `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`
- `src/async_model_gateway/model_runtime/model_pool/pool.py`
- `src/async_model_gateway/model_runtime/runtime_model/`
- `src/async_model_gateway/model_runtime/model_execution/`
- `tests/model_runtime/model_pool/test_local_model_loader.py`
- `pyproject.toml`, `uv.lock`, `.github/workflows/ci.yml`, `README.md`, `docs/`, all
  package exports, and all historical ONNX/local-runtime topic artifacts.

### Written

- Plan-Creator: this topic's `.plan.md`, `.spec.md`, and `.step.md`.
- Plan-Reviewer: this topic's `.plan-review.json`.
- Human: this topic's `.human-check.json` only after plan review approves.
- Tester/Reviewer: declared RED and review evidence only at their named gates.

### Updated

- `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py`
- `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`
- This topic's step tracker as the actual phase owner records completion truthfully.

### Deleted

- None. Removing a dependency, provider behavior, public symbol, historical evidence,
  or any path is scope drift.

## Implementation Steps

1. Tester adds fresh RED coverage in
   `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py` using only
   ordinary static imports and injected typed callables: prove the existing source has
   no supported callable seam while preserving the named top-level/nested
   `ModuleNotFoundError` expectations; record the result in the declared RED artifact.
2. Implementer updates only
   `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py`: separate
   the real private lazy import into a fully typed zero-argument importer and accept a
   private test-only callable override at the helper boundary; centralize exact
   top-level-missing translation around that seam while retaining options validation,
   `asyncio.to_thread(...)`, and CPU-only construction unchanged.
3. Implementer updates only
   `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`: delete
   `sys`/`ModuleType` imports and all module-table mutation; inject callable factories
   for real construction, provider failure, top-level missing dependency, nested
   missing dependency, thread-offload, and cancellation tests as needed, without
   weakening their assertions or adding dynamic module loading.
4. Implementer runs the declared focused, full, typing, lint, governance-source, and
   diff checks; confirms only `Written`/`Updated` paths changed; updates the step
   tracker only with actual completed work; then hands the topic to independent
   implementation and code review.

## Validation / Acceptance Checks

- The only production/test diffs are the two declared `Updated` paths; all ReadOnly
  paths, public contracts, dependencies, CI, and architecture decisions remain intact.
- Production ONNX acquisition continues to perform real lazy import when no private
  override is supplied; no public injection interface exists.
- A callable-injected `ModuleNotFoundError(name="onnxruntime")` produces the exact
  existing chained install-guidance `RuntimeError`; an injected nested
  `ModuleNotFoundError(name="onnxruntime.capi")` is the same exception object.
- Tests contain no `ModuleType`, `sys.modules`, `importlib`, module-table mutation, or
  dynamic module loading, and do not add a governance exception.
- Existing valid acquisition, invalid options, provider failure, invalid path/model,
  CPU-only provider, thread-offload, cancellation, explicit-family routing, opaque
  handle, and ModelExecution handoff semantics continue to pass.
- Run:

```bash
uv run pytest --no-cov tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py -v
uv run pytest --no-cov tests/model_runtime/model_pool tests/model_runtime/model_execution -v
uv run pytest -v
uv run pyright
uv run ruff check src tests plan/pr-18-remove-dynamic-onnx-import-test
rg -n "ModuleType|sys\\.modules|importlib|setitem\\(sys" tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py
git diff --check
```

The `rg` command must return no matches; a nonzero no-match exit is the expected
acceptance result and must be reported explicitly rather than treated as a test failure.

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

No release workflow required. After merge, stop; do not modify README, version, tags,
publication, or release state under this topic.

## Open Questions / Unresolved Items

None. The named PR thread, private seam boundary, test strategy, exact writable paths,
and unchanged contracts are locked.

## Python Implementation

### Goal

Replace ONNX optional-import failure simulation with a typed private callable seam
without changing acquisition behavior or public runtime-model boundaries.

### Non-goals

- No `LocalModelLoader`, `ModelPool`, `LoadedRuntimeModel`, or `ModelExecution` change.
- No provider/session API exposure, execution behavior, lifecycle, or async-policy
  redesign.
- No dependency, lockfile, CI, docs, version, release, or PR-state modification.
- No dynamic module loading, `ModuleType`, `sys.modules`, `importlib`, or module-table
  mutation in tests.

### Current Context

- `_onnx_runtime_loader.py` currently does the real lazy `InferenceSession` import in a
  private helper and translates only a top-level missing optional dependency.
- `test_onnx_local_runtime_acquisition.py` directly mutates `sys.modules` for the
  missing-extra case and fabricates a `ModuleType` with `__getattr__` for a nested
  import failure, contrary to the repository test governance.
- Existing tests already statically import `onnx`/`onnxruntime` for real fixture and
  session checks, and the helper remains a private dependency of `LocalModelLoader`.

### Requirements

1. Production calls retain a real lazy `onnxruntime.InferenceSession` import and do
   not require a test override.
2. The private seam is fully typed and accepts a zero-argument callable that returns
   the erased session constructor; it cannot become a public API or module-routing
   mechanism.
3. Tests simulate top-level and nested `ModuleNotFoundError` only by injected
   callables, with exact existing translation/identity semantics.
4. The test file removes all `ModuleType`, `sys.modules`, and module-table mutation
   uses while retaining static imports and existing behavioral coverage.
5. Existing options validation, CPU-only provider construction, `asyncio.to_thread`,
   cancellation, provider-error, explicit-family, opaque-handle, and execution-handoff
   behavior remain unchanged.

### Decisions

- Async-planning status: exempt — cite exemption evidence: no async boundary,
  lifecycle, concurrency, failure ownership, cancellation, timeout, or retry decision
  changes; the existing `load_onnx_runtime(...)` coroutine and thread-offloaded session
  construction retain their frozen behavior.
- Module/package placement: exactly the private ONNX helper and its existing focused
  acquisition test file.
- New public API: no; the injectable importer is private to the helper module.
- Interface changes: private helper-only optional callable seam; `ModelPool.acquire(...)`
  and all public imports/signatures stay unchanged.
- Breaking changes allowed: no; existing production calls use the default real importer.
- New dependencies: no.
- Error handling strategy: preserve options `ValueError`, exact chained top-level
  missing-extra `RuntimeError`, and unchanged nested/provider/cancellation propagation.
- Typing strategy: private named `Callable` aliases or equivalent fully typed callable
  annotations; erased constructor/session use `object`; no `Any`, broad ignore, or
  dynamic module types.

### Public Contract / API Changes

No public API changes. `ModelPool.acquire(self, artifact: ModelArtifact) ->
LoadedRuntimeModel[object]`, opaque `LoadedRuntimeModel` semantics, and `ModelExecution`
injected-invoker behavior remain unchanged.

### Affected Files / Modules

Likely affected files:

- `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py`
- `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`

Candidate files to inspect only:

- `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`
- `src/async_model_gateway/model_runtime/model_pool/pool.py`
- `src/async_model_gateway/model_runtime/model_execution/execution.py`
- `AGENTS.md`

### Implementation Steps

1. Create fresh static-import RED tests that require a typed callable seam and prohibit
   module-table mutation.
2. Add the private typed real-import/callable-injection seam to the ONNX helper without
   changing its production default or async/provider behavior.
3. Replace every dynamic optional-import simulation in the focused test with injected
   callables and retain all existing assertions.
4. Run validation and record only truthfully completed phase/check evidence.

### Test Plan

#### TestCase

- Happy path: the default path acquires a real CPU-only `InferenceSession`; an injected
  constructor returns the exact supplied session through the opaque handle and existing
  `ModelExecution` handoff.
- Invalid input: non-empty `loader_options` still raises the exact `ValueError` before
  importer/constructor execution.
- Edge case: injected top-level missing `onnxruntime` receives exact chained install
  guidance; injected nested `onnxruntime.capi` error propagates by identity.
- Regression: provider construction, missing/invalid artifacts, explicit family route,
  thread offload, and cancellation preserve existing behavior.
- Backward compatibility: public acquisition annotation, package exports, opaque handle,
  and injected ModelExecution invocation semantics do not change.

### Validation Commands

Use the commands declared in `Validation / Acceptance Checks`, including focused and
full pytest, Pyright, Ruff, dynamic-module-governance source scan, and `git diff --check`.

### Risks

- Catching injected errors in the wrong layer could translate nested provider import
  failures into misleading installation guidance.
- A broad public parameter or untyped seam could leak provider implementation details
  or weaken strict typing.
- Replacing only one dynamic simulation could leave a governance violation in the test
  file despite passing functional tests.

### Rollback Plan

Revert only `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py`
and `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`, plus this
topic's planning/review evidence as applicable. Do not alter ReadOnly parent contracts
or PR state during rollback.

### Open Questions

None.
