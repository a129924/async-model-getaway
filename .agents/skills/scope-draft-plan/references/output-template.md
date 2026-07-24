# Draft Plan output template

Translate headings and prose into the requested language. When no language is
specified, use Traditional Chinese. Produce exactly one recommended Mission;
do not turn the sections into an implementation plan.

```md
# Draft Plan：`<Mission 名稱>`

## 1. 判定摘要

- **建議模式**：BC Mission
- **Primary BC**：
- **核心結果**：
- **Scope 信心**：高／中／低
- **是否可進入 Implementation Plan**：是／否
- **需要 Human Decision**：無／列出必要決策

## 2. 原始需求摘要

用一至三句話重述需求，不把未確認的解法當成需求。

## 3. 核心問題

說明 actor 遇到的問題、需要的可觀察結果，以及不處理的阻礙。

## 4. 假設

只列會影響 scope 或驗收的假設；沒有時寫「無重大假設」。

## 5. 建議 Mission

### Mission Statement

以一句話描述完整、可驗收的 capability。

### 為什麼切在這裡

說明為何它不是技術 task、為何相關獨立能力不納入，以及為何適合一次完整 SDD。

## 6. In Scope

列出完成 Mission 必要的業務行為與能力，不列檔案、class 或實作步驟。

## 7. Out of Scope

列出刻意不處理的角色、例外、生命週期階段與跨 BC 工作；每項應是明確排除或合理的後續 capability。

## 8. 端到端行為

- **主要成功情境**：Given／When／Then。
- **核心失敗情境**：Given／When／Then。
- **可觀察結果**：資料、狀態或對 actor 可見的結果。

## 9. Acceptance Criteria

列出可測試、可觀察且不綁定實作方式的完成條件。

## 10. 影響邊界

### Domain

- Aggregate／Entity／Value Object：
- 受影響的 Invariants：
- 新增或改變的 Domain Behavior：

### Contracts

- Public API：
- Events／Messages：
- Cross-BC Contracts：
- Backward Compatibility：

### Data

- 主要資料：
- Ownership：
- Migration：
- Rollback：

不適用時寫「不適用」。

## 11. Technical Task Map

以高階項目列出必要的 Domain／Application behavior、persistence、data、delivery adapter、verification、以及必要的 observability 或 rollback evidence。

> 上述項目是同一個 Mission 內的 Technical Tasks，不是獨立 SDD 專案，也不代表必須由不同 Agent 並行執行。

## 12. 風險與 Gate

僅列需要特別處理的 domain invariant、public contract、data migration、authorization、cross-BC ownership、不可逆 side effect 或 scope expansion；對每項列出風險、處理方式與是否需要 Human Gate。

## 13. Verification Strategy

說明所需證據方向，例如 domain、contract、integration 或 end-to-end tests，migration／rollback verification，manual scenario，或 logs／metrics；不寫完整測試實作。

## 14. Follow-up Missions

列出刻意排除的後續 business capabilities，不列單一技術層。

## 15. Implementation Plan Handoff

- Implementation Plan 必須維持本 Mission 邊界。
- Domain、Repository、Database、DTO／API 與 Tests 是同一 Mission 的 tasks，不得各自重開 SDD。
- 可拆 milestones 與小 commits；只有 domain、contract、data、security、cross-BC 或重大 scope 偏離需要 Human Gate。
- 若無法在既定邊界完成，先回報 Scope Gap，不得默默擴大範圍。
```
