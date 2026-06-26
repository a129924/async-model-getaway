> Semantic warning: 在 authoring 當下找不到
> `analysis/model-execution-boundary/requirements.md` 與
> `analysis/model-execution-boundary/technical-spec.md`。此 plan
> 依據 repo exploration、workflow contract，以及已鎖定的 topic 決策撰寫；
> analysis layer 目前屬缺件狀態，但不重開 scope。

# model-execution-boundary

## Goal / Outcome

- 以 repo-visible planning artifacts 凍結 model-side 文件修正 contract，將
  `ModelExecution` 正式建立為 `ModelPool` / `ModelGateway` 的 sibling
  boundary，並把現有 architecture/spec wording 收斂到一致的責任切分。
- 當此 topic 完成時，`docs/architecture.md`、
  `docs/specs/model-side-boundary.md`、
  `docs/specs/orchestrator-boundary.md` 與
  `docs/specs/core-abstractions-boundary.md` 會一致表達：
  `ModelPool` 是 local runtime-model provider / lifecycle owner，
  `ModelGateway` 是 remote runtime-model provider / access boundary，
  `runtime-model` 是 unified consumption surface，
  `ModelExecution` 是 invocation semantics owner，而 `orchestrator`
  只負責協調，不直接 execute model。

## Scope

- **In scope**:
  - 在 `plan/model-execution-boundary/` 下建立本 topic 的 repo-visible
    planning artifacts。
  - 規劃後續對 `docs/architecture.md`、
    `docs/specs/model-side-boundary.md`、
    `docs/specs/orchestrator-boundary.md`、
    `docs/specs/core-abstractions-boundary.md` 的 bounded wording correction。
  - 僅在 cross-reference 或 deferred wording 無法保持一致時，才允許最小幅度
    觸及 `docs/specs/canonical-input-boundary.md`。

- **Out of scope**:
  - 任何 Python implementation、module/package layout、具體 class /
    protocol / signature 設計。
  - 任何 provider-specific execution contract、request/response schema、
    public method naming，或把 `features` 升格為 execution contract。
  - 任何把 `model-payload` 改寫成 inference payload 的文件或設計變更。
  - 任何重新打開 response cache、registry、freshness、artifact loading、
    local loader、release 或 stable-library metadata 的 topic。
  - 任何 review artifact authoring、commit、push、plan review、planner
    final gate、`human check` 或 `human merge`。

## Locked Decisions

- 正式名稱固定為 `ModelExecution`。
- `ModelExecution` 是 `ModelPool` / `ModelGateway` 的 sibling boundary，
  不是 child boundary。
- `ModelPool` / `ModelGateway` 只擁有 runtime-model provider /
  acquisition-access boundary，不擁有 execution policy 或 invocation
  semantics。
- `runtime-model` 是 unified consumption surface，不是 system-level
  execution owner。
- `orchestrator` 只做 coordinator，不直接 execute model。
- `canonical input boundary` 保持不變；`features` 不是 execution
  contract；`model-payload` 不是 inference payload。
- `docs/specs/canonical-input-boundary.md` 僅能做必要的 cross-reference
  或 deferred wording 對齊；若無必要則保持不變。
- 此 topic 是 docs-only correction topic，不是 stable-library topic，也不宣告
  release-facing timing；`## Stable library metadata` 依 contract 明確省略。
- 此 topic 以 plan/spec/step companion artifacts 凍結文件修正 contract；不得
  因為 companion artifacts 存在而推進任何 reviewer、human gate 或 publish
  狀態。

## Boundaries / Exclusions

- Planning actor 只負責本 topic 的 planning artifacts authoring。
- Implementer 之後只能修改 `## Artifact Paths` 明確列出的文件；若修正範圍超出
  這些 paths，必須回到 `spec-and-plan-finalization`。
- Reviewer 之後只負責獨立 verdict 與 blocking issue 記錄；reviewer 不實作、
  不代寫 creator steps，也不關閉 human gates。
- Main Agent / Human routing、`human check`、`human merge` 與 PR / release
  流程不屬於本次 plan authoring。
- 任何把 topic 擴張成 execution API 設計、provider taxonomy、schema
  formalization、cache/registry ownership 重分配的工作，都屬於不同 topic。

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow
  `spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix`；
  此 topic 不使用條件式 `release` workflow，於 `merged` 停止。
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

- 目前只完成 plan/spec/step authoring；不得把這次 authoring 視為 plan review、
  `approved`、`human check` 或 `implement-plan` 入口。
- `approved` 仍需後續 repo-visible `plan-review.json` verdict 與明確的
  repo-visible `human check`；兩者目前都尚未發生。
- analysis layer 缺少 `requirements.md` 與 `technical-spec.md`，已以上方
  semantic warning 明示；此 topic 仍以已鎖定的 human decisions 與 repo-visible
  docs boundary 為唯一 scope 來源，不得在 reviewer 或 implementer 階段自行重開
  analysis scope。
- 若後續有人提議新增 Python surface、provider-specific execution contract、
  request/response schema 或重寫 canonical input semantics，必須回到
  `spec-and-plan-finalization`。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/model-execution-boundary/model-execution-boundary.plan.md` | Planning actor | 本 topic 的 repo-visible execution contract |
| Topic step tracking | `plan/model-execution-boundary/model-execution-boundary.step.md` | Implementer | repo-visible implementation progress / gate-tracking companion artifact |
| Topic wording spec | `plan/model-execution-boundary/model-execution-boundary.spec.md` | Planning actor | 凍結 cross-doc wording 與 acceptance contract 的 companion artifact |
| Plan review artifact | `plan/model-execution-boundary/model-execution-boundary.plan-review.json` | Reviewer | repo-visible planning gate verdict |
| Architecture summary | `docs/architecture.md` | Implementer | 對齊高層 responsibility summary、runtime-model surface 與 orchestrator / execution 分界 |
| Core abstractions boundary spec | `docs/specs/core-abstractions-boundary.md` | Implementer | 對齊共享詞彙、閱讀順序與依賴方向摘要，使 `ModelExecution` 成為正式 sibling boundary |
| Model side boundary spec | `docs/specs/model-side-boundary.md` | Implementer | 對齊 `ModelExecution`、`ModelPool`、`ModelGateway` 與 `runtime-model` 的正式責任切分 |
| Orchestrator boundary spec | `docs/specs/orchestrator-boundary.md` | Implementer | 對齊 orchestrator 僅負責 coordination、不直接 execute model 的 wording |
| Canonical input boundary spec | `docs/specs/canonical-input-boundary.md` | Implementer | 僅在必要時做最小 cross-reference / deferred wording 對齊，避免誤導為 execution-contract rewrite |

Artifact path notes:

- 本 topic 不修改 `README.md`、`VERSION`、`docs/settings-policy.md`、其他既有
  `plan/` artifacts、任何 source/tests path，或任何 review artifact 以外的 gate
  artifact。
- `docs/specs/canonical-input-boundary.md` 是 conditional path：只有在不修改它就
  會導致 cross-doc wording 衝突時才可編輯；若能維持一致則保持不變。
- 上述 paths 是可執行合約；若後續修正需要超出這些精確 paths，必須停止並返回
  `spec-and-plan-finalization`。

## Implementation Steps

1. 更新 `docs/architecture.md`，將高層責任摘要改寫為 provider boundary 與
   invocation boundary 分離：`ModelPool` 僅負責 local runtime-model provider /
   lifecycle、`ModelGateway` 僅負責 remote runtime-model provider / access、
   `ModelExecution` 擁有 invocation semantics，而 `orchestrator`
   保持為 coordinator。
2. 更新 `docs/specs/model-side-boundary.md`，把 model side 的正式共享詞彙從
   目前三個業務名詞擴張為包含 `ModelExecution` 的 sibling boundary set，同時
   明確收斂 `ModelPool` / `ModelGateway` 不擁有 execution policy，並維持
   `runtime-model` 只作統一 consumption surface。
3. 更新 `docs/specs/orchestrator-boundary.md` 與
   `docs/specs/core-abstractions-boundary.md`，讓依賴方向、共享詞彙與 owner
   responsibility 一致表達 orchestrator 依賴 `ModelExecution` 或等價的
   execution boundary 來發生 invocation，而不是自己直接 execute model。
4. 檢查 `docs/specs/canonical-input-boundary.md` 是否存在把 `features`
   暗示成 execution contract、或把 `model-payload` 暗示成 inference
   payload 的 wording；只有在 cross-doc 對齊確實需要時，才做最小幅度的
   cross-reference / deferred wording 修正。
5. 完成上述文件修正後，執行 bounded consistency pass，確認所有列入本 topic
   的文件都一致維持：`ModelExecution` 為 sibling boundary、
   `runtime-model` 為 consumption surface、`orchestrator` 不直接 execute
   model、`features` 不是 execution contract、`model-payload`
   不是 inference payload，然後再更新
   `plan/model-execution-boundary/model-execution-boundary.step.md`。

## Validation / Acceptance Checks

- Topic plan sections、status names、allowed transitions 與 reviewer handoff
  shape 必須持續符合 `plan/topic-plan-contract.md` 與
  `plan/agent-handoff-workflow.md`。
- `plan/model-execution-boundary/model-execution-boundary.step.md` 必須鏡像每個
  編號的 implementation step，且目前只能標記 `plan-authoring` 完成；不得預填
  plan review、`human check`、implementation 或 merge 相關完成狀態。
- `plan/model-execution-boundary/model-execution-boundary.spec.md` 必須存在，並把
  cross-doc wording contract 凍結為 reviewer 與 implementer 可檢查的 acceptance
  criteria。
- `docs/architecture.md`、`docs/specs/model-side-boundary.md`、
  `docs/specs/orchestrator-boundary.md` 與
  `docs/specs/core-abstractions-boundary.md` 完成後，必須一致出現
  `ModelExecution` sibling boundary 與 orchestrator coordinator-only framing。
- `ModelPool` 完成後必須只被描述為 local runtime-model provider / lifecycle
  owner；`ModelGateway` 完成後必須只被描述為 remote runtime-model provider /
  access boundary；兩者都不得再被寫成 execution policy owner。
- `runtime-model` 完成後必須仍被描述為 unified consumption surface，而不是
  system-level execution owner。
- `features` 不得被升格為 execution contract；`model-payload` 不得被改寫成
  inference payload；`canonical input boundary` 不得被重開成新的 topic。
- 本 topic 的 implementation evidence 不得聲稱任何 Python implementation、
  concrete class / protocol / signature、provider-specific execution contract、
  request/response schema 或 release/stable-library 變更已完成。

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
- Merge 後即停止；不得在此 topic 下新增 `VERSION`、release notes、tag 或
  README promotion work。

## Open Questions / Unresolved Items

- None.
