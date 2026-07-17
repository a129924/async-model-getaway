> Semantic warning — analysis layer INCOMPLETE：`analysis/model-execution-minimal-consumption-boundary/requirements.md` 與 `analysis/model-execution-minimal-consumption-boundary/technical-spec.md` 均不存在。本計畫以已驗證 baseline、Human 鎖定的 release intent 與既有 lightweight `v<semver>` tag evidence 為依據；不得因 optional analysis layer 缺失而擴張 scope。

# model-execution-minimal-consumption-boundary

## Goal / Outcome

建立最小 public `ModelExecution` boundary：消費 `LoadedRuntimeModel[RuntimeT]`，透過既有私有 `_provider_runtime()` handoff 取得 provider runtime，並 direct-await injected async invoker 完成單次 invocation。

Implementation merge 後，以獨立 post-merge release phase 將最小 boundary 如實同步至限定文件與 version metadata，並以線性 `M -> R -> E -> V` commit chain 發布 lightweight tag `v0.6.0`。不建立 `v0.6.0` GitHub Release，也不發布至 PyPI 或 TestPyPI。

## Scope

### In-Scope

#### Implement-plan

- 新增 `async_model_gateway.model_runtime.model_execution` package。
- 新增 public generic class `ModelExecution[RuntimeT, InvocationT, ResultT]`。
- Constructor 以 keyword-only 方式接收 typed async invoker。
- `execute()` 取得既有 provider runtime 並 direct-await invoker 一次。
- 驗證 runtime、invocation、result identity/value 不被轉換。
- 驗證一般 exception 與 `CancelledError` 原樣傳播。
- 驗證 execution seam 保留具體 runtime、invocation、result types。
- 驗證 `ModelPool.acquire()` 仍回傳 `LoadedRuntimeModel[object]`。
- 建立 fresh RED、implementation review 與 code review gates。

#### Release

- Implementation PR Human merge 後，以 fresh `release-human-check` 關閉 release entry gate。
- 更新 `README.md`、`docs/architecture.md`、`docs/specs/model-side-boundary.md` 與 `docs/specs/core-abstractions-boundary.md`，只宣告最小 `ModelExecution` boundary 已存在。
- 將 version 從 `0.5.0` 同步為 `0.6.0` 於 runtime version、packaging metadata 與 lockfile。
- 在 README 與 topic release evidence 記錄狹義 release 摘要。
- 建立 exact linear chain：`M` 是 merged implementation；`R` 是 release docs/version direct child；`E` 是只加入 `release.yaml` 的 direct child；`V` 是只加入 Reviewer-owned `release-review.yaml` 的 direct child。
- Lightweight `v0.6.0` 永遠指向 `R`。
- Reviewer 在 `origin/dev == E` 時唯讀驗證並 author `release-review.yaml` 及其 artifact blob OID。
- 另一位 transport-only Implementer 原樣 commit/push Reviewer artifact 形成 `V`。
- 驗證 `v0.6.0` GitHub Release 不存在、PyPI 與 TestPyPI 均無 `0.6.0`，且 repo 無 publication automation。

### Out-Of-Scope

- Torch、ONNX、Pickle 或其他真實 provider invocation。
- Artifact loading、檔案或網路 I/O。
- Provider adapter registry、framework abstraction 或 `LoaderFamily` dispatch。
- `ModelArtifact` 或 `LoaderFamily` generic 化。
- 修改 `ModelPool.acquire()` 或新增 pool/execution convenience API。
- Cache、reuse、close、unload、timeout、retry、backpressure、task management 或 resource ownership。
- Local/remote provider alignment、`orchestrator`、`ModelGateway` 或完整 gateway execution flow。
- 修改 `docs/specs/orchestrator-boundary.md` 或 `docs/specs/canonical-input-boundary.md`。
- 建立 `v0.6.0` GitHub Release；發布 `0.6.0` 至 PyPI 或 TestPyPI。
- 對 PyPI、TestPyPI 以外 registry 作未驗證的 no-publication 宣稱。
- Annotated tag、additional release assets、release branch 或額外 publication channel。

## Locked Decisions

- Optional analysis artifacts 均不存在；採 semantic-warning routing，不得擴張 locked scope。
- D1 verdict 是 `non-trivial`；async planning 是 `triggered`。
- Public API 固定為：

```python
RuntimeT = TypeVar("RuntimeT")
InvocationT = TypeVar("InvocationT")
ResultT = TypeVar("ResultT")


class ModelExecution(Generic[RuntimeT, InvocationT, ResultT]):
    def __init__(
        self,
        *,
        invoke: Callable[[RuntimeT, InvocationT], Awaitable[ResultT]],
    ) -> None: ...

    async def execute(
        self,
        model: LoadedRuntimeModel[RuntimeT],
        invocation: InvocationT,
    ) -> ResultT: ...
```

- Constructor 只保存 `self._invoke = invoke`。
- `execute()` 完整 production flow 固定為：

```python
runtime = model._provider_runtime()
return await self._invoke(runtime, invocation)
```

- `ModelExecution` 是 `_provider_runtime()` 唯一 production consumer；handoff 保持 private。
- 若 strict Pyright 對唯一 consumer line 報 `reportPrivateUsage`，只允許該行加入 `# pyright: ignore[reportPrivateUsage]`；禁止 file-wide 或未具名 suppression。
- 每次 `execute()` 只呼叫並 await invoker 一次；不建立 task，不使用 gather、fan-out、batch、stream 或 background ownership。
- Result、一般 exception 與 `CancelledError` 原樣傳播；不加入 validation、translation、timeout、retry 或 fallback。
- `ModelPool.acquire()` 與 local loader family 保持 `LoadedRuntimeModel[object]`。
- `model_execution/__init__.py` 只公開 `ModelExecution`；TypeVars 不由 package root 公開；umbrella/root 不 re-export。
- 不新增 dependency。
- Implement-plan 不得提前修改 release-only paths。
- Release version 固定為 `0.6.0`；tag 固定為 lightweight `v0.6.0`。
- Repo 既有 tags 使用 `v<semver>`，既有 release evidence 使用 lightweight tag；Reviewer仍須確認同名 local/remote tag 不存在且無相反 policy。
- Release docs 只宣告最小 `ModelExecution` owner、typed callable seam、direct-await 與原樣 failure/cancellation；不得宣稱 provider invocation、loader I/O、orchestrator、remote execution、lifecycle、timeout 或 retry 已完成。

### Release commit-chain invariants

- Release 開始時 `origin/dev == M`。
- `R.parent == M`；R 只含 Human-authored `release-human-check.json`、四份 docs、README、runtime version、`pyproject.toml` 與 `uv.lock`。
- R commit subject：`chore(release): cut v0.6.0`；push 後 `origin/dev == R`。
- Lightweight `v0.6.0` 從 R 建立且永遠指向 R；不得 move、replace、delete 或 retarget。
- `E.parent == R`；E 只含 `model-execution-minimal-consumption-boundary.release.yaml`。
- E commit subject：`chore(release): record v0.6.0 evidence`；push 後 `origin/dev == E`。
- Reviewer 只能在 `origin/dev == E`、`E.parent == R`、`R.parent == M` 且 tag 指 R 時 review。
- Reviewer只 author `release-review.yaml`，並以 `git hash-object` 提供 exact artifact blob OID；Reviewer不得 commit/push。
- Transport-only Implementer驗證 worktree/staged blob OID 與Reviewer OID一致，不得改任何 byte。
- `V.parent == E`；V 只含 `release-review.yaml`。
- V commit subject：`chore(release): record v0.6.0 review`；commit trailer 記錄 `Reviewer-Blob-OID: <oid>`；push 後 `origin/dev == V`。
- `released` 只在 `origin/dev == V`、M/R/E/V parent 與 path invariants成立、remote V review blob等於Reviewer OID、verdict是`approved`且tag仍指R時成立。
- `needs-rework` verdict也須原樣transport形成V後停止；不得retag、直接修檔或標記released。

### Publication claim boundary

- 只驗證 GitHub repository `a129924/async-model-getaway` 沒有 `v0.6.0` GitHub Release。
- 只驗證 PyPI/TestPyPI distribution `async-model-gateway` 沒有 `0.6.0`。
- 驗證 repo 沒有 PyPI、TestPyPI 或 GitHub Release publication automation。
- 不得延伸為任何 registry 均未發布。

## Boundaries / Exclusions

- Plan-Creator 只建立或修正 plan/spec/step；Plan-Reviewer只產出planning verdict。
- 本revision必須重新通過Plan-Reviewer與fresh pre-implementation Human check；先前結果不得沿用。
- Human關閉pre-implementation human check、human merge及post-merge release-human-check。
- Human author release-human-check；Release Implementer只可原樣transport進R。
- Tester只建立tests、fixture、topic Pyright config與fresh RED，不改production或release-only paths。
- Implementer在implement-plan只改declared production files與step progress，不改tests配合實作。
- Reviewer負責implementation/code/release review，不直接修正；code-review independence由派遣保證。
- Release Reviewer只author `release-review.yaml`與blob OID，不commit/push。
- Transport-only Implementer只原樣transport Reviewer artifact形成V。
- Observer只調度、triage及依repo-visible V verdict report；不修改repo、不手算gate、不author review或tag。
- Scope、path、API、async、private handoff、version、tag mode、M/R/E/V topology或release intent drift返回`spec-and-plan-finalization`。
- Historical planning/review/release evidence不得重寫。

### Release-review artifact schema

```yaml
review: model-execution-minimal-consumption-boundary-release
review_status: COMPLETE
verdict: approved | needs-rework
revision: v0.6.0-release
chain:
  M: {expected_role: merged-implementation, actual_commit: "<sha>"}
  R:
    expected_parent: "<M-sha>"
    expected_only_paths:
      - plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.release-human-check.json
      - README.md
      - docs/architecture.md
      - docs/specs/model-side-boundary.md
      - docs/specs/core-abstractions-boundary.md
      - src/async_model_gateway/__version__.py
      - pyproject.toml
      - uv.lock
    actual_commit: "<sha>"
    actual_parent: "<sha>"
    actual_paths_match: true | false
  E:
    expected_parent: "<R-sha>"
    expected_only_paths:
      - plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.release.yaml
    actual_commit: "<sha>"
    actual_parent: "<sha>"
    actual_paths_match: true | false
  V:
    expected_parent: "<E-sha>"
    expected_only_paths:
      - plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.release-review.yaml
    actual_commit_semantics: SELF
    actual_ref_after_transport: origin/dev
    transport_verification_required: true
reviewer:
  reviewed_release_evidence_blob_oid: "<blob-oid>"
  authored_release_review_blob_oid_delivery: out-of-band
  authored_release_review_blob_oid_algorithm: git-hash-object
  transport_must_preserve_exact_blob: true
origin_dev:
  at_review: "<E-sha>"
  expected_after_transport: SELF
  actual_at_review_matches_E: true | false
tag:
  name: v0.6.0
  expected_kind: lightweight
  expected_target: "<R-sha>"
  actual_kind: lightweight | annotated | missing
  actual_local_target: "<sha-or-null>"
  actual_remote_target: "<sha-or-null>"
  targets_match_R: true | false
docs_version_checks:
  docs_scope_matches: true | false
  deferred_boundaries_preserved: true | false
  runtime_version: "0.6.0"
  pyproject_version: "0.6.0"
  lockfile_version: "0.6.0"
  versions_match: true | false
publication_negative_checks:
  github_release_v0_6_0: {expected_http_status: 404, actual_http_status: "<status>", passed: true | false}
  pypi_0_6_0: {expected_http_status: 404, actual_http_status: "<status>", passed: true | false}
  testpypi_0_6_0: {expected_http_status: 404, actual_http_status: "<status>", passed: true | false}
  publication_automation: {disallowed_matches_found: [], passed: true | false}
blocking_issues:
  - {issue: "<string>", file: "<string>", fix: "<string>"}
```

Reviewer artifact無法內嵌自身blob OID；Reviewer完成後out-of-band提供OID，Transport-only Implementer將OID寫入V trailer並驗證remote V tree blob一致。

## Status / Allowed Transitions

- **Current**：`review-ready`。此materialized revision尚未核准，必須fresh Plan-Reviewer與Human check。
- **Execution model**：`spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix -> release`。
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
  - `merged` -> `released`
- Fresh approved plan review及`human-check.json`的`cleared_for: implement-plan`後Tester才可開始RED。
- Implementation/code reviews approved後才能PR routing；Human merge固定M。
- Human必須author fresh release-human-check後才能建立R。
- Released只依repo-visible V verdict與chain/tag/blob invariants判定；Observer只triage/report。

## Artifact Paths

### Written

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.plan.md` | Plan-Creator | implementation/release contract |
| Python specification | `plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.spec.md` | Plan-Creator | D1 behavior contract |
| Step tracker | `plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.step.md` | Plan-Creator=`plan-authoring`; Plan-Reviewer=`plan-review`; Tester=`tdd-test-authoring`; Implementer=`implementation`; Reviewer=`implementation-review`/`code-review` | 每個actor只更新自己擁有的stage與該phase實際progress |
| Plan review | `plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.plan-review.json` | Plan-Reviewer | fresh verdict |
| Human check | `plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.human-check.json` | Human | implementation clearance |
| RED evidence | `plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.red-tests.yaml` | Tester | fresh RED evidence |
| Topic Pyright config | `plan/model-execution-minimal-consumption-boundary/pyrightconfig.json` | Tester | strict fixture routing |
| Behavior tests | `tests/model_runtime/model_execution/test_model_execution.py` | Tester | execution behavior |
| Package tests | `tests/model_runtime/model_execution/test_model_execution_package_surface.py` | Tester | surface/signatures |
| Static fixture | `tests/typecheck/model_execution_minimal_consumption.py` | Tester | precision/erasure |
| Package initializer | `src/async_model_gateway/model_runtime/model_execution/__init__.py` | Implementer | public surface |
| Execution source | `src/async_model_gateway/model_runtime/model_execution/execution.py` | Implementer | execution owner |
| Implementation review | `plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.implementation-review.yaml` | Reviewer | conformance verdict |
| Code review | `plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.code-review.yaml` | Reviewer | quality verdict |
| README | `README.md` | Release Implementer | R summary |
| Architecture | `docs/architecture.md` | Release Implementer | R boundary status |
| Model-side spec | `docs/specs/model-side-boundary.md` | Release Implementer | R model-side contract |
| Core spec | `docs/specs/core-abstractions-boundary.md` | Release Implementer | R core status |
| Runtime version | `src/async_model_gateway/__version__.py` | Release Implementer | R version |
| Package version | `pyproject.toml` | Release Implementer | R metadata |
| Lockfile | `uv.lock` | Release Implementer | R lock metadata |
| Release Human gate | `plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.release-human-check.json` | Human authors; Implementer transports | R clearance |
| Release evidence | `plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.release.yaml` | Release Implementer | E evidence |
| Release review | `plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.release-review.yaml` | Reviewer authors; transport Implementer commits | V verdict |

### ReadOnly

- `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py`
- `src/async_model_gateway/model_runtime/runtime_model/__init__.py`
- `src/async_model_gateway/model_runtime/model_pool/pool.py`
- `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`
- `src/async_model_gateway/model_runtime/model_pool/__init__.py`
- `src/async_model_gateway/model_runtime/model_artifact/artifact.py`
- `src/async_model_gateway/model_runtime/model_artifact/loader_family.py`
- `src/async_model_gateway/model_runtime/model_artifact/__init__.py`
- `src/async_model_gateway/model_runtime/__init__.py`
- `src/async_model_gateway/__init__.py`
- `docs/specs/orchestrator-boundary.md`
- `docs/specs/canonical-input-boundary.md`
- `.github/workflows/ci.yml`
- 本topic以外所有既有planning/review/release evidence。
- Release前全部release-only paths；R後全部R paths；E後`release.yaml`；Reviewer與transport phase除`release-review.yaml`外全部paths。

### Deleted

None。任何extra path、nonlinear commit、retag或刪檔均為plan drift。

## Stable library metadata

- `README row`：R只宣告最小`ModelExecution` boundary及保留wider boundaries deferred。
- `VERSION bump`：`0.5.0 -> 0.6.0`於runtime、pyproject與lockfile。
- `timing`：release；Human merge與fresh release-human-check後。
- `tag`：lightweight `v0.6.0`永久指R。
- `rationale`：狹義public subpackage需要同步first-read與metadata，不代表完整runtime stack。
- `release summary`：README及`release.yaml`。
- `GitHub Release`：`v0.6.0`不得建立。
- `PyPI/TestPyPI`：`0.6.0`不得發布；不對其他registry作claim。

## Implementation Steps

1. Tester建立`tests/model_runtime/model_execution/test_model_execution.py`。
2. Tester建立`tests/model_runtime/model_execution/test_model_execution_package_surface.py`。
3. Tester建立`tests/typecheck/model_execution_minimal_consumption.py`。
4. Tester建立`plan/model-execution-minimal-consumption-boundary/pyrightconfig.json`。
5. Tester確認`src/async_model_gateway/model_runtime/model_execution/__init__.py`及`src/async_model_gateway/model_runtime/model_execution/execution.py`尚無production implementation diff，執行focused pytest與dedicated Pyright，並將fresh nonzero RED、fixture analysis、requirement mapping及baseline guard寫入`plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.red-tests.yaml`。
6. Implementer建立`src/async_model_gateway/model_runtime/model_execution/execution.py`，定義三個locked TypeVars、typed constructor及exact two-line`execute()` flow。
7. Implementer執行strict Pyright；只有`src/async_model_gateway/model_runtime/model_execution/execution.py`的唯一`model._provider_runtime()`consumer line實際報`reportPrivateUsage`時，才在該行加入具名line-local suppression。
8. Implementer建立`src/async_model_gateway/model_runtime/model_execution/__init__.py`，只re-export`ModelExecution`。
9. Implementer執行全部pre-merge validation commands，確認focused tests及dedicated Pyright由RED轉GREEN，且`tests/typecheck/model_execution_minimal_consumption.py`確實被分析。
10. Implementer確認pre-merge Written以外無diff、全部ReadOnly及release-only paths無變更、Deleted為None，並只更新`plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.step.md`中的implementation phase與實際完成entries。

Reviewer/Human/PR/release工作不屬於Implementation Steps。

## Validation / Acceptance Checks

- API、two-line flow、identity、await-once、failure/cancellation及typing contracts成立。
- 無task、timeout、retry、adapter、I/O、dispatch或resource ownership。
- Package只公開`ModelExecution`；pool erasure不變；禁止dynamic module loading。
- Pre-merge commands全數通過且release-only paths無diff。
- M/R/E/V direct-child、path allowlist、origin/dev及tag-to-R invariants成立。
- Reviewer artifact blob OID由transport原樣保存；approved才released，needs-rework保存V後停止。
- GitHub Release、PyPI、TestPyPI checks各為404；automation scan無match；不外推其他registry。

## Reviewer Handoff

```json
{
  "verdict": "approved | needs-rework",
  "blocking_issues": [{"issue": "string", "file": "string", "fix": "string"}],
  "copilot_feedback_triage": {"ADDRESS": [], "DISCUSS": [], "SKIP": []}
}
```

## Post-merge / release actions

1. Human merge固定M；Human author release-human-check。
2. Release Implementer確認local/dev/origin/dev均為M，建立並驗證R，push dev。
3. Release Implementer從R建立/push lightweight`v0.6.0`。
4. Release Implementer執行negative checks，author/commit/push只含`release.yaml`的E。
5. Reviewer在origin/dev==E時獨立驗證、author`release-review.yaml`並提供blob OID。
6. Transport-only Implementer驗證exact OID，commit/push只含review artifact的V及OID trailer。
7. Needs-rework則保存V並停止；approved且remote V/chain/blob/tag成立時Observer只triage/report released。

## Open Questions / Unresolved Items

None。

# Python Implementation Plan Extension

## Goal

新增最小typed async execution owner，透過既有private handoff執行單一injected invoker並保留三個generic types；merge後依M/R/E/V發布`0.6.0` lightweight tag release。

## Non-goals

### Non-Goal

- 不實作provider、adapter、loader I/O、remote execution或orchestration。
- 不修改LoadedRuntimeModel、ModelPool、artifact contracts或umbrella/root。
- 不加入cache、timeout、retry、task或resource ownership。
- Implement-plan不修改docs/version/lock。
- 不建立GitHub Release、不發布PyPI/TestPyPI、不對其他registry作claim。

## Current Context

`LoadedRuntimeModel[RuntimeT]`已是covariant generic，`_provider_runtime() -> RuntimeT`是private handoff；pool/loader仍回傳`LoadedRuntimeModel[object]`。Version baseline是`0.5.0`，既有tag為`v<semver>`且最近evidence為lightweight tag。

## Requirements

### In-Scope

1. 新增public`ModelExecution`與locked三generic signatures。
2. Direct-await一次並原樣傳播identity/result/failure/cancellation。
3. Strict fixture保留precision且pool erasure不變。
4. Fresh RED、implementation review及code review。
5. Post-merge限定docs/version/lock、M/R/E/V、lightweight`v0.6.0`、Reviewer blob transport與negative publication evidence。

### Out-Of-Scope

- Validation/schema normalization、provider/registry/dispatch、I/O、multiple invocation/concurrency、lifecycle、timeout/retry。
- Implement-plan release promotion；orchestrator/canonical-input spec edits；annotated tag或publication。

## Decisions

- Async-planning status: triggered — cite trigger evidence: public async execute、direct await、failure與cancellation policy。
- Module/package placement: implement-plan只新增`model_execution/__init__.py`與`execution.py`；release按canonical exact table。
- New public API: yes — `ModelExecution` locked signatures。
- Interface changes: no existing changes；additive、non-breaking。
- New dependencies: no。
- Error handling: 原樣傳播；無custom exception。
- Typing: strict、三個invariant TypeVars、無Any、conditional unique suppression。

### Async boundary decision

Constructor sync；`execute()`是唯一async boundary。

### Resource lifecycle decision

無resource ownership或cleanup。

### Concurrency model

單一sequential direct-await；無task/fan-out/batch/stream。

### Failure model

同步、awaitable與CancelledError原樣傳播；無translation/grouping。

### Cancellation / timeout policy

Caller owns cancellation；無shield、timeout、retry。

### Validation plan

Pytest驗證await/identity/failure/cancellation；strict fixture驗證precision/erasure；release驗證M/R/E/V、blob、tag與404 checks。

### Handoff notes for the implementer

保持exact flow；pre-merge不得碰release paths；R/E/transport各遵守exact allowlist，transport不得改Reviewer bytes。

## Public Contract / API Changes

`from async_model_gateway.model_runtime.model_execution import ModelExecution`；package `__all__`只含該class，umbrella/root不變，version於release改為`0.6.0`。

## Affected Files / Modules

### Written

Canonical `## Artifact Paths` exact table是唯一authority，包含plan/spec/step、gate/evidence、兩個tests、一個fixture、兩個production files、四份docs、三個version/lock paths及release human/evidence/review artifacts。

### ReadOnly

Canonical exact `### ReadOnly`清單與phase freeze rules是唯一authority；不得以broad directory放寬。

### Deleted

None。

## Implementation Steps

1. Tester建立`tests/model_runtime/model_execution/test_model_execution.py`。
2. Tester建立`tests/model_runtime/model_execution/test_model_execution_package_surface.py`。
3. Tester建立`tests/typecheck/model_execution_minimal_consumption.py`。
4. Tester建立`plan/model-execution-minimal-consumption-boundary/pyrightconfig.json`。
5. Tester確認`src/async_model_gateway/model_runtime/model_execution/__init__.py`及`src/async_model_gateway/model_runtime/model_execution/execution.py`尚無production implementation diff，執行focused pytest與dedicated Pyright，並將fresh nonzero RED、fixture analysis、requirement mapping及baseline guard寫入`plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.red-tests.yaml`。
6. Implementer建立`src/async_model_gateway/model_runtime/model_execution/execution.py`，定義三個locked TypeVars、typed constructor及exact two-line`execute()` flow。
7. Implementer執行strict Pyright；只有`src/async_model_gateway/model_runtime/model_execution/execution.py`的唯一`model._provider_runtime()`consumer line實際報`reportPrivateUsage`時，才在該行加入具名line-local suppression。
8. Implementer建立`src/async_model_gateway/model_runtime/model_execution/__init__.py`，只re-export`ModelExecution`。
9. Implementer執行全部pre-merge validation commands，確認focused tests及dedicated Pyright由RED轉GREEN，且`tests/typecheck/model_execution_minimal_consumption.py`確實被分析。
10. Implementer確認pre-merge Written以外無diff、全部ReadOnly及release-only paths無變更、Deleted為None，並只更新`plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.step.md`中的implementation phase與實際完成entries。

## Test Plan

### TestCase

1. Runtime、invocation、result identity保持。
2. Invoker awaited exactly once。
3. 一般exception與CancelledError原樣傳播。
4. Static fixture保留FakeRuntime/FakeInvocation/FakeResult，pool仍erased。
5. Package只公開ModelExecution；unique production consumer及dependency isolation。
6. M/R/E/V linear、R tag permanent、E/V single-path與Reviewer blob transport。
7. GitHub Release、PyPI、TestPyPI 404及automation無match。
8. Needs-rework仍transport V但不released。

Required category mapping：

- **Happy path**：TestCase 1、2；runtime、invocation與result identity保持，且invoker exactly once awaited。
- **Invalid input**：TestCase 3；invoker拒絕invocation並拋出sentinel一般exception，`ModelExecution`不新增validation且原樣傳播。
- **Edge case**：TestCase 3；`CancelledError`原樣傳播，不被catch、shield或translate。
- **Regression**：TestCase 5；package surface、唯一production consumer與dependency isolation維持locked boundary。
- **Backward compatibility**：TestCase 4、5；pool acquisition仍erased為`LoadedRuntimeModel[object]`，umbrella/root exports不變。
- **Static typing**：TestCase 4；strict fixture保留`FakeRuntime`、`FakeInvocation`與`FakeResult`。
- **Release topology**：TestCase 6、8；M/R/E/V linear、R tag permanent、E/V single-path、Reviewer blob transport與needs-rework stop semantics。
- **Publication exclusions**：TestCase 7；GitHub Release、PyPI、TestPyPI各為HTTP 404，publication automation scan無match。

測試只用static imports，不得dynamic module loading。

## Validation Commands

```bash
uv run pytest --no-cov tests/model_runtime/model_execution -v
uv run pyright --project plan/model-execution-minimal-consumption-boundary/pyrightconfig.json tests/typecheck/model_execution_minimal_consumption.py
uv run pytest -v
uv run ruff check src tests plan/model-execution-minimal-consumption-boundary
uv run pyright
uv lock --check
git diff --check
```

### Release R preflight

```bash
git fetch origin dev --tags
git rev-parse dev
git rev-parse origin/dev
git tag --list v0.6.0
git ls-remote --tags origin refs/tags/v0.6.0
uv run pytest --no-cov tests/model_runtime/model_execution -v
uv run pytest -v
uv run ruff check src tests plan/model-execution-minimal-consumption-boundary
uv run pyright
uv lock --check
git diff --check
rg -n '0\.6\.0' README.md pyproject.toml src/async_model_gateway/__version__.py uv.lock
```

Expected semantics：local `dev`與`origin/dev`均等於M；local與remote `v0.6.0`查詢均無輸出；所有quality gates通過；三個version sources均為`0.6.0`；R staged diff只含R allowlist。

### Final M/R/E/V topology

在V push完成後，由`origin/dev`反向解析exact linear chain：

```bash
V="$(git rev-parse origin/dev)"
E="$(git rev-parse "${V}^")"
R="$(git rev-parse "${E}^")"
M="$(git rev-parse "${R}^")"

test "$(git rev-parse "${V}^")" = "${E}"
test "$(git rev-parse "${E}^")" = "${R}"
test "$(git rev-parse "${R}^")" = "${M}"
test "$(git rev-parse origin/dev)" = "${V}"
```

Expected semantics：四個`test`均exit `0`；`V.parent == E`、`E.parent == R`、`R.parent == M`且`origin/dev == V`。

### Per-commit path allowlists

```bash
test "$(git diff-tree --no-commit-id --name-only -r "${R}" | sort)" = "$(printf '%s\n' \
  README.md \
  docs/architecture.md \
  docs/specs/core-abstractions-boundary.md \
  docs/specs/model-side-boundary.md \
  plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.release-human-check.json \
  pyproject.toml \
  src/async_model_gateway/__version__.py \
  uv.lock | sort)"

test "$(git diff-tree --no-commit-id --name-only -r "${E}")" = \
  "plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.release.yaml"

test "$(git diff-tree --no-commit-id --name-only -r "${V}")" = \
  "plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.release-review.yaml"
```

Expected semantics：三個`test`均exit `0`；R只含八個locked paths，E只含`release.yaml`，V只含`release-review.yaml`。

### Reviewer blob transport integrity

```bash
REVIEW_PATH="plan/model-execution-minimal-consumption-boundary/model-execution-minimal-consumption-boundary.release-review.yaml"
REVIEWER_BLOB_OID="$(git show -s --format=%B "${V}" | sed -n 's/^Reviewer-Blob-OID: //p')"
REMOTE_REVIEW_BLOB_OID="$(git rev-parse "${V}:${REVIEW_PATH}")"

test -n "${REVIEWER_BLOB_OID}"
test "${REMOTE_REVIEW_BLOB_OID}" = "${REVIEWER_BLOB_OID}"
```

Expected semantics：commit trailer包含單一non-empty Reviewer blob OID，且V tree中的review blob與Reviewer handoff OID完全相同；兩個`test`均exit `0`。

### Lightweight tag target

```bash
test "$(git cat-file -t v0.6.0)" = "commit"
test "$(git rev-parse 'v0.6.0^{commit}')" = "${R}"
REMOTE_TAG_TARGET="$(git ls-remote --tags origin refs/tags/v0.6.0 | awk '{print $1}')"
test "${REMOTE_TAG_TARGET}" = "${R}"
```

Expected semantics：`git cat-file -t`回傳`commit`，證明tag為lightweight；local與remote `v0.6.0`均解析到R；三個`test`均exit `0`。

### GitHub Release negative check

```bash
gh api -i repos/a129924/async-model-getaway/releases/tags/v0.6.0
```

Expected semantics：command因not found回傳nonzero，response header明確為HTTP `404`。Network/auth failure或其他HTTP status不得記為pass。Actual status與exit code都必須寫入E及release-review。

### PyPI negative check

```bash
curl --silent --show-error \
  --output /dev/null \
  --write-out '%{http_code}\n' \
  https://pypi.org/pypi/async-model-gateway/0.6.0/json
```

Expected semantics：stdout精確為`404`。Network failure或其他HTTP status不得記為pass；actual HTTP status寫入E及release-review。

### TestPyPI negative check

```bash
curl --silent --show-error \
  --output /dev/null \
  --write-out '%{http_code}\n' \
  https://test.pypi.org/pypi/async-model-gateway/0.6.0/json
```

Expected semantics：stdout精確為`404`。Network failure或其他HTTP status不得記為pass；actual HTTP status寫入E及release-review。

### Publication automation negative check

```bash
rg -n \
  '(pypi|testpypi|twine|uv publish|hatch publish|poetry publish|gh release|softprops/action-gh-release|pypa/gh-action-pypi-publish)' \
  .github/workflows/ci.yml \
  pyproject.toml
```

Expected semantics：無match且`rg` exit code為`1`。這個nonzero exit是預期的no-match signal，不得誤判為validation failure；若有任何match或其他execution error即不得pass。Command、exit code與empty matches都寫入E及release-review。

所有release commands必須在對應phase執行：R preflight在tag前；negative checks由Release Implementer寫入E且Reviewer在`origin/dev == E`時獨立重跑；final M/R/E/V、blob、origin/dev與tag checks在V transport後確認。No-publication結論只限`v0.6.0` GitHub Release、PyPI與TestPyPI `0.6.0`。

## Risks

- Private suppression過寬、type erasure、unawaited invocation、exception swallowing或export drift。
- Docs overclaim、version drift、tag collision/wrong kind/retarget、nonlinear R/E/V、extra paths或Reviewer blob mutation。
- Network failure誤記404、automation無match exit status誤判、claim擴張至其他registry。

## Rollback Plan

- Merge前移除topic新files並保持ReadOnly/release paths無diff。
- M後R前未通過Human gate則停止。
- R後tag前問題由bounded correction處理；tag push後不得retag。
- E後Reviewer即使needs-rework仍author並transport V後停止。
- V後不amend/force-push/rewrite M/R/E/V；新問題回planning。

## Open Questions

None。
