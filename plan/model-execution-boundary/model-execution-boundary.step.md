---
topic: model-execution-boundary
phase: plan-authoring
created: 2026-06-26
---

# model-execution-boundary — Step Tracking

> **Executor**: 完成後將每個步驟標記為 `[X]`。
> 在此 topic 進入 reviewer 或 implementation 之前，不得預填任何 gate 已通過。
> 請在 `plan/model-execution-boundary/model-execution-boundary.step.md` 更新此檔。

## Workflow Stages

- [X] plan-authoring
- [ ] plan-review
- [ ] implementation
- [ ] validation

## Gate Status

- Reviewer verdict: pending
- Human check: pending
- Current workflow position: `spec-and-plan-finalization`；topic 目前停在
  `review-ready`，尚未進入 `reviewer-in-progress`
- Analysis layer: 缺少
  `analysis/model-execution-boundary/requirements.md` 與
  `analysis/model-execution-boundary/technical-spec.md`

## Implementation Steps

- [ ] 1. 更新 `docs/architecture.md`，將高層責任摘要改寫為 provider boundary 與 invocation boundary 分離：`ModelPool` 僅負責 local runtime-model provider / lifecycle、`ModelGateway` 僅負責 remote runtime-model provider / access、`ModelExecution` 擁有 invocation semantics，而 `orchestrator` 保持為 coordinator。
- [ ] 2. 更新 `docs/specs/model-side-boundary.md`，把 model side 的正式共享詞彙擴張為包含 `ModelExecution` 的 sibling boundary set，同時明確收斂 `ModelPool` / `ModelGateway` 不擁有 execution policy，並維持 `runtime-model` 只作統一 consumption surface。
- [ ] 3. 更新 `docs/specs/orchestrator-boundary.md` 與 `docs/specs/core-abstractions-boundary.md`，讓依賴方向、共享詞彙與 owner responsibility 一致表達 orchestrator 依賴 execution boundary，而不是自己直接 execute model。
- [ ] 4. 檢查 `docs/specs/canonical-input-boundary.md` 是否存在把 `features` 暗示成 execution contract、或把 `model-payload` 暗示成 inference payload 的 wording；只有在 cross-doc 對齊確實需要時，才做最小幅度的 cross-reference / deferred wording 修正。
- [ ] 5. 完成上述文件修正後，執行 bounded consistency pass，確認所有列入本 topic 的文件都一致維持：`ModelExecution` 為 sibling boundary、`runtime-model` 為 consumption surface、`orchestrator` 不直接 execute model、`features` 不是 execution contract、`model-payload` 不是 inference payload，然後再更新 `plan/model-execution-boundary/model-execution-boundary.step.md`。
