> Semantic warning: `analysis/local-runtime-handle-ownership-clarification/requirements.md`
> 與 `analysis/local-runtime-handle-ownership-clarification/technical-spec.md` 均不存在。
> 本 plan 依 Human 已鎖定 contract 與 parent baseline
> `feat/andrew/onnx-local-runtime-acquisition` at `31a3d1d` 撰寫；analysis layer
> 為 incomplete-layer mode，不得據此擴張為 executable runtime model、provider
> adapter，或重新設計 invocation contract。

# local-runtime-handle-ownership-clarification

## Goal / Outcome

- 對已完成的 handle-ownership implementation 與已存在的 authorized CI one-line
  diff 做 preserve-and-verify；不重寫任何 original source、docs、tests、type fixtures
  或 workflow。
- 唯一的 current Implementer write 是為三個 declared human-check JSON 各加上一個
  final LF；`LoadedRuntimeModel`、`ModelPool.acquire(...)` 與 `ModelExecution` contract
  均維持既有 historical truth。

## Scope

### In scope

- 將 original handle-ownership source、docs、tests、type fixtures、RED evidence 與
  Pyright config 視為 historical ReadOnly context；只驗證其既有 contract，禁止重寫。
- 保留並驗證已存在於 worktree 的 `.github/workflows/ci.yml` 唯一 authorized
  dependency-sync diff；它是 historical ReadOnly context，不是 current Implementer
  writable target，revised-scope validation/review 尚未完成。
- 對三個已宣告 human-check JSON 各補上一個 final LF；JSON text、values、key order
  與 indentation 必須 byte-for-byte 保持不變，除最後 LF 外不得有內容改動。
- Plan-Creator、Plan-Reviewer、Reviewer 與 Human 依其各自 gate ownership 更新
  planning/review/human artifacts；這些 gate writes 不屬於 Implementer scope。

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
- 對任何 original handle-ownership source、docs、tests、type fixtures、RED evidence、
  Pyright config 或 `.github/workflows/ci.yml` existing authorized diff 的重寫。
- 任何 CI workflow、trigger、action、Python version、validation command 或 pre-commit
  policy 變更；既有 `Sync dependencies` exact command diff 亦不得重寫。
- 三個 human-check JSON 的任何 JSON value、key order、indentation、whitespace（final
  LF 除外）或 gate semantics 變更。

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
- Validation-hygiene retrofit D1 verdict: `trivial`。唯一未完成的 work 是既有 CI
  workflow 的 single sync-command flag addition，以及三個 declared JSON 的 one-final-LF
  normalization；它們不改 source/test/dependency declaration/public contract 或 async
  behavior。原 handle-ownership implementation 的 `non-trivial` spec/RED artifacts
  保留為 historical truth，但不是此 retrofit 的 fresh requirement。
- Historical CI context: `.github/workflows/ci.yml` already changes
  `uv sync --frozen --group dev` to
  `uv sync --frozen --group dev --extra onnx`. This retrofit may only preserve and
  verify that existing line; it must not add, remove, or rewrite any CI diff.
- The exact CI one-line diff already exists in the worktree from authorized prior
  implementation. This retrofit must preserve and verify it; it must not rewrite the
  workflow. The only additional implementation writes are the three declared final LFs.
- Current Implementer writable boundary is exact and closed: only the three final-LF
  JSON target paths declared below. All original handle-ownership source/docs/tests/type
  fixtures and the existing CI workflow diff are historical ReadOnly
  preserve-and-verify context.
- Bounded final-LF repair targets are exactly
  `plan/onnx-local-runtime-acquisition-minimal-boundary/onnx-local-runtime-acquisition-minimal-boundary.human-check.json`,
  `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.human-check.json`,
  and
  `plan/local-runtime-acquisition-documentation-consistency/local-runtime-acquisition-documentation-consistency.human-check.json`.
  Each receives exactly one trailing LF and no JSON-semantic or other byte change.
- The existing CI sync diff and the three final-LF writes are both required for declared
  full pre-commit validation: the former makes the optional runtime available to
  existing checks, while the latter satisfy repository text-file hygiene without
  altering human-gate meaning.

## Boundaries / Exclusions

- Plan-Creator 只建立/更新 planning artifacts；Tester 的 original RED tests/evidence
  已是 historical ReadOnly；Implementer 只可寫入三個 declared final-LF JSON paths；
  Reviewer 與 Plan-Reviewer 只提供 independent verdict；Human 只關閉 human gates。
- `LoadedRuntimeModel` 的 executable redesign、provider-specific adapter 或 execution
  dispatch 另立 topic；不得在本 topic 以 rename、temporary `execute`、deprecated
  escape hatch 或 public factory 偷渡。
- tests 不得使用動態模組載入；完整 production-tree ownership assertion 必須以 static
  source/AST inspection 實作，且不可把 test-only `_provider_runtime()` overrides 誤判為
  production consumers。
- 所有 implementation/test/docs changes 必須限於 Artifact Paths；需要修改未列檔案、
  public contract、dependency 或 release intent 時，回到 `spec-and-plan-finalization`。

## Status / Allowed Transitions

- **Current**: `review-ready`；authorized CI one-line diff 已存在但 revised-scope
  validation/review 未完成，且新增三個 final-LF target paths 是 scope change。因此既有
  CI-retrofit plan-review、implementation/code review 與 human-check 皆不適用於此
  revised contract，等待 fresh independent Plan-Reviewer verdict。
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
- 原 implementation 的 RED/test artifacts 已完成並維持 historical truth。CI repair
  與 final-LF repair 都是 trivial validation-hygiene changes，不新增或修改 tests，且
  不要求 fresh RED 或 CI-specific spec；fresh Plan-Reviewer `approved` verdict 與
  refreshed revised-scope repo-visible human-check 是唯一可開始此 bounded work 的前置
  gate。
- scope、private ownership placement、public contract、test governance、documentation
  wording、dependency 或 release intent 漂移，皆返回 `spec-and-plan-finalization`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.plan.md` | Plan-Creator | Repo-visible execution contract |
| Python spec | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.spec.md` | Historical ReadOnly | Original non-trivial behavior contract; not refreshed for trivial CI retrofit |
| Step tracker | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.step.md` | Plan-Creator, then phase owner | Workflow and implementation progress |
| Plan review | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.plan-review.json` | Plan-Reviewer | Independent planning verdict |
| Human-check gate state | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.human-check.json` | Human | Explicit clearance for `implement-plan`; gate-state semantics are Human-owned |
| ONNX acquisition human-check LF target | `plan/onnx-local-runtime-acquisition-minimal-boundary/onnx-local-runtime-acquisition-minimal-boundary.human-check.json` | Implementer | Add exactly one final LF; preserve JSON semantics and bytes otherwise |
| Handle-ownership human-check LF target | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.human-check.json` | Implementer | After Human clearance, add exactly one final LF; preserve JSON semantics and bytes otherwise |
| Documentation-consistency human-check LF target | `plan/local-runtime-acquisition-documentation-consistency/local-runtime-acquisition-documentation-consistency.human-check.json` | Implementer | Add exactly one final LF; preserve JSON semantics and bytes otherwise |
| RED evidence | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.red-tests.yaml` | Historical ReadOnly | Original test/type evidence; no fresh CI retrofit RED artifact |
| Topic Pyright config | `plan/local-runtime-handle-ownership-clarification/pyrightconfig.json` | Historical ReadOnly | Original strict static-fixture routing |
| Implementation review | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.implementation-review.yaml` | Reviewer | Plan-conformance verdict |
| Code review | `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.code-review.yaml` | Reviewer | Independent quality and boundary verdict |
| Runtime-model contract | `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py` | Historical ReadOnly | Preserve-and-verify abstract opaque handle/private handoff |
| Local loader | `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` | Historical ReadOnly | Preserve-and-verify loader-local concrete handle/ONNX handoff |
| Model-side spec | `docs/specs/model-side-boundary.md` | Historical ReadOnly | Preserve-and-verify ownership documentation |
| CI workflow | `.github/workflows/ci.yml` | Historical ReadOnly | Preserve-and-verify the existing authorized `--extra onnx` sync diff |
| Runtime-model tests | `tests/model_runtime/runtime_model/test_loaded_runtime_model.py` | Historical ReadOnly | Preserve-and-verify abstract contract regression |
| Runtime-model package tests | `tests/model_runtime/runtime_model/test_runtime_model_package_surface.py` | Historical ReadOnly | Preserve-and-verify public import/export surface |
| Local-loader tests | `tests/model_runtime/model_pool/test_local_model_loader.py` | Historical ReadOnly | Preserve-and-verify local construction/routing regression |
| Model-pool tests | `tests/model_runtime/model_pool/test_model_pool.py` | Historical ReadOnly | Preserve-and-verify opaque acquisition compatibility |
| ONNX acquisition tests | `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py` | Historical ReadOnly | Preserve-and-verify ONNX provenance/execution handoff |
| Model-execution package tests | `tests/model_runtime/model_execution/test_model_execution_package_surface.py` | Historical ReadOnly | Preserve-and-verify production-tree caller governance |
| Generic-erasure type fixture | `tests/typecheck/runtime_model_generic_erasure.py` | Historical ReadOnly | Preserve-and-verify generic opaque-handle assertions |
| Execution type fixture | `tests/typecheck/model_execution_minimal_consumption.py` | Historical ReadOnly | Preserve-and-verify `ModelExecution` contract assertions |

### ReadOnly

- All historical artifact paths labelled `Historical ReadOnly` above, including the
  original handle-ownership source/docs/tests/type fixtures and existing CI workflow
  diff. They are preserve-and-verify context, not current Implementer targets.
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
- `pyproject.toml`
- `uv.lock`

### Written

- Plan-Creator writes revised plan/step state; Plan-Reviewer, Reviewer, and Human write
  their separately owned gate artifacts. The validation-hygiene retrofit's only
  Implementer writes are final-LF bytes in the three declared JSON targets; it creates
  no fresh spec, RED, source, docs, test, type-fixture, or CI artifact.

### Updated

- Plan-Creator may update this plan and step tracker; later independent actors may update
  their own review/human-gate artifacts. Implementer may update exactly the three
  final-LF JSON targets and no other path.

### Deleted

- None. `_LocalLoadedRuntimeModel` and `_create_loaded_runtime_model(...)` are removed
  symbols inside an updated file, not deleted paths. Any path deletion is plan drift.

Artifact path notes:

- 此 topic 不修改 README、package/root exports、version、dependencies、lockfile 或
  release artifacts。
- listed paths are the executable contract. A later need outside these paths stops work
  and returns to `spec-and-plan-finalization`.

## Implementation Steps

1. After fresh plan-review and refreshed revised-scope human-check, Implementer
   preserve-and-verifies all Historical ReadOnly context, including the existing
   `.github/workflows/ci.yml` `Sync dependencies`
   `uv sync --frozen --group dev --extra onnx` diff. It must not rewrite the workflow,
   source, docs, tests, type fixtures, or evidence artifacts.
2. Implementer appends exactly one final LF to each of the three declared human-check
   JSON files without changing JSON text, values, key order, indentation, or any
   non-final byte. These are the only current Implementer writes.
3. Implementer runs the full declared CI-parity/pre-commit validation and inspects each
   JSON diff at byte level, confirming its only representation change is removal of the
   `\ No newline at end of file` marker; it hands evidence to independent review and
   does not author reviewer/human artifacts or close those gates.

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
- CI `Sync dependencies` installs the published ONNX optional runtime before the existing
  Pyright, pytest, and pre-commit commands; its only command difference is `--extra onnx`.
- Revised-scope validation preserves and verifies the existing authorized CI diff; only
  the three declared JSON final LFs may be newly written.
- The CI retrofit has a `trivial` D1 verdict: no fresh RED, test edit, or CI-specific
  spec authoring is required.
- Each of the three final-LF JSON diffs removes only the missing-final-newline marker;
  their parsed JSON and all meaningful text/formatting remain unchanged.
- Run:

```bash
uv run pytest --no-cov tests/model_runtime/runtime_model tests/model_runtime/model_pool tests/model_runtime/model_execution -v
uv run pyright --project plan/local-runtime-handle-ownership-clarification/pyrightconfig.json tests/typecheck/runtime_model_generic_erasure.py tests/typecheck/model_execution_minimal_consumption.py
uv run pytest -v
uv run ruff check src tests plan/local-runtime-handle-ownership-clarification
uv run pyright
git diff --check
uv lock --check
uv sync --frozen --group dev --extra onnx
uv run --no-sync pyright
uv run --no-sync pytest
uv run --no-sync pre-commit run --all-files
git diff -- plan/onnx-local-runtime-acquisition-minimal-boundary/onnx-local-runtime-acquisition-minimal-boundary.human-check.json plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.human-check.json plan/local-runtime-acquisition-documentation-consistency/local-runtime-acquisition-documentation-consistency.human-check.json
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

驗證已完成的 handle-ownership implementation 與 existing CI diff 均被保留，並只對
三個 declared human-check JSON 進行 final-LF normalization。

### Non-Goal

- 不重寫 original handle-ownership source、docs、tests、type fixtures、RED evidence、
  Pyright config 或 existing CI workflow diff。
- 不讓 `LoadedRuntimeModel` 變成 `RuntimeModel`，不新增 `execute(...)`，也不改變
  `ModelExecution`、ONNX acquisition 或任何 public/runtime behavior。

### Current Context

- `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py` now
  contains only the public abstract `LoadedRuntimeModel[RuntimeT]` contract; the prior
  private local class/factory has been removed.
- `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` now owns
  private concrete local-handle construction without a runtime-model factory import or
  `reportPrivateUsage` suppression.
- `src/async_model_gateway/model_runtime/model_execution/execution.py` already owns the
  sole production `_provider_runtime()` call and direct-await injected-invoker seam;
  declared source changes do not modify that file.
- `.github/workflows/ci.yml` already contains the authorized exact dev-plus-ONNX sync
  diff, but it has not yet passed revised-scope CI-parity validation and review.
- The three declared human-check JSON files each currently end with `}` rather than
  final LF; this causes full `pre-commit run --all-files` validation hygiene failures
  without changing their JSON meaning.

### Requirements

1. Original handle-ownership source/docs/tests/type fixtures remain Historical ReadOnly
   preserve-and-verify context; their already-approved ownership contract is not a
   current implementation target.
2. Existing `.github/workflows/ci.yml` dev-plus-ONNX sync diff remains Historical
   ReadOnly and is verified, not rewritten.
3. Only the three declared human-check JSON paths receive exactly one final LF; their
   JSON semantics and all non-final bytes remain unchanged.
4. Planning, review, and human-gate artifacts retain their separately declared owners;
   Implementer does not update them except for the final-LF bytes at the three targets.

### Decisions

- Async-planning status: exempt — cite exemption evidence: the original private
  construction move is complete, and the existing exact CI workflow diff only makes an
  existing optional dependency available before unchanged CI commands. Neither changes
  an async boundary, task ownership, cancellation, timeout, retry, lifecycle, or
  concurrency policy. The added final-LF normalization is byte hygiene only and does
  not change runtime behavior.
- Module/package placement: the original module move is historical ReadOnly context;
  current work does not modify either module.
- CI repair placement: `.github/workflows/ci.yml` existing `Sync dependencies` diff is
  Historical ReadOnly preserve-and-verify context; current work does not modify it.
- Final-LF repair placement: only the three exact human-check JSON paths declared in
  `Artifact Paths`; no JSON parser, schema, or semantic rewrite is allowed.
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

### Historical ReadOnly Context / Current Writable Targets

Historical ReadOnly context:

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
- `.github/workflows/ci.yml`

Current Implementer writable targets only:

- `plan/onnx-local-runtime-acquisition-minimal-boundary/onnx-local-runtime-acquisition-minimal-boundary.human-check.json`
- `plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.human-check.json`
- `plan/local-runtime-acquisition-documentation-consistency/local-runtime-acquisition-documentation-consistency.human-check.json`

Candidate files to inspect without modification:

- `src/async_model_gateway/model_runtime/model_execution/execution.py`
- `src/async_model_gateway/model_runtime/model_pool/pool.py`
- `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py`
- `tests/model_runtime/model_execution/test_model_execution.py`
- `tests/typecheck/onnx_local_runtime_acquisition.py`

### Implementation Steps

The original handle-ownership steps are historical ReadOnly evidence. The current
trivial retrofit has exactly these Implementer actions:

1. Preserve-and-verify all historical context, including the existing CI sync diff;
   make no write to any source, docs, test, type-fixture, evidence, or workflow path.
2. Append one final LF, and no other byte, to each declared human-check JSON target.
   Inspect their raw diffs to verify JSON text, values, key order, and indentation are
   untouched.
3. Run the full pre-commit all-files command together with CI-parity validation and
   `git diff --check`; obtain fresh independent review for the expanded path set.

### Test Plan

- Historical regression verification — existing runtime-model, model-pool,
  model-execution, and type-fixture checks validate the ReadOnly handle-ownership
  contract without test edits.
- CI parity — the frozen dev-plus-ONNX sync succeeds and the unchanged no-sync Pyright,
  pytest, and pre-commit commands complete with the optional runtime installed.
- Validation hygiene — raw diffs for all three human-check JSON targets show only a
  final-LF normalization, while their JSON values/order/indentation remain unchanged.

### Validation Commands

```bash
uv run --extra onnx pytest --no-cov tests/model_runtime/runtime_model tests/model_runtime/model_pool tests/model_runtime/model_execution -v
uv run --extra onnx pyright --project plan/local-runtime-handle-ownership-clarification/pyrightconfig.json tests/typecheck/runtime_model_generic_erasure.py tests/typecheck/model_execution_minimal_consumption.py
uv run --extra onnx pytest -v
uv run --extra onnx ruff check src tests plan/local-runtime-handle-ownership-clarification
uv run --extra onnx pyright
git diff --check
uv lock --check
uv sync --frozen --group dev --extra onnx
uv run --no-sync pyright
uv run --no-sync pytest
uv run --no-sync pre-commit run --all-files
git diff -- plan/onnx-local-runtime-acquisition-minimal-boundary/onnx-local-runtime-acquisition-minimal-boundary.human-check.json plan/local-runtime-handle-ownership-clarification/local-runtime-handle-ownership-clarification.human-check.json plan/local-runtime-acquisition-documentation-consistency/local-runtime-acquisition-documentation-consistency.human-check.json
```

### Risks

- Moving the private concrete class can accidentally leave a hidden factory import,
  private-use suppression, or stale type fixture, which would preserve the ownership
  violation despite green behavioral tests.
- A raw-text ownership assertion can confuse abstract/test-local declarations with call
  expressions; the required production-tree AST/source test must distinguish them.
- Documentation can overstate the opaque handle as an executable provider adapter; its
  wording must remain bounded to acquisition and existing `ModelExecution` ownership.
- Changing any CI command beyond the sync extra, or masking the missing optional runtime
  with a lazy-import/type suppression change, would widen this bounded repair.
- Reformatting a target JSON, changing any gate value, or changing a byte beyond the
  final LF would corrupt the historical human-gate evidence and fail this retrofit.

### Rollback Plan

Remove only the added final LF from the three declared JSON targets through the
validation-hygiene retrofit commit. Do not revert or rewrite the historical
handle-ownership source/docs/tests/type fixtures or existing CI workflow diff as part of
this retrofit rollback.

### Open Questions

None.
