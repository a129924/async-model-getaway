> Semantic warning: 在 authoring 當下找不到
> `analysis/model-artifact-release-wording-correction/requirements.md` 與
> `analysis/model-artifact-release-wording-correction/technical-spec.md`。此
> plan 依據已發布的 `v0.4.5` baseline、目前 `README.md` / package version
> state、以及明確 human 指示撰寫；analysis layer 目前屬 incomplete-layer
> mode，不得視為已補齊。

# model-artifact-release-wording-correction

## Goal / Outcome

- 以新的 bounded follow-up topic 規劃 `ModelArtifact` release-facing wording
  correction，讓後續工作只需在精確的 release-facing artifacts 內修正
  `README.md` wording、同步必要的 patch-release metadata，且不 retroactively
  改寫已發布的 `v0.4.5` history。
- 當此 topic 完成時，repo 會有一份獨立的 release-only execution contract：
  它只允許 forward-only 的 wording correction，並要求任何對外修正都經由下一個
  patch release 進行。

## Scope

- **In scope**:
  - 在 `plan/model-artifact-release-wording-correction/` 下維護本 topic 的
    `plan.md`。
  - 規劃 `README.md` 中 package baseline / first-read summary 的最小必要
    release-facing wording correction，使 `ModelArtifact` 與既有 shared read
    contract 一致。
  - 規劃 `src/async_model_gateway/__version__.py`、`pyproject.toml`，以及必要時
    `uv.lock` 的 patch-release metadata 更新。
  - 規劃 merge 後的條件式 release workflow、patch tag 條件處理，與 release note
    限界。

- **Out of scope**:
  - 任何 `ModelArtifact`、`LoaderFamily`、`LocalModelLoader`、`ModelPool`、
    `ModelRegistry`、`ResponseCache` 或其他 Python/runtime/docs boundary 的實作或
    重設計。
  - 任何 retroactive 改寫 `v0.4.5` tag、release record、merged commit history，
    或既有 released-state 敘述。
  - 任何 `docs/architecture.md`、`docs/specs/`、`src/async_model_gateway/model_artifact/`、
    `tests/`，或 `plan/model-artifact-minimal-boundary/` 既有 artifacts 的修改。
  - 任何超出 `README.md` 與 patch-release metadata 的 broader docs sweep、source
    implementation、review artifact 預填、commit、push、merge 或 release execution。

## Locked Decisions

- analysis-layer routing 採 incomplete-layer mode：此 topic 沒有
  `analysis/model-artifact-release-wording-correction/requirements.md` 或
  `technical-spec.md`，且本次 plan 依據 human 明確指示在缺件情況下 author。
- 此 topic 是新的 post-release follow-up topic；它不回寫、不覆寫，也不重新詮釋
  `model-artifact-minimal-boundary` 的既有 implementation / release history。
- 此 topic 只處理 release-facing wording correction；任何 code、tests、architecture
  docs 或 public contract 擴張都必須另開新 topic。
- `README.md` correction 固定為最小必要修正：`ModelArtifact` 必須被描述為
  shared read contract 的一部分，並與 explicit `LoaderFamily` vocabulary 搭配；
  不得再以 `local artifact identity` 或其他 identity authority 語義對外表述。
- 此 topic 是 stable-library / release-facing topic，因此必須包含
  `## Stable library metadata`，並啟用條件式 `release` workflow。
- repo 目前沒有 root `VERSION` 檔；此 topic 的 executable version sources
  固定為 `src/async_model_gateway/__version__.py` 與 `pyproject.toml`，若 package
  version metadata 需要同步，`uv.lock` 也在 scope 內。
- authoring 當下觀察到的 released baseline 是 `0.4.5`；若在此 topic release
  前沒有其他 intervening release，預期 next patch tag 是 `v0.4.6`。若 current
  baseline 在 release 前已前進，則 release actor 必須以當下最新 released
  baseline 的下一個 patch version 發佈，但仍只允許處理本 topic 的 wording
  correction。
- 此 topic 不採用 Python planning extension path；`*.step.md` 與 `*.spec.md`
  在本 topic 中刻意缺席。若後續 scope 擴張到 Python implementation contract，
  必須先回到 `spec-and-plan-finalization` 重開 planning。

## Boundaries / Exclusions

- Planning actor 只負責 author 本 topic 的 planning artifact；不實作
  `README.md`、version metadata、tag、release note 或任何 source/docs/test 變更。
- Implementer 之後只能修改 `## Artifact Paths` 明確列出的 release-facing paths；
  若需要碰觸其他 docs/specs/source/tests paths，必須回到
  `spec-and-plan-finalization`。
- Reviewer 只負責 repo-visible plan verdict；reviewer 不代替 creator 寫 release
  correction，也不代替 Human 關閉 gate。
- Human gate 仍必須獨立存在；plan review 通過不代表可直接進入
  `implement-plan`。
- **Forbidden actions**:
  - retag、刪除、取代、重新發布或 rewrite `v0.4.5`
  - 改寫既有 merged / released history，使 `v0.4.5` 看起來像原本就沒有 wording mismatch
  - 透過本 topic 修改 `plan/model-artifact-minimal-boundary/` 的既有 plan/review/gate artifacts
  - 透過本 topic 擴張成 architecture docs sweep、Python behavior change、tests rework 或 public API 調整
  - 預填 reviewer-owned `*.plan-review.json` 或 human-owned `*.human-check.json`

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow
  `spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix -> release`；
  此 topic 明確宣告 release-facing timing，因此允許 `merged -> released`。
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

- 進入 `implement-plan` 前，必須先有
  `plan/model-artifact-release-wording-correction/model-artifact-release-wording-correction.plan-review.json`
  的 `approved` verdict，並由
  `plan/model-artifact-release-wording-correction/model-artifact-release-wording-correction.human-check.json`
  明確記錄 human check cleared evidence。
- 在 planning authoring 當下，上述 reviewer / human gate artifacts 尚未建立正式
  pass evidence；因此本 topic 目前停在 `review-ready`。
- 此 topic 的 correction 僅限 forward-only release path；即使未來 release baseline
  改變，也不得把 workflow 反向改寫成針對 `v0.4.5` 的 retroactive repair。
- release 只在 `merged` 後成立；pre-merge 狀態不得建立 tag、不得宣稱已修正
  已發布的 `v0.4.5`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/model-artifact-release-wording-correction/model-artifact-release-wording-correction.plan.md` | Planning actor | 本 follow-up topic 的 repo-visible execution contract |
| Plan review artifact | `plan/model-artifact-release-wording-correction/model-artifact-release-wording-correction.plan-review.json` | Reviewer | repo-visible planning gate verdict |
| Human check gate artifact | `plan/model-artifact-release-wording-correction/model-artifact-release-wording-correction.human-check.json` | Human | explicit repo-visible gate evidence that clears the approved plan for `implement-plan` |
| Project summary | `README.md` | Implementer | 最小 first-read release-facing wording correction path |
| Package version source | `src/async_model_gateway/__version__.py` | Implementer | package runtime version metadata 的 patch bump source |
| Packaging metadata | `pyproject.toml` | Implementer | package version metadata 的 patch bump source |
| Lockfile metadata | `uv.lock` | Implementer | package version metadata 需要同步時的 bounded lockfile sync path |

Artifact path notes:

- 此 topic 明確不修改 `docs/architecture.md`、`docs/specs/`、
  `src/async_model_gateway/model_artifact/`、`tests/`、或
  `plan/model-artifact-minimal-boundary/` 下的任何既有 artifact。
- repo 沒有 root `VERSION` 檔；請把 `src/async_model_gateway/__version__.py` 與
  `pyproject.toml` 視為此 topic 的 executable version sources。
- listed paths 是 executable contract；若後續工作偏離這些精確 paths，必須停止並回到
  `spec-and-plan-finalization`。
- `README.md`、`src/async_model_gateway/__version__.py`、`pyproject.toml` 與必要時的
  `uv.lock` 是本 topic 唯一 release-only implementation artifacts；不得藉此話題帶入
  其他 docs/source/test 變更。

## Stable library metadata

- `README row`: 修正 `README.md` 中「目前階段」對 `ModelArtifact` 的 release-facing
  描述，使其回到 shared read contract + explicit `LoaderFamily` 的既有 contract；
  不做 broader README sweep。
- `VERSION bump`: `patch bump`；authoring 當下觀察到的 released baseline 是
  `0.4.5`，若沒有 intervening release，預期 next tag 是 `v0.4.6`。若 release
  時 baseline 已前進，則改為當下 latest released baseline 的下一個 patch
  version；不得反向固定或回寫 `v0.4.5`。
- `timing`: `release`。
- `rationale`: 已發布 `v0.4.5` 的 README wording 與既有 contract 不一致，但保守路徑
  已鎖定為 forward-only follow-up；因此此 topic 只承接 wording correction 與必要的
  patch-release metadata，不改寫已發布歷史。
- `release note expectation`: release note 只宣告 `ModelArtifact` release-facing
  wording correction / contract clarification；不得宣告新的 Python behavior、loader
  runtime 或 broader model-side capability。

## Implementation Steps

1. 更新 `README.md`，只在既有 first-read / release-facing summary 內修正
   `ModelArtifact` wording，使其與 shared read contract、explicit
   `LoaderFamily`、以及 deferred `LocalModelLoader` semantics 一致；不得展開成
   broader docs sweep。
2. 在 `src/async_model_gateway/__version__.py` 與 `pyproject.toml` 實作
   patch-release metadata bump，並在 package version metadata 需要同步時更新
   `uv.lock`；不得藉此處理其他 dependency、build-system 或 packaging work。
3. 執行 bounded validation，至少證明 `README.md` wording correction 與 version
   metadata 同步、only-listed artifact paths 被修改、且本 topic 沒有回寫任何
   `v0.4.5` released history 或既有 topic artifacts。
4. 將 pre-merge work 停在 repo-visible merged-ready state；tag 建立、release note
   發佈與 actual release execution 不屬於 `implement-plan`，必須留到 merge 後的
   條件式 `release` workflow。

## Validation / Acceptance Checks

- Canonical topic-plan sections、status names、allowed transitions 與 reviewer
  handoff shape 必須持續符合 repo workflow contracts。
- plan 文首必須保留 analysis layer 缺件 warning，明確說明本 topic 是在
  incomplete-layer mode 下 author。
- Validation 必須證明 `README.md` correction 只限 release-facing wording，並且
  `ModelArtifact` 不再被表述為 `local artifact identity` 或其他 identity authority。
- Validation 必須證明 corrected wording 與既有 contract 對齊：`ModelArtifact`
  是 shared read contract 的一部分，`LoaderFamily` 為 explicit vocabulary，而
  `LocalModelLoader` / artifact I/O / runtime behavior 仍未因本 topic 被宣告為已實作。
- Validation 必須證明 `v0.4.5` 的 tag、release record、merged history 與既有 topic
  artifacts 沒有被 retroactively 改寫。
- Validation 必須證明 version bump 只作用於 `src/async_model_gateway/__version__.py`、
  `pyproject.toml` 與必要時的 `uv.lock`，且 bump direction 維持為下一個 patch
  release。
- Validation 不得要求新增 `step.md`、`spec.md`、source/test/docs implementation、
  release execution evidence，或任何 reviewer / human gate 的預填內容。

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
- release actor 必須從 merged commit 執行 forward-only patch release；若 release
  當下 baseline 仍是 `0.4.5`，預期 tag 是 `v0.4.6`。
- 若在此 topic release 前已有 intervening release，release actor 必須改用當下
  latest released baseline 的下一個 patch tag，但 release contents 仍只限本 topic
  的 wording correction，不得藉此混入新的 contract / behavior change。
- release note 應明確說明這是 `ModelArtifact` release-facing wording correction，
  而不是對 `v0.4.5` 的 retroactive rewrite。

## Open Questions / Unresolved Items

- None.
