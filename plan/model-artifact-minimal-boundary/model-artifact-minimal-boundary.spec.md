# model-artifact-minimal-boundary Specification

## Acceptance Criteria

1. `async_model_gateway.model_artifact` 必須成為此 topic 唯一 public import
   surface，且只 re-export `ModelArtifact` 與 `LoaderFamily`。
2. `src/async_model_gateway/model_artifact/` 必須成為此 topic 唯一 source root，
   `tests/model_artifact/` 必須成為此 topic 唯一 tests lane。
3. `LoaderFamily` 必須是 bounded enum，starter vocabulary 只允許
   `pickle`、`torch`、`onnx`。
4. `ModelArtifact` 必須只承載 `loader_family`、`artifact_path` 與
   `loader_options`。
5. `ModelArtifact` 不得接受 `model-payload` identity material，也不得把
   `loader_family` 改寫成推論結果。
6. Source layout 必須維持一檔一概念，且本 topic 不得新增任何
   `LocalModelLoader` source / test surface。
7. repo-visible docs 必須一致表達 `model_artifact` 是 shared read contract、
   不是 identity material，且 `LocalModelLoader` 仍是 docs-level deferred
   boundary。
8. release-facing metadata files 不得出現在 `implement-plan` steps；它們只保留在
   stable-library metadata 與 merge 後 `release` workflow。

## Behavioral Scenarios

### Scenario 1: Explicit enum family and minimal artifact metadata form a valid shared read contract

- **Given**: producer 顯式提供一個合法的 `LoaderFamily.pickle`
- **And**: producer 提供 non-empty `artifact_path`
- **And**: `loader_options` 只包含 JSON-like read-time metadata
- **When**: 建立 `ModelArtifact`
- **Then**: `ModelArtifact` 會保留原始 explicit `LoaderFamily`
- **And**: contract 只承載 `loader_family`、`artifact_path` 與 `loader_options`
- **And**: 這個 contract 不會要求 `model-payload`、`payload-hash` 或其他
  identity material

### Scenario 2: Invalid explicit values fail closed before any loader behavior is inferred

- **Given**: producer 提供未知 family 值、blank `artifact_path`、或非法
  `loader_options` value
- **When**: 建立 `LoaderFamily` 或 `ModelArtifact`
- **Then**: constructor 會以 `ValueError` 或 `TypeError` fail closed
- **And**: implementation 不會根據副檔名、path fragment、artifact content、
  pickle shape 或其他 heuristics 自行補值

### Scenario 3: Package surface stays narrow and leaves LocalModelLoader deferred

- **Given**: caller 匯入 `async_model_gateway.model_artifact`
- **When**: 檢查 package surface
- **Then**: caller 只能取得 `ModelArtifact` 與 `LoaderFamily`
- **And**: package surface 不會暴露 `LocalModelLoader`
- **And**: root package、`model_registry` 與 `response_cache` 既有 public
  surface 不會被改寫成 re-export owner

### Scenario 4: Source and tests lanes stay fixed to the locked human decision

- **Given**: implementer 依 topic plan 執行 `implement-plan`
- **When**: 檢查新增 source 與 tests paths
- **Then**: source 只允許落在 `src/async_model_gateway/model_artifact/`
- **And**: tests 只允許落在 `tests/model_artifact/`
- **And**: implementation 不得改走 `model_pool` 或 `tests/model_pool` lane

### Scenario 5: Release-facing metadata remains post-merge only

- **Given**: topic 進入 stable-library / release-facing workflow
- **When**: implementer 與 release actor 檢查 topic plan contract
- **Then**: release-facing metadata files 不會出現在 `implement-plan` steps
- **And**: 這些 paths 只在 stable-library metadata 與 merge 後 `release`
  workflow 被引用
- **And**: tag 與 release notes 仍保留給 merge 後的 `release` workflow

## Error / Edge Cases

- family value 若不在 bounded enum vocabulary `pickle|torch|onnx` 內，必須直接失敗。
- `artifact_path` 若為空字串，必須直接失敗；不得改以 current working
  directory、預設副檔名或 fallback path 推測 artifact。
- `loader_options` 若包含非 JSON-like nested value，必須直接失敗。
- 此 topic 不得把 `loader_options` 內容拿去做 `payload-hash`
  canonicalization；shared read contract 與 identity authority 仍維持分離。
- 即使 `artifact_path` 看起來像熟悉格式，本 topic 仍不得因為 path 內容而省略
  explicit `LoaderFamily`。
- `LocalModelLoader`、artifact existence probing、resource lifecycle、timeout、
  cancellation、retry 與 backend-specific behavior 都屬於其他 topic 的邊界。
