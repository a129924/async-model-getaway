# model-execution-boundary Specification

## Acceptance Criteria

1. `docs/architecture.md` 必須把 `ModelExecution` 正式描述為
   `ModelPool` / `ModelGateway` 的 sibling boundary，而不是任一 provider
   boundary 的 child 或內部細節。
2. `docs/specs/model-side-boundary.md` 必須明確收斂：
   `ModelPool` 是 local runtime-model provider / lifecycle owner，
   `ModelGateway` 是 remote runtime-model provider / access boundary，
   `ModelExecution` 是 invocation semantics owner，而 `runtime-model`
   只是 unified consumption surface。
3. `docs/specs/orchestrator-boundary.md` 必須明確表達 `orchestrator`
   只做 coordination，不直接 execute model，也不擁有 execution policy。
4. `docs/specs/core-abstractions-boundary.md` 必須把共享詞彙、閱讀順序與依賴方向
   對齊到新的 sibling boundary 切分，避免繼續把 provider acquisition 與
   invocation semantics 混為同一責任。
5. `docs/specs/canonical-input-boundary.md` 只有在 cross-doc consistency
   確實需要時才可修改；即使修改，也不得把 `features` 重寫成 execution
   contract，或把 `model-payload` 重寫成 inference payload。
6. 本 topic 不得引入任何 Python class / protocol / signature、
   provider-specific execution contract、request/response schema、
   public method naming，或 cache/registry/freshness/artifact loading
   responsibility re-open。

## Behavioral Scenarios

### Scenario 1: Architecture summary separates provider and execution ownership

- **Given**: 讀者先讀 `docs/architecture.md`
- **When**: 讀者查看 model-side 與 orchestrator 的高層責任摘要
- **Then**: 讀者會看到 `ModelPool` / `ModelGateway` 負責 provider /
  access 邊界
- **And**: 讀者會看到 `ModelExecution` 負責 invocation semantics
- **And**: 讀者不會再被文字引導成 `orchestrator` 直接 execute model

### Scenario 2: Model-side spec narrows provider boundaries without promoting runtime-model

- **Given**: 讀者查看 `docs/specs/model-side-boundary.md`
- **When**: 讀者檢查 `ModelPool`、`ModelGateway`、`ModelExecution` 與
  `runtime-model` 的責任說明
- **Then**: `ModelPool` 只承擔 local runtime-model provider / lifecycle
- **And**: `ModelGateway` 只承擔 remote runtime-model provider / access
- **And**: `runtime-model` 仍是 unified consumption surface
- **And**: `runtime-model` 不會被升格成 system-level execution owner

### Scenario 3: Orchestrator spec remains coordinator-only

- **Given**: 讀者查看 `docs/specs/orchestrator-boundary.md`
- **When**: 讀者檢查 owner responsibility、依賴 authority 與 exclusion
- **Then**: 文件必須明確表達 `orchestrator` 依賴 model-side execution
  boundary 來完成 invocation
- **And**: 文件不得再宣稱 `orchestrator` 自己擁有 execute-model 責任

### Scenario 4: Canonical input semantics remain unchanged

- **Given**: topic 需要 cross-doc wording alignment
- **When**: `docs/specs/canonical-input-boundary.md` 被檢查或必要時被最小修正
- **Then**: `features` 仍是 bounded capability / usage-mode vocabulary
- **And**: `model-payload` 仍是 model identity material
- **And**: 文件不得把兩者重新定義成 execution contract 或 inference payload

## Error / Edge Cases

- 若任一文件仍把 `ModelExecution` 寫成 `ModelPool` 或 `ModelGateway`
  的 child / internal concern，則視為 cross-doc contract 未完成。
- 若任一文件把 `runtime-model` 寫成 system-level execution owner，則視為責任切分
  倒退。
- 若 `orchestrator` wording 仍保留 direct execute model 的語意，則不得視為 topic
  完成。
- 若 `docs/specs/canonical-input-boundary.md` 可以不改就保持一致，則不得為了追求
  對稱而擴大修改範圍。
- 若修正需要新的 provider-specific execution vocabulary、schema 或 method
  naming，表示 topic scope 已漂移，必須回到 planning 而不是在本 topic 內補寫。
