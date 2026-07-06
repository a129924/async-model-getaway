> Semantic warning: 在 authoring 當下找不到
> `analysis/response-cache-operational-minimal-boundary-release/requirements.md` 與
> `analysis/response-cache-operational-minimal-boundary-release/technical-spec.md`。
> 此 plan 依據已 merge 的
> `response-cache-operational-minimal-boundary` repo-visible contract、目前
> `README.md` 與 package version baseline、以及明確 human 授權撰寫；analysis
> layer 目前缺件，不可視為已補齊。

# response-cache-operational-minimal-boundary-release

## Goal / Outcome

- 以獨立 repo-visible planning slice 承接已 merge 的
  `response-cache-operational-minimal-boundary` release-facing work，將
  version bump、`README.md` first-read wording、tag/release timing 與必要
  stable-library metadata 鎖成可執行合約。
- 當此 topic 完成時，既有 merged topic 的 non-release contract 會維持原樣，而
  release-facing actor 只需依本 plan 修改最小必要 metadata/files 並在 merge 後執行
  條件式 `release` workflow。

## Scope

- **In scope**:
  - `plan/response-cache-operational-minimal-boundary-release/response-cache-operational-minimal-boundary-release.plan.md`
    的 release-facing contract authoring。
  - `README.md` 中 package version baseline 與 first-read summary 的最小必要 release-facing wording 更新規劃。
  - `src/async_model_gateway/__version__.py`、`pyproject.toml` 與必要時 `uv.lock` 的 version bump 規劃。
  - merge 後 tag / release timing 的 repo-visible contract。
  - stable-library metadata 宣告，明確說明 README / version / release timing 的 owner 與理由。

- **Out of scope**:
  - 任何重新打開 `ResponseCache` architecture、API、owner boundary、async policy 或 store exposure 決策。
  - 任何修改既有 `response-cache-operational-minimal-boundary` analysis、plan、spec、step 或 review artifacts。
  - 任何 source/test/docs 變更超出 `README.md`、`src/async_model_gateway/__version__.py`、`pyproject.toml` 與必要 lockfile sync。
  - 任何 tag 建立、release 發佈、merge、push、version 檔案實改或 release execution。

## Locked Decisions

- analysis-layer routing 採 incomplete-layer mode：此 topic 沒有
  `analysis/response-cache-operational-minimal-boundary-release/requirements.md`
  或 `technical-spec.md`，且本次是依 human 明確授權在缺件情況下完成 plan。
- 已 merge 的 `response-cache-operational-minimal-boundary` 仍是
  `ResponseCache` non-release contract 的唯一 authority；本 topic 只承接
  release-facing metadata、timing 與 wording，不回寫也不覆寫既有 boundary 決策。
- 此 topic 是 stable-library / release-facing topic，因此必須包含
  `## Stable library metadata`，並啟用條件式 `release` workflow。
- repo 目前沒有 root `VERSION` 檔；此 topic 的 executable version sources
  固定為 `src/async_model_gateway/__version__.py` 與 `pyproject.toml`，若 lockfile
  因 package version 變動需要同步，則 `uv.lock` 也在 scope 內。
- release 版本策略固定為 `patch bump`；authoring 當下觀察到的 baseline 是
  `0.4.3`，因此若沒有其他先行 release，此 topic 對應的下一個 release tag
  會是 `v0.4.4`。
- `README.md` 只允許最小必要 release-facing wording 更新：它必須反映最小
  operational `ResponseCache` boundary 已落地，但不得藉此擴張成 broader docs
  sweep 或重新詮釋 architecture。
- tag 與 release timing 固定為 `merged` 之後的條件式 `release` workflow；
  不得在 feature branch、`publish-in-progress` 或 `pr-open` 狀態預先建立 tag。

## Boundaries / Exclusions

- Planning actor 只負責 author 本 release slice 的 topic plan；不實作 version bump、
  `README.md` wording、tag 或 release。
- Implementer 之後只能修改 `## Artifact Paths` 列出的精確 release-facing paths；
  若發現需要 source/test/docs 邊界外變更，必須回到 `spec-and-plan-finalization`。
- Reviewer 只負責獨立 plan verdict；reviewer 不代替 creator 執行 version bump、
  也不代替 human 或 release actor 關閉 gate。
- Human gate 仍需在 plan review 通過後獨立明示；本 plan 只宣告未來 gate path，
  不建立、不預填 human check artifact。
- 此 topic 不得把既有 merged topic 的 implementation scope、public contract、
  analysis-layer baseline 或 validation claims retroactively 改寫成 release topic。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow
  `spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix -> release`；
  由於本 topic 明確宣告 release-facing timing，因此 `release` workflow 條件成立。
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

- `approved` 依 repo contract 必須同時具備
  `plan/response-cache-operational-minimal-boundary-release/response-cache-operational-minimal-boundary-release.plan-review.json`
  的 `approved` verdict 與獨立 human check gate pass。
- 此 topic 只規劃 release-facing file edits 與 merge 後 release timing；若後續實作想觸碰
  response-cache source/tests/docs boundary，必須停止並回到
  `spec-and-plan-finalization`。
- 既有 merged topic 已在 `merged` 狀態停止，因其 contract 明確宣告
  `No release workflow required`；本 topic 是獨立承接 release workflow 的唯一入口。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/response-cache-operational-minimal-boundary-release/response-cache-operational-minimal-boundary-release.plan.md` | Planning actor | 本 release slice 的 repo-visible execution contract |
| Plan review artifact | `plan/response-cache-operational-minimal-boundary-release/response-cache-operational-minimal-boundary-release.plan-review.json` | Reviewer | repo-visible planning gate verdict |
| Human check gate artifact | `plan/response-cache-operational-minimal-boundary-release/response-cache-operational-minimal-boundary-release.human-check.json` | Human | explicit repo-visible gate that clears the approved release-facing plan for `implement-plan` |
| Project summary | `README.md` | Implementer | 最小 first-read release-facing wording 更新，反映 operational response-cache boundary 已落地 |
| Package version source | `src/async_model_gateway/__version__.py` | Implementer | package runtime version metadata 的 patch bump source |
| Packaging metadata | `pyproject.toml` | Implementer | package version metadata 的 patch bump source |
| Lockfile metadata | `uv.lock` | Implementer | 當 package version bump 導致 lock metadata 需同步時的 bounded sync path |

Artifact path notes:

- repo 沒有 root `VERSION` 檔；請把 `src/async_model_gateway/__version__.py` 與
  `pyproject.toml` 視為此 topic 的 executable version sources。
- 此 topic 不修改 `response_cache` source/test/docs paths，也不修改
  `plan/response-cache-operational-minimal-boundary/` 下的任何既有 artifact。
- listed paths 是 executable contract；若後續工作偏離這些精確 paths，必須停止並回到
  `spec-and-plan-finalization`。
- 本輪 plan authoring 只宣告 future reviewer / human gate paths，不建立對應 artifact。

## Stable library metadata

- `README row`: 更新 `README.md` 的「目前階段」版本 baseline 敘述與最小已落地 boundary 摘要，補上 minimal operational `ResponseCache` availability；不做 full README sweep。
- `VERSION bump`: `patch bump`；以 authoring 當下觀察到的 `0.4.3` 為 baseline，預期 next patch release 為 `0.4.4`。
- `timing`: `release`。
- `rationale`: 既有 merged topic 新增了 repo-visible public boundary，但原 topic 明確排除 stable-library / release work；因此必須以獨立 release slice 承接 README、version metadata 與 tag timing，避免 retroactively 改寫原 topic contract。
- `release note expectation`: release workflow 應記錄最小 operational `ResponseCache` boundary 已納入 package baseline，且此次 release 不代表 backend、TTL、orchestrator 或 broader cache architecture 已實作完成。

## Implementation Steps

1. 更新 `README.md`，只在既有 first-read 摘要內補上最小 operational `ResponseCache` boundary 已落地與對應 version baseline；不得展開成 broader architecture rewrite。
2. 在 `src/async_model_gateway/__version__.py` 與 `pyproject.toml` 實作 `patch bump`，並在 package version metadata 需要同步時更新 `uv.lock`；不得擴張成其他 packaging 或 dependency work。
3. 執行 release-facing bounded validation，至少驗證 `README.md` wording 與 version metadata 同步，且 lockfile metadata 沒有留下 version drift。
4. 將實作停在 repo-visible merged-ready state；tag 建立與 release 發佈不屬於 `implement-plan`，必須留到 merge 後的條件式 `release` workflow。

## Validation / Acceptance Checks

- Canonical topic-plan sections、status names、allowed transitions 與 reviewer handoff shape 必須持續符合 repo workflow contracts。
- plan 文首必須保留 analysis layer 缺件 warning，明確說明本 topic 是在 human 授權下以 incomplete-layer mode author。
- Validation 必須證明既有 `response-cache-operational-minimal-boundary` contract 仍維持 non-release authority，本 topic 沒有重開 architecture / API / boundary decision。
- Validation 必須證明 `README.md` 更新只限 first-read release-facing wording，不擴張成 broader docs sweep。
- Validation 必須證明 version bump 只作用於 `src/async_model_gateway/__version__.py`、`pyproject.toml` 與必要的 `uv.lock` sync，且 bump direction 維持 `patch bump`。
- Validation 必須證明 release timing 只在 `merged` 之後執行，且 tag 來源是 merged commit，而不是 feature branch 或 pre-merge state。
- Validation 不得要求新增 `ResponseCache` source/test changes、plan companion artifacts、review verdict 預填、human check 預填或 release execution evidence。

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

- 此 topic merge 後需要進入條件式 `release` workflow。
- release actor 必須從 merged commit 建立與 patch bump 對應的 tag；若此 topic 仍對應 authoring 時觀察到的 baseline，預期 tag 是 `v0.4.4`。
- release actor 應在 tag 建立後發佈對應 release，並在 release note 中只宣告 minimal operational `ResponseCache` boundary 已納入 package baseline；不得藉 release note 擴張成未實作功能承諾。

## Open Questions / Unresolved Items

- None.
