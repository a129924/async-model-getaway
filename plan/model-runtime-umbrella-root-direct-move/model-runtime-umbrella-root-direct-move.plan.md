> Semantic warning: 在 authoring 當下找不到
> `analysis/model-runtime-umbrella-root-direct-move/requirements.md` 與
> `analysis/model-runtime-umbrella-root-direct-move/technical-spec.md`。此 plan
> 依據 repo exploration、既有 docs/specs wording 與已鎖定的人類決策撰寫；
> analysis layer 目前屬 incomplete-layer mode，不得把缺件狀態視為可自由擴張
> scope 的授權。

# model-runtime-umbrella-root-direct-move

## Goal / Outcome

- 凍結一個 slim、repo-visible 的 topic plan，讓既有最小 shared read contract
  `ModelArtifact` / `LoaderFamily` 直接從
  `async_model_gateway.model_artifact` 移到
  `async_model_gateway.model_runtime.model_artifact`，並以單一 umbrella root
  `model_runtime` 承接後續 model-runtime family layout。
- 當此 topic 完成時，`model_artifact` 的 source layout、tests lane、README 與
  architecture/spec wording 都會對齊新 owner path；舊的
  `async_model_gateway.model_artifact` import path 不保留 compatibility layer，
  但 `ModelArtifact` / `LoaderFamily` 的既有 shared read contract 語意不會在此
  topic 被重新定義。

## Scope

- **In scope**:
  - 建立此 topic 的 canonical plan artifact：
    `plan/model-runtime-umbrella-root-direct-move/model-runtime-umbrella-root-direct-move.plan.md`。
  - 規劃 direct move：
    `src/async_model_gateway/model_artifact/**` ->
    `src/async_model_gateway/model_runtime/model_artifact/**`。
  - 規劃 tests lane direct move：
    `tests/model_artifact/**` ->
    `tests/model_runtime/model_artifact/**`。
  - 規劃 `README.md`、`docs/architecture.md`、
    `docs/specs/canonical-input-boundary.md`、
    `docs/specs/core-abstractions-boundary.md` 與
    `docs/specs/model-side-boundary.md` 的 wording realignment，使其改指向新
    package owner path，同時維持 shared read contract 語意不變。
  - 規劃 repo-visible review 與 `human check` gate evidence paths，以及後續必須跑通的測試 / 靜態檢查 contract。

- **Out of scope**:
  - 任何重新設計 `ModelArtifact` 欄位、`LoaderFamily` vocabulary、或 shared
    read contract semantics 的工作。
  - 任何把 `model_registry`、`response_cache`、`ModelExecution`、
    `ModelGateway`、`ModelPool` 或其他 package roots 一起搬進 `model_runtime`
    的 umbrella sweep。
  - 任何為 `async_model_gateway.model_artifact` 保留 shim、re-export 或相容層。
  - 任何 package version bump、release tag、release note 或 `uv.lock`
    metadata sync。
  - 任何採用 Python planning extension 的 `*.spec.md`、`*.step.md`、
    `*.red-tests.yaml` 或 `*.implementation-review.yaml` companion artifacts。

## Locked Decisions

- umbrella root 已鎖定為單一 `model_runtime`；此 topic 不重新評估多 root 或其他命名。
- direct move 已鎖定：
  `src/async_model_gateway/model_artifact/**` 必須直接移到
  `src/async_model_gateway/model_runtime/model_artifact/**`，不得改成 copy、shim
  或雙寫維持。
- tests lane 已鎖定：
  `tests/model_artifact/**` 必須直接移到
  `tests/model_runtime/model_artifact/**`，不得保留舊 lane 並行。
- breaking change 已明確允許：
  `async_model_gateway.model_artifact` 不保留相容層，舊 import path failure
  屬於預期結果。
- 這次 topic 是在 supersede 舊 package root / tests lane lock，而不是重新定義
  `ModelArtifact` / `LoaderFamily` 語意、欄位、enum vocabulary 或 deferred
  model-side responsibilities。
- `src/async_model_gateway/model_runtime/__init__.py` 只用來建立 umbrella root
  package boundary；此 topic 不要求 `async_model_gateway.model_runtime`
  re-export `ModelArtifact` 或 `LoaderFamily`。
- 此 topic 維持 canonical base-plan path，不採用 Python extension companion
  artifacts；測試成功與 gate evidence 直接寫在本 plan 中，不額外新增
  `*.spec.md` / `*.step.md` 路線。
- analysis layer 目前不完整；除非人類明確 `override` 或後續補齊 analysis
  artifacts，否則下游角色不得把缺件當作重新打開 scope 的理由。
- 目前觀察到的 package version baseline 是 `0.4.6`；此 topic 只宣告 public
  surface move 與 docs wording realignment，不承接 versioning / release
  metadata 變更。
- 此 topic 會影響 stable-library public surface，因此必須保留
  `## Stable library metadata`；但 release workflow 不在本 topic 內啟用。

## Boundaries / Exclusions

- Planning actor 只 author 或 refine 此 topic 的 plan，不實作 source、tests、
  docs 或 gate evidence files。
- Implementer 之後只能修改 `## Artifact Paths` 中列出的精確 repo-visible paths；
  若需要新增其他 package、額外 docs sweep、或 broader umbrella migration，必須回到
  `spec-and-plan-finalization`。
- Reviewer 只負責獨立的 repo-visible plan verdict；reviewer 不實作變更，也不代替
  Human 關閉 `human check` / `human merge`。
- Human gate 必須獨立存在；chat consensus、branch 存在、或 reviewer silence 都不能替代
  `human check`。
- 此 topic 不改 repo workflow names、status model 或 gate semantics。
- 任何想把 `model_registry`、`response_cache` 或其他 boundary 納入
  `model_runtime` umbrella 的需求，都屬於不同 topic。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow
  `spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix`；
  此 topic 不宣告條件式 `release` workflow，因此在 `merged` 停止。
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

- `approved` 必須同時具備
  `plan/model-runtime-umbrella-root-direct-move/model-runtime-umbrella-root-direct-move.plan-review.json`
  的 `approved` verdict，以及
  `plan/model-runtime-umbrella-root-direct-move/model-runtime-umbrella-root-direct-move.human-check.json`
  的明確通過狀態。
- 在 plan review 與 `human check` 兩個 gates 都完成前，不得進入
  `implement-plan`。
- 此 plan 只宣告 review artifact path 與 human-check artifact path；不預填
  reviewer verdict，也不預填 human pass。
- `uv run pytest -q` 是此 topic 的必要 validation contract。full-suite pytest
  只作為驗證 import-path move 沒有殘留破口的證據，不授權擴張 implementation
  scope。
- 若 reviewer 或 implementer 想新增 compatibility layer、保留舊 tests lane、
  或順便 umbrella-move 其他 package，topic 必須先回到
  `spec-and-plan-finalization`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/model-runtime-umbrella-root-direct-move/model-runtime-umbrella-root-direct-move.plan.md` | Planning actor | 此 topic 的 repo-visible execution contract |
| Plan review artifact | `plan/model-runtime-umbrella-root-direct-move/model-runtime-umbrella-root-direct-move.plan-review.json` | Reviewer | repo-visible planning gate verdict |
| Human check gate artifact | `plan/model-runtime-umbrella-root-direct-move/model-runtime-umbrella-root-direct-move.human-check.json` | Human | explicit repo-visible gate evidence that clears the approved plan for `implement-plan` |
| Legacy model-artifact package root | `src/async_model_gateway/model_artifact/__init__.py` | Implementer | direct move 後應刪除的舊 package root |
| Legacy ModelArtifact owner | `src/async_model_gateway/model_artifact/artifact.py` | Implementer | direct move 後應移除的舊 concept owner path |
| Legacy LoaderFamily owner | `src/async_model_gateway/model_artifact/loader_family.py` | Implementer | direct move 後應移除的舊 enum owner path |
| Umbrella root package | `src/async_model_gateway/model_runtime/__init__.py` | Implementer | 建立 `model_runtime` umbrella root 的最小 package boundary |
| New model-artifact package root | `src/async_model_gateway/model_runtime/model_artifact/__init__.py` | Implementer | direct move 後的 topic-local public import surface |
| New ModelArtifact owner | `src/async_model_gateway/model_runtime/model_artifact/artifact.py` | Implementer | moved shared read contract owner |
| New LoaderFamily owner | `src/async_model_gateway/model_runtime/model_artifact/loader_family.py` | Implementer | moved bounded enum owner |
| Legacy model-artifact package-surface tests | `tests/model_artifact/test_model_artifact_package_surface.py` | Implementer | direct move 後應刪除的舊 tests lane file |
| Legacy LoaderFamily tests | `tests/model_artifact/test_loader_family.py` | Implementer | direct move 後應刪除的舊 tests lane file |
| Legacy ModelArtifact tests | `tests/model_artifact/test_model_artifact.py` | Implementer | direct move 後應刪除的舊 tests lane file |
| New model-artifact package-surface tests | `tests/model_runtime/model_artifact/test_model_artifact_package_surface.py` | Implementer | moved package-surface coverage，鎖定新 owner path 與舊 path breaking change |
| New LoaderFamily tests | `tests/model_runtime/model_artifact/test_loader_family.py` | Implementer | moved enum coverage under new tests lane |
| New ModelArtifact tests | `tests/model_runtime/model_artifact/test_model_artifact.py` | Implementer | moved shared read contract coverage under new tests lane |
| Project summary | `README.md` | Implementer | first-read wording 必須改指向 `async_model_gateway.model_runtime.model_artifact` |
| Architecture summary | `docs/architecture.md` | Implementer | 高層責任與 local read contract wording 必須改指向新 owner path |
| Canonical input boundary spec | `docs/specs/canonical-input-boundary.md` | Implementer | `model_artifact` shared read contract wording 改指向新 owner path，但不改 identity semantics |
| Core abstractions boundary spec | `docs/specs/core-abstractions-boundary.md` | Implementer | `model_artifact` / `LocalModelLoader` boundary wording 改指向新 owner path |
| Model side boundary spec | `docs/specs/model-side-boundary.md` | Implementer | `ModelArtifact` / `LoaderFamily` public owner path 與 deferred loader wording 改指向新 package lane |

Artifact path notes:

- `src/async_model_gateway/__version__.py`、`pyproject.toml` 與 `uv.lock`
  刻意不列入 implementation path；它們在本 topic 內是 explicit no-change。
- `model_registry`、`response_cache`、root package
  `src/async_model_gateway/__init__.py`，以及其他 `docs/specs/*` 檔案都不在此
  topic scope 內。
- listed paths 是 executable contract；若後續工作偏離這些精確 paths，必須停止並回到
  `spec-and-plan-finalization`。

## Stable library metadata

- `README row`: 在 `publish-in-progress` 更新 `README.md` 中「目前階段」與最小
  model-artifact boundary 摘要，將 public owner path 從
  `async_model_gateway.model_artifact` 改為
  `async_model_gateway.model_runtime.model_artifact`；不做超出此 breaking move 的
  README sweep。
- `VERSION bump`: no bump。`src/async_model_gateway/__version__.py`、
  `pyproject.toml` 與 `uv.lock` 在本 topic 維持 explicit no-change；authoring
  當下觀察到的 baseline 仍是 `0.4.6`。
- `timing`: `publish-in-progress`。
- `rationale`: 此 topic 影響 public import surface，README 與 repo-visible
  boundary wording 必須與 source/test direct move 同步落地；但 versioning 與
  release metadata 不屬於這個 bounded refactor。
- `release-note expectation`: none in this topic。若未來需要發布，breaking
  import-path 說明必須由獨立 release slice 依 merged state 處理。

## Implementation Steps

1. 新增 `src/async_model_gateway/model_runtime/__init__.py`，並將
   `src/async_model_gateway/model_artifact/__init__.py`、
   `artifact.py`、`loader_family.py` 直接移到
   `src/async_model_gateway/model_runtime/model_artifact/`；移動後不得留下
   `async_model_gateway.model_artifact` shim、re-export 或 compatibility files。
2. 將 `tests/model_artifact/test_model_artifact_package_surface.py`、
   `test_loader_family.py` 與 `test_model_artifact.py` 直接移到
   `tests/model_runtime/model_artifact/`，並更新 assertions / imports，使測試鎖定
   新 owner path，同時明確驗證舊 import path 不再是合法 public surface。
3. 更新 `README.md`、`docs/architecture.md`、
   `docs/specs/canonical-input-boundary.md`、
   `docs/specs/core-abstractions-boundary.md` 與
   `docs/specs/model-side-boundary.md`，讓 repo-visible wording 一致表達：
   umbrella root 是 `model_runtime`、`model_artifact` 已移到新 package lane、
   但 `ModelArtifact` / `LoaderFamily` 語意與 deferred boundaries 不變。
4. 執行 validation：
   `uv run pytest -q`、
   `uv run ruff check README.md docs src tests plan/model-runtime-umbrella-root-direct-move`
   與 `uv run pyright`。只有三個命令都通過，才可視為此 topic 達成「測試成功仍是必要條件」的 contract。

## Validation / Acceptance Checks

- Canonical topic-plan sections、status names、allowed transitions 與 reviewer
  handoff shape 必須持續符合 repo workflow contracts。
- implementation 完成後，唯一合法的 public owner path 必須是
  `async_model_gateway.model_runtime.model_artifact`；舊的
  `async_model_gateway.model_artifact` 不得存在 shim、alias、re-export 或其他相容層。
- implementation 必須證明這次是 package root / tests lane direct move，而不是
  `ModelArtifact` / `LoaderFamily` semantics rewrite；欄位、enum vocabulary 與
  deferred model-side responsibilities 不得在此 topic 被擴張。
- `tests/model_artifact/` 舊 lane 必須移除，且
  `tests/model_runtime/model_artifact/` 新 lane 必須完整承接 coverage。
- `README.md`、`docs/architecture.md`、
  `docs/specs/canonical-input-boundary.md`、
  `docs/specs/core-abstractions-boundary.md` 與
  `docs/specs/model-side-boundary.md` 都必須改指向新 owner path，並清楚表達這只是
  public surface move，不是重新定義 shared read contract。
- `model_registry`、`response_cache` 與其他非列舉 package / tests lanes 必須保持不變。
- `src/async_model_gateway/__version__.py`、`pyproject.toml` 與 `uv.lock`
  必須維持未修改。
- `uv run pytest -q`、`uv run ruff check README.md docs src tests plan/model-runtime-umbrella-root-direct-move`
  與 `uv run pyright` 必須全部通過。

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
- merge 後此 topic 停止；若之後需要 package version bump、release note 或其他發布動作，必須另開 release-facing topic。

## Open Questions / Unresolved Items

- None.
