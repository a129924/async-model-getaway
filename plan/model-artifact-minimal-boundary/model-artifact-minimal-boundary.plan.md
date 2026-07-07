> Semantic warning: 在 authoring 當下找不到
> `analysis/model-artifact-minimal-boundary/requirements.md` 與
> `analysis/model-artifact-minimal-boundary/technical-spec.md`。此 plan
> 依據 repo exploration、已鎖定的 human decisions，以及現有 docs/specs
> boundary 撰寫；analysis layer 目前屬 incomplete-layer mode，不得視為已補齊。

# model-artifact-minimal-boundary

## Goal / Outcome

- 以 repo-visible planning artifacts 凍結 `ModelArtifact` +
  `LoaderFamily` shared read contract 的最小 Python boundary，讓後續實作只需在
  明確受限的 source / tests / docs paths 內落地，不重新打開
  `LocalModelLoader`、`ModelPool` 或 broader model-side acquisition scope。
- 當此 topic 完成時，repository 會有一個狹義 public surface
  `async_model_gateway.model_artifact`，只公開 `ModelArtifact` 與
  bounded-enum `LoaderFamily`；此 shared read contract 僅承載
  `loader_family`、`artifact_path` 與 `loader_options`，而 `LocalModelLoader`
  仍維持 docs-level deferred boundary。

## Scope

- **In scope**:
  - 在 `plan/model-artifact-minimal-boundary/` 下維護本 topic 的
    `plan.md`、`step.md` 與 `spec.md`。
  - 規劃 `src/async_model_gateway/model_artifact/` 下最小 shared read contract
    package surface，只落地 `ModelArtifact` 與 `LoaderFamily`。
  - 規劃對應 `tests/model_artifact/` pytest coverage，以及必要的 repo-visible
    architecture / spec wording alignment。
  - 明確鎖定 conditional `release` workflow：README / version metadata
    保留為 merge 後 release contract，不進入 `implement-plan`。

- **Out of scope**:
  - 任何 `LocalModelLoader` source/test implementation。
  - 任何 `ModelPool` runtime lifecycle、artifact I/O、resource ownership、
    timeout / cancellation、backend taxonomy 或 `runtime-model` acquisition
    behavior。
  - 任何把 `model_artifact` 與 `model-payload` 混用、把
    `LoaderFamily` 擴張成 loader registry、或加入副檔名 / path / content
    guessing 的行為。
  - 任何 `ModelGateway`、`ModelExecution`、`ResponseCache`、
    `ModelRegistry` 或 broader orchestration / release automation rework。

## Locked Decisions

- 此 topic 已鎖定為 split-topic；本輪只落地 `ModelArtifact` +
  `LoaderFamily` shared read contract。
- 此 topic 明確採用 Python planning extension path，並保留 companion
  `*.step.md` 與 `*.spec.md` artifacts。
- D1 verdict: `non-trivial`。此 topic 會新增 public Python surface、跨 docs
  wording alignment，且需凍結 import boundary、最小欄位 contract 與
  conditional release intent。
- `LocalModelLoader` 維持 docs-level deferred boundary；本 topic 不新增
  `local_model_loader.py`、不新增 loader I/O tests，也不把 deferred
  boundary 偷渡成 executable behavior。
- `ModelArtifact` 是 producer 與 local model side 之間的 shared read
  contract，不是 `payload-hash` identity material，不參與
  `ModelRegistry` freshness authority。
- public package / source root 固定為 `async_model_gateway.model_artifact` /
  `src/async_model_gateway/model_artifact/`；不得改走 `model_pool` package
  lane，也不得要求 root package re-export 新 surface。
- tests lane 固定為 `tests/model_artifact/`；不得改走 `tests/model_pool/`
  或任何其他 topic lane。
- `ModelArtifact` 最小欄位固定只有 `loader_family`、`artifact_path`、
  `loader_options`；不得新增 `artifact_locator`、`loader_settings`、
  `delivery_target` 或其他 extra contract。
- `LoaderFamily` 固定為 bounded enum；starter vocabulary 只允許
  `pickle`、`torch`、`onnx`。family 值必須由 producer 明示提供，不得由
  副檔名、path 片段、artifact content、object shape 或 fallback
  heuristics 猜測。
- release workflow 啟用；release-facing metadata files 只能保留在下方的
  stable-library metadata 與 merge 後的 `release` workflow，不能進入
  `implement-plan` steps。
- authoring 當下觀察到的 package version baseline 是 `0.4.4`；若無其他先行
  release，此 topic 的預期下一個 release tag 是 `v0.4.5`。

## Boundaries / Exclusions

- Planning actor 只負責 author 本 topic 的 planning artifacts；不實作 source、
  tests、docs、version bump、tag 或 release notes。
- Implementer 之後只能修改 `## Artifact Paths` 中明確列出的 pre-merge
  implementation paths；若需要新檔、額外 docs sweep、或 broader model-side
  package layout，必須回到 `spec-and-plan-finalization`。
- Reviewer 只負責獨立 plan verdict 與後續 implementation review；reviewer
  不代替 creator 寫 implementation steps，也不代替 Human 關閉 gates。
- Human gate 仍必須獨立存在；即使本輪不建立 human-owned artifact，也不得把
  chat consensus、reviewer silence 或 PR 綠燈視為 `human check`。
- 此 topic 不重寫 repo workflow names、status names、gate semantics，也不把
  conditional release workflow 擴張成自動化 publishing topic。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow
  `spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix -> release`；
  此 topic 已宣告條件式 `release` workflow，因此允許 `merged -> released`。
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

Routing notes:

- analysis layer 目前缺件，已以上方 semantic warning 明示；後續 reviewer /
  implementer 不得把缺件狀態當成可自由擴張 scope 的理由。
- 本輪 creator rework 已完成，topic 已回到 `review-ready`；下一個合法步驟是
  reviewer 在
  `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.plan-review.json`
  重新記錄 verdict。
- `approved` 依 repo contract 必須同時具備 repo-visible review verdict 與未來的
  explicit `human check`；在這兩個 gate 真的存在前，不得進入
  `implement-plan`。
- `release` 只在 `merged` 後成立；release metadata 與 tag / release notes
  不得被誤寫成 pre-merge implementation evidence。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.plan.md` | Planning actor | 本 topic 的 repo-visible execution contract |
| Topic step tracking | `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.step.md` | Implementer | repo-visible implementation progress companion artifact |
| Topic behavior spec | `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.spec.md` | Planning actor | non-trivial Python behavior contract |
| Plan review artifact | `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.plan-review.json` | Reviewer | repo-visible planning gate verdict |
| Human check gate artifact | `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.human-check.json` | Human | explicit repo-visible gate that clears the approved plan for `implement-plan` |
| RED test artifact | `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.red-tests.yaml` | Implementer | `implement-plan` 期間的 repo-visible TDD gate evidence |
| Implementation review artifact | `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.implementation-review.yaml` | Reviewer | repo-visible implementation-review gate evidence |
| Architecture summary | `docs/architecture.md` | Implementer | 對齊 model-side responsibility summary 與 local read contract wording |
| Canonical input boundary spec | `docs/specs/canonical-input-boundary.md` | Implementer | 對齊 `model_artifact` shared read contract 的最小文字與 non-identity semantics |
| Core abstractions boundary spec | `docs/specs/core-abstractions-boundary.md` | Implementer | 對齊 `model_artifact` / `LocalModelLoader` / model-side boundaries 的依賴方向摘要 |
| Model side boundary spec | `docs/specs/model-side-boundary.md` | Implementer | 對齊 `ModelArtifact` / `LoaderFamily` shared read contract 與 `LocalModelLoader` deferred boundary |
| Project summary (release-only) | `README.md` | Implementer | merge 後 `release` workflow 使用的 first-read wording update path，反映最小 `ModelArtifact` / `LoaderFamily` shared read contract 已納入 package baseline |
| Package version source (release-only) | `src/async_model_gateway/__version__.py` | Implementer | merge 後 `release` workflow 使用的 package runtime version patch-bump source |
| Packaging metadata (release-only) | `pyproject.toml` | Implementer | merge 後 `release` workflow 使用的 package version metadata patch-bump source |
| Lockfile metadata (release-only, conditional) | `uv.lock` | Implementer | merge 後 `release` workflow 中 package version metadata 需要同步時的 bounded lockfile sync path |
| Model-artifact package surface | `src/async_model_gateway/model_artifact/__init__.py` | Implementer | topic-local public import surface for `ModelArtifact` and `LoaderFamily` |
| ModelArtifact value contract | `src/async_model_gateway/model_artifact/artifact.py` | Implementer | immutable shared read contract owner for explicit local artifact metadata |
| LoaderFamily bounded enum | `src/async_model_gateway/model_artifact/loader_family.py` | Implementer | explicit producer-supplied loader-family owner |
| Package-surface tests | `tests/model_artifact/test_model_artifact_package_surface.py` | Implementer | 驗證 public import surface narrowness 與 deferred boundary exclusions |
| LoaderFamily tests | `tests/model_artifact/test_loader_family.py` | Implementer | 驗證 bounded enum vocabulary 與 fail-closed behavior |
| ModelArtifact tests | `tests/model_artifact/test_model_artifact.py` | Implementer | 驗證最小欄位、type rejection 與 non-identity semantics |

Artifact path notes:

- 本 topic 不修改 `src/async_model_gateway/__init__.py`、任何
  `model_registry/`、`response_cache/`、`tests/model_registry/`、
  `tests/response_cache/` 或其他既有 plan topic artifacts。
- `README.md`、`src/async_model_gateway/__version__.py`、`pyproject.toml` 與必要時的
  `uv.lock` 已以上述 exact rows 宣告為 release-only artifact paths；它們只供
  merge 後 `release` workflow 使用，不授權進入 pre-merge
  `implement-plan`。
- `model-artifact-minimal-boundary.plan-review.json` 與
  `model-artifact-minimal-boundary.human-check.json` 在本輪不建立，只預留 exact
  future gate paths。
- 若後續工作偏離上述精確 paths，必須停止並回到
  `spec-and-plan-finalization`。

## Stable library metadata

- `README row`: merge 後的 release workflow 需更新 `README.md` 的「目前階段」與
  boundary 摘要，使其明確表達最小 `ModelArtifact` / `LoaderFamily` shared read
  contract 已存在，同時保留 `LocalModelLoader` 為 docs-level deferred boundary。
- `VERSION bump`: `patch bump`；以 authoring 當下觀察到的 `0.4.4` 為 baseline，
  若無 intervening release，預期 next tag 為 `v0.4.5`。
- `release-only metadata files`:
  `src/async_model_gateway/__version__.py`、`pyproject.toml`，以及 package version
  metadata 需要同步時的 `uv.lock`。
- `timing`: `release`。
- `rationale`: 此 topic 會新增 public package boundary，並要求 first-read /
  package version metadata 與 release note 對齊；stable-library effect 以
  merge 後 release workflow 為正式生效時點。
- `release note expectation`: release note 只宣告最小 `ModelArtifact` +
  `LoaderFamily` shared read contract 已納入 package baseline，並明確聲明
  `LocalModelLoader`、artifact I/O 與 `ModelPool` runtime behavior 仍未在此 topic
  落地。

## Implementation Steps

1. 在 `tests/model_artifact/test_model_artifact_package_surface.py`、
   `tests/model_artifact/test_loader_family.py` 與
   `tests/model_artifact/test_model_artifact.py` 新增 RED coverage，並記錄
   `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.red-tests.yaml`；
   測試必須先鎖定 public import surface、bounded `LoaderFamily` vocabulary、
   `ModelArtifact` 最小欄位、non-identity semantics、以及
   `LocalModelLoader` 仍缺席的 boundary。
2. 新增 `src/async_model_gateway/model_artifact/__init__.py`、
   `src/async_model_gateway/model_artifact/loader_family.py` 與
   `src/async_model_gateway/model_artifact/artifact.py`，使 source layout
   維持一檔一概念，而 `async_model_gateway.model_artifact` 只公開
   `ModelArtifact` 與 `LoaderFamily`。
3. 更新 `docs/architecture.md`、`docs/specs/canonical-input-boundary.md`、
   `docs/specs/core-abstractions-boundary.md` 與
   `docs/specs/model-side-boundary.md`，讓 repo-visible wording 一致表達：
   `model_artifact` 是 shared read contract、`LoaderFamily` 必須顯式提供、
   `LoaderFamily` starter vocabulary 只允許 `pickle|torch|onnx`、
   `ModelArtifact` 只承載 `loader_family` / `artifact_path` /
   `loader_options`，且 `LocalModelLoader` 仍是 docs-level deferred boundary。
4. 執行唯一 validation contract：`uv run pytest -q`、
   `uv run ruff check docs src tests plan/model-artifact-minimal-boundary`
   與 `uv run pyright`。先前的 bounded pytest subset 雖然 assertions 全過，
   但會被 repo-wide coverage gate 卡在 `75.94%`，因此不得再作為現行
   execution contract；現行 contract 改為 full-suite `uv run pytest -q`。
   這個 full-suite pytest 只作為 validation contract，並不擴張此 topic 的
   source、docs、tests scope、locked decisions、artifact paths、public
   contract 或 release intent；完成後只更新
   `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.step.md`
   的 implementer-owned state，再交由 reviewer 產出獨立 verdict。

## Validation / Acceptance Checks

- Canonical topic-plan sections、status names、allowed transitions、reviewer
  handoff shape 與條件式 `release` workflow 必須持續符合 repo contracts。
- `model-artifact-minimal-boundary.spec.md` 必須存在，因為此 topic 已鎖定為
  `non-trivial`。
- `model-artifact-minimal-boundary.step.md` 必須鏡像每個編號的 implementation
  step，且在目前階段只允許 `plan-authoring` 完成；`plan-review` 為下一階段，
  其餘 workflow stages 不得預填。
- Validation 必須證明 public import surface 只在
  `async_model_gateway.model_artifact`；root package 與其他既有 package roots
  都不得 re-export 新 surface。
- Validation 必須證明 `LoaderFamily` 是 bounded enum，且 starter vocabulary
  只允許 `pickle`、`torch`、`onnx`；實作不得把 family 當成推論結果。
- Validation 必須證明 `ModelArtifact` 只承載 `loader_family`、
  `artifact_path`、`loader_options`，且 shared read contract 不參與
  `model-payload` identity authority。
- Validation 必須證明 `LocalModelLoader` 在本 topic 中仍缺席 source/test
  surface，並僅以 deferred docs wording 被引用。
- Validation 必須證明 release-facing metadata files 未被寫入
  `implement-plan` steps，並只保留在 stable-library metadata 與 merge 後
  `release` workflow。
- Validation 不得要求新增 loader I/O、artifact existence probing、timeout /
  cancellation policy、resource lifecycle、provider taxonomy 或 broader
  `ModelPool` behavior。

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

- 此 topic merge 後必須進入條件式 `release` workflow。
- release actor 必須在 merge 後更新 `README.md`、`src/async_model_gateway/__version__.py`、
  `pyproject.toml`，並在 package version metadata 需要同步時更新 `uv.lock`。
- 若無 intervening release，release actor 應從 merged state 建立 `v0.4.5`
  tag，並發佈只涵蓋最小 `ModelArtifact` / `LoaderFamily` shared read contract
  的 release notes。
- tag、release notes 與 release-facing metadata 是 merge 後 release action，
  不是 repo file implementation evidence。

## Open Questions / Unresolved Items

- None.

## Non-goals

- 此 topic 不實作 `LocalModelLoader`、不做 local artifact read、也不引入
  concrete backend / serialization adapters。
- 此 topic 不建立 `ModelPool` public owner、resource lifecycle、
  pooling policy、timeout、retry 或 cancellation semantics。
- 此 topic 不改寫 `model-payload` hashing、`ModelRegistry` freshness、
  `ResponseCache` identity、或任何 `runtime-model` execution contract。
- 此 topic 不加入 loader-family guessing、artifact probing、path normalization
  fallback、或 object-shape inference。
- 此 topic 不在本輪建立 reviewer-owned 或 human-owned gate artifact。

## Current Context

- `docs/architecture.md`、`docs/specs/canonical-input-boundary.md`、
  `docs/specs/core-abstractions-boundary.md` 與
  `docs/specs/model-side-boundary.md` 已把 `model_artifact` 視為 local path 的
  shared read contract，但 repo 目前尚無對應 Python package surface。
- repo 已有最小 `ModelRegistry` 與 `ResponseCache` boundaries；它們都強調
  boundary owner 與 import surface 必須狹義且明確，這是本 topic 的直接規範參考。
- `src/async_model_gateway/` 目前沒有 `model_artifact/` package。
- authoring 當下的 package version baseline 為 `0.4.4`，而 working tree 乾淨。
- analysis companion artifacts 缺件，因此本 plan 必須自己明示 incomplete-layer
  mode，而不能假設有既有 technical spec 可依附。

## Requirements

1. `async_model_gateway.model_artifact` 必須成為此 topic 唯一 public import
   surface，並只公開 `ModelArtifact` 與 `LoaderFamily`。
2. `LoaderFamily` 必須是 bounded enum，starter vocabulary 只允許
   `pickle`、`torch`、`onnx`，且 family 值必須由 producer 顯式提供。
3. `ModelArtifact` 必須只明確承載 `loader_family`、`artifact_path` 與
   `loader_options`；不得接受 `model-payload` 或其他 identity material。
4. `ModelArtifact` / `LoaderFamily` 的 source layout 必須維持一檔一概念，且不新增
   `LocalModelLoader` source file。
5. `tests/model_artifact/` 必須成為此 topic 唯一 tests lane，不得改走
   `tests/model_pool/` 或其他 package lane。
6. repo-visible docs 必須一致表達 `model_artifact` 是 shared read contract、
   不是 identity material，且 `LocalModelLoader` 仍 deferred。
7. release-facing metadata files 只能在 stable-library metadata 與 merge 後
   `release` workflow 被引用；不得進入 `implement-plan` steps。

## Decisions

- `Async-planning status:` exempt — cite exemption evidence: 本 topic 只規劃
  immutable value contract、package surface、docs wording 與 release metadata
  timing；不新增 async callable、resource lifecycle、concurrency、timeout 或
  cancellation boundary，且 `LocalModelLoader` 明確 deferred。
- Module/package placement: 新增
  `src/async_model_gateway/model_artifact/` package，並把 public shared read
  contract 固定放在該 package 下。
- New public API: yes — `async_model_gateway.model_artifact` re-export
  `LoaderFamily` 與 `ModelArtifact`。
- Interface changes: yes — 新增一個狹義 public subpackage，但不修改既有 root
  package、`model_registry` 或 `response_cache` public surfaces。
- Breaking changes allowed: no — 此 topic 只新增新 surface，不縮減或改名既有
  public contract。
- New dependencies: no — 維持現有 dependency baseline，不引入新第三方套件。
- Error handling strategy: unknown `LoaderFamily` values、blank
  `artifact_path`、以及 malformed `loader_options` values 都必須 fail closed；
  value-boundary 問題使用 `ValueError` 或 `TypeError`，不得加入 loader-side
  fallback taxonomy。
- Typing strategy: fully typed；`LoaderFamily` 使用 bounded enum，
  `ModelArtifact` 使用 immutable typed value object，`loader_options`
  使用 topic-local JSON-like alias；不使用 `Any`。

## Public Contract / API Changes

- 新增 public subpackage import surface：
  `async_model_gateway.model_artifact`
- `LoaderFamily` public surface：
  `LoaderFamily(str, Enum)`
  - bounded enum vocabulary 只允許 `pickle`、`torch`、`onnx`
  - producer 必須顯式提供 family；不做 suffix / content / object-shape
    inference
- `ModelArtifact` public surface：
  `ModelArtifact(loader_family: LoaderFamily, artifact_path: str, loader_options: dict[str, JSONLike])`
  - `loader_family`: 顯式 loader-family owner
  - `artifact_path`: 顯式 artifact path；不得為空
  - `loader_options`: topic-local JSON-like config bag；只承載 read-time 補充資訊
- 無既有 public API 被修改或移除。

## Affected Files / Modules

Read-only context:

- `AGENTS.md`
- `docs/architecture.md`
- `docs/specs/canonical-input-boundary.md`
- `docs/specs/core-abstractions-boundary.md`
- `docs/specs/model-side-boundary.md`
- `plan/agent-handoff-workflow.md`
- `plan/topic-plan-contract.md`

Written paths:

- `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.plan.md`
- `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.step.md`
- `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.spec.md`
- `src/async_model_gateway/model_artifact/__init__.py`
- `src/async_model_gateway/model_artifact/artifact.py`
- `src/async_model_gateway/model_artifact/loader_family.py`
- `tests/model_artifact/test_model_artifact_package_surface.py`
- `tests/model_artifact/test_loader_family.py`
- `tests/model_artifact/test_model_artifact.py`
- `docs/architecture.md`
- `docs/specs/canonical-input-boundary.md`
- `docs/specs/core-abstractions-boundary.md`
- `docs/specs/model-side-boundary.md`

Deleted paths:

- None.

Likely affected files:

- `src/async_model_gateway/model_artifact/__init__.py`
- `src/async_model_gateway/model_artifact/artifact.py`
- `src/async_model_gateway/model_artifact/loader_family.py`
- `tests/model_artifact/test_model_artifact_package_surface.py`
- `tests/model_artifact/test_loader_family.py`
- `tests/model_artifact/test_model_artifact.py`

Candidate files to inspect:

- `src/async_model_gateway/model_registry/entry.py`
- `src/async_model_gateway/model_registry/model_payload/canonical_hash.py`
- `tests/test_package_entrypoint.py`
- `tests/test_local_path_guard.py`
- `docs/specs/orchestrator-boundary.md`

## Test Plan

Test cases:

- Happy path:
  `tests/model_artifact/test_loader_family.py` 驗證合法 enum members
  `pickle`、`torch`、`onnx` 可被顯式使用；
  `tests/model_artifact/test_model_artifact.py` 驗證合法 `ModelArtifact`
  會保留 `loader_family`、`artifact_path` 與 `loader_options`。
- Invalid input:
  驗證未知 family 值、blank `artifact_path`、與非 JSON-like
  `loader_options` value 會 fail closed。
- Edge case:
  驗證 `loader_options` 可承載空 dict 與巢狀 JSON-like values，但 shared read
  contract 不會推導 `LoaderFamily` 或觸發 artifact probing。
- Regression:
  `tests/model_artifact/test_model_artifact_package_surface.py` 驗證 public
  import surface 只在 `async_model_gateway.model_artifact`，且不暴露
  `LocalModelLoader` 或其他 owner surface；同時保留
  `tests/test_package_entrypoint.py` 與 `tests/test_local_path_guard.py`
  作為既有 repo guard regression matrix。
- Backward compatibility:
  驗證 root package、`model_registry` 與 `response_cache` 既有 import surface
  不會因新 package 引入而被改寫或 re-export。

## Validation Commands

- `uv run pytest -q`
- `uv run ruff check docs src tests plan/model-artifact-minimal-boundary`
- `uv run pyright`

先前的 bounded pytest subset 只保留為 historical reviewer context，不再作為現行 execution contract。

## Risks

- 若 implementer 回到 `model_pool` package lane 或 `tests/model_pool/` tests
  lane，會再次造成 public boundary drift，讓 shared read contract 與已鎖定的人類決策失配。
- 若 implementer 把 `LoaderFamily` 擴張成自由字串、slug contract 或推論機制，
  會重新打開本 topic 已明確排除的 loader-guessing scope。
- 若 release-facing metadata 被提前拉回 `implement-plan`，會再次違反條件式
  `release` workflow 與 human gate timing。

## Rollback Plan

- 若此 topic plan 之後需要回退，只回退
  `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.plan.md`、
  `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.spec.md` 與
  `plan/model-artifact-minimal-boundary/model-artifact-minimal-boundary.step.md`
  的 rework 內容，並重新以 reviewer blocking issues 為基線再 author 一版。
