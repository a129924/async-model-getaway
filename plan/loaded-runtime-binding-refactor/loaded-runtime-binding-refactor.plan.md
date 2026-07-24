> Semantic warning — analysis layer INCOMPLETE：`analysis/loaded-runtime-binding-refactor/requirements.md` 與 `analysis/loaded-runtime-binding-refactor/technical-spec.md` 均不存在。本計畫只依已鎖定 human decisions 與 repository baseline 撰寫；不得藉此擴張 scope 或重開 contract。

# loaded-runtime-binding-refactor

## Goal / Outcome

### Goal

將 local ONNX runtime 的 internal component boundary 重構為 `LoadedRuntimeModel`、`ModelLoader`、`ModelExecutor`、`RuntimeBinding`、`ModelPool` 與唯一 `_LocalRuntimeComposition`。

這不是 public feature：不存在 external/public composition entrypoint 或已接入 caller。驗收是 internal component-level sequence：

```python
binding = self._binding_resolver.resolve(artifact.loader_family)
loaded_model = await self._model_pool.acquire(
    artifact,
    loader=binding.loader,
    max_concurrency=binding.max_concurrency,
)
return await binding.executor.execute(loaded_model, invocation)
```

同一 binding 從 resolve 持續至 execute 返回或拋出例外。

## Scope

### In-Scope

- ONNX-only internal resolver、composition、injected loader/pool acquisition、concrete loaded resource、executor gate lifecycle，以及 private `_OnnxRuntime` Protocol。
- `model_pool/loaders/` private loader package；`ModelLoader` 與 `_OnnxModelLoader` 分檔；production ONNX runtime/loader/executor/binding precise generic pairing，並只在 outer resolver 做 object erasure。
- 移除 abstract/opaque `LoadedRuntimeModel`、`loader_family`、`_provider_runtime()`、`_LocalLoadedRuntimeModel`、public `ModelExecution`，以及 `model_pool` package export。
- `Semaphore(1)`、aware-UTC timestamps、普通例外與 `CancelledError` 原樣傳播。
- binding continuity、resolver ordering、executor import AST boundary、strict Pyright pairing、fresh RED evidence。
- 刪除三個失效 live legacy `tests/typecheck` fixtures；保留四個 historical Pyright configs 為 read-only/non-executed evidence。
- human merge 後的 0.7.0 release docs/version/lockfile 與 lightweight `v0.7.0` tag。

### Out-Out-Scope

- cache/key/pool hit/reuse/dedup/eviction/close/unload。
- public composition/pool/loader/executor/loaded-model API 或 orchestrator wiring。
- 真實 ONNX inference/result schema、provider adapter、timeout/retry。
- PICKLE/TORCH loading/execution、remote `ModelGateway`、response cache。
- `ModelArtifact`/`LoaderFamily` schema、canonical-input/orchestrator documents。
- 修改或執行 historical Pyright configs、GitHub Release、PyPI/TestPyPI publication。

### Non-Goal

- 不建立 public caller 來使用 `_create_local_runtime_composition()`。
- 不建立 loader/executor registry 或根據 runtime/type/metadata late dispatch。
- 不為移除的 package exports 提供 compatibility adapter。
- 不將 release 工作列入 pre-merge implementation steps。

## Locked Decisions

- D1 verdict: `non-trivial`; async planning is triggered。
- `runtime_model/_onnx_runtime.py` 定義 private `_OnnxRuntime` Protocol；唯一 required member 是 `get_providers(self) -> list[str]`。`_OnnxModelLoader`、`_OnnxModelExecutor` 與 production ONNX `RuntimeBinding` 必須以相同 `_OnnxRuntime` 作 precise generic pairing；不得在 provider pairing 內部以 `object` 取代該型別。
- `RuntimeBinding[RuntimeT, InvocationT, ResultT]` 是 private frozen slots dataclass，包含 loader、executor、`max_concurrency`。
- 在 `model_pool/loaders/_onnx_model_loader.py`，private lazy importer/session constructor 的 `asyncio.to_thread(InferenceSession, ...)` result 只可在 optional third-party-stub boundary 以明確 `cast(_OnnxRuntime, ...)` 轉為 Protocol；不得有其他 ONNX runtime cast。
- `_RuntimeBindingResolver.resolve(loader_family: LoaderFamily) -> RuntimeBinding[object, object, object]` 是唯一 outer routing/erasure boundary：ONNX 先建立 precise `_OnnxRuntime` pairing，再在 resolver return boundary 以明確 `cast` erase；PICKLE/TORCH raise `NotImplementedError`；不可達 fallback 用 `assert_never(...)`。
- `_LocalRuntimeComposition` 是唯一 production `resolve()` caller。其 exact contract：

  ```python
  class _LocalRuntimeComposition:
      def __init__(
          self,
          *,
          model_pool: ModelPool,
          binding_resolver: _RuntimeBindingResolver,
      ) -> None: ...

      async def execute(
          self,
          artifact: ModelArtifact,
          invocation: object,
      ) -> object: ...
  ```

  它只 resolve 一次，將同一 binding 的 loader/concurrency 傳入 pool，並以同一 binding 的 executor execute；acquire 後不得 re-resolve。
- `_create_local_runtime_composition() -> _LocalRuntimeComposition` 是 module-private，建立 private pool/resolver。不得虛構 public caller；測試以 static private imports 注入 recording resolver/pool/loader/executor doubles。
- `ModelPool` 與 acquire 都是 internal；`model_pool/__init__.py` exports nothing。exact acquire signature：

  ```python
  async def acquire(
      self,
      artifact: ModelArtifact,
      *,
      loader: ModelLoader[RuntimeT],
      max_concurrency: int,
  ) -> LoadedRuntimeModel[RuntimeT]: ...
  ```

  Pool validate artifact、await injected loader、以 `Semaphore(max_concurrency)` 建 wrapper；不得有 resolver/executor/retained loader/model/cache/dispatch state。
- `LoadedRuntimeModel[RuntimeT]` 是 concrete generic slots dataclass，保留 public `runtime`、`execution_gate`、`loaded_at`、`last_used_at`、`mark_used()`。`.runtime` visibility 已獲 human 接受，只供 internal acquire caller；不可有 family/binding/loader/executor/execute/lifecycle/private-handoff member。
- `ModelLoader[RuntimeT]` 位於 private `model_pool/loaders/_model_loader.py`，是 nominal ABC：`async load(self, artifact: ModelArtifact) -> RuntimeT`。private `_OnnxModelLoader` 位於 `model_pool/loaders/_onnx_model_loader.py`，回傳 `_OnnxRuntime` raw session。`ModelExecutor[RuntimeT, InvocationT, ResultT]` 是 nominal ABC；`execute()` acquire gate、mark used、direct-await `_invoke(model.runtime, invocation)`。
- `_OnnxModelExecutor._invoke()` 只在 gate/timestamp lifecycle 後 raise `NotImplementedError`；普通錯誤與 `CancelledError` 不 catch、不 translate。
- Executor source 不得 import resolver/composition、`model_pool`、`model_artifact`；AST test 強制。不得以 runtime type、metadata、`isinstance`、family、registry dispatch。
- UTC helper 是 module-private，產生 aware UTC datetime；`last_used_at` 僅於取得 execution gate 後更新。
- `runtime_model`、`model_execution`、`model_pool` package initializers 均不 re-export implementation types；無 compatibility adapter。
- 刪除三個 invalid live fixtures：`tests/typecheck/onnx_local_runtime_acquisition.py`、`tests/typecheck/model_execution_minimal_consumption.py`、`tests/typecheck/runtime_model_generic_erasure.py`；同時刪除被 loaders package 取代的 `_local_model_loader.py`、`_onnx_runtime_loader.py` 與 `test_local_model_loader.py`。
- 四個 historical Pyright configs 保留、不可修改、不可執行。
- 無 dependency change；既有 ONNX CPU-only loading/options/native-error policy 不變。
- Release 已鎖：verified merge 後更新 declared release paths 至 0.7.0、更新 lockfile，建立/push lightweight `v0.7.0` 指向 release commit。

## Boundaries / Exclusions

- Plan-Creator 只 owner plan/spec/step；Plan-Reviewer 只 owner plan-review JSON。
- Tester owner RED tests/type config/evidence；Implementer owner approved source/deletion changes 與 truthful tracker progress；Reviewer owner independent review artifacts。
- Human owner pre-implementation 與 pre-merge gates。
- 任何 public surface、resolver-owner 移動、真實 ONNX invocation、historical config 修改均屬 plan drift。

## Status / Allowed Transitions

- **Current**: `review-ready`。
- **Execution model**: `spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix -> release`。
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
- 在 `approved -> implement-plan` 前，Human 必須寫入 exact one-key JSON：`{"status":"cleared_for_implementation"}`。
- 在 `pr-open -> merged` 前，Human 必須寫入 exact JSON：`{"status":"cleared_for_merge","pr":"<actual PR identifier>"}`。
- 實際 merge commit 僅由 repo/PR merge evidence 驗證；release tag 指向 post-merge release commit。

## Artifact Paths

### ReadOnly

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Historical Pyright config | `plan/onnx-local-runtime-acquisition-minimal-boundary/pyrightconfig.json` | Historical evidence | Read-only, non-executed historical evidence |
| Historical Pyright config | `plan/model-execution-minimal-consumption-boundary/pyrightconfig.json` | Historical evidence | Read-only, non-executed historical evidence |
| Historical Pyright config | `plan/runtime-model-runtime-generic-erasure/pyrightconfig.json` | Historical evidence | Read-only, non-executed historical evidence |
| Historical Pyright config | `plan/local-runtime-handle-ownership-clarification/pyrightconfig.json` | Historical evidence | Read-only, non-executed historical evidence |

### Written

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/loaded-runtime-binding-refactor/loaded-runtime-binding-refactor.plan.md` | Plan-Creator | Repo-visible implementation/release contract |
| Python spec | `plan/loaded-runtime-binding-refactor/loaded-runtime-binding-refactor.spec.md` | Plan-Creator | Non-trivial behavior contract |
| Step tracker | `plan/loaded-runtime-binding-refactor/loaded-runtime-binding-refactor.step.md` | Plan-Creator then Implementer | Plan authoring, then truthful implementation progress |
| Plan review | `plan/loaded-runtime-binding-refactor/loaded-runtime-binding-refactor.plan-review.json` | Plan-Reviewer | Independent planning verdict |
| Human check | `plan/loaded-runtime-binding-refactor/loaded-runtime-binding-refactor.human-check.json` | Human | Pre-implementation gate |
| Human merge | `plan/loaded-runtime-binding-refactor/loaded-runtime-binding-refactor.human-merge.json` | Human | Pre-merge gate |
| RED evidence | `plan/loaded-runtime-binding-refactor/loaded-runtime-binding-refactor.red-tests.yaml` | Tester | Fresh RED and type-analysis evidence |
| Topic Pyright config | `plan/loaded-runtime-binding-refactor/pyrightconfig.json` | Tester | Strict routing for this topic’s sole live fixture |
| Implementation review | `plan/loaded-runtime-binding-refactor/loaded-runtime-binding-refactor.implementation-review.yaml` | Reviewer | Implementation-conformance verdict |
| Code review | `plan/loaded-runtime-binding-refactor/loaded-runtime-binding-refactor.code-review.yaml` | Reviewer | Independent code-quality verdict |
| Loader package initializer | `src/async_model_gateway/model_runtime/model_pool/loaders/__init__.py` | Implementer | Private loader package boundary without public re-export |
| Generic loader source | `src/async_model_gateway/model_runtime/model_pool/loaders/_model_loader.py` | Implementer | Nominal generic `ModelLoader` ABC |
| ONNX loader source | `src/async_model_gateway/model_runtime/model_pool/loaders/_onnx_model_loader.py` | Implementer | Precise `_OnnxRuntime` loader |
| ONNX runtime protocol | `src/async_model_gateway/model_runtime/runtime_model/_onnx_runtime.py` | Implementer | Private provider runtime Protocol |
| ONNX loader tests | `tests/model_runtime/model_pool/test_onnx_model_loader.py` | Tester | Precise loader/raw runtime behavior |

### Deleted

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Obsolete live typecheck fixture | `tests/typecheck/onnx_local_runtime_acquisition.py` | Implementer | Delete invalid fixture that imports removed pool/runtime exports |
| Obsolete live typecheck fixture | `tests/typecheck/model_execution_minimal_consumption.py` | Implementer | Delete invalid fixture that imports removed public execution export |
| Obsolete live typecheck fixture | `tests/typecheck/runtime_model_generic_erasure.py` | Implementer | Delete invalid fixture that imports removed runtime/pool exports |
| Replaced loader source | `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` | Implementer | Delete superseded local dispatcher |
| Replaced ONNX helper | `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py` | Implementer | Delete superseded ONNX helper |
| Replaced loader tests | `tests/model_runtime/model_pool/test_local_model_loader.py` | Implementer | Delete tests for superseded dispatcher |

### Modify

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Runtime resource | `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py` | Implementer | Replace abstract opaque contract with concrete generic resource |
| Runtime package surface | `src/async_model_gateway/model_runtime/runtime_model/__init__.py` | Implementer | Remove package re-export |
| Executor implementation | `src/async_model_gateway/model_runtime/model_execution/execution.py` | Implementer | Replace public execution seam with internal executor lifecycle |
| Executor package surface | `src/async_model_gateway/model_runtime/model_execution/__init__.py` | Implementer | Remove package re-export |
| ONNX binding and resolver | `src/async_model_gateway/model_runtime/model_pool/_runtime_binding.py` | Implementer | Outer routing erasure over precise ONNX pairing |
| Pool implementation | `src/async_model_gateway/model_runtime/model_pool/pool.py` | Implementer | Internal injected-loader acquisition without resolver/cache |
| Pool package surface | `src/async_model_gateway/model_runtime/model_pool/__init__.py` | Implementer | Remove `ModelPool` export |
| Composition owner | `src/async_model_gateway/model_runtime/_local_runtime_composition.py` | Implementer | Resolve-once composition implementation |
| Runtime resource tests | `tests/model_runtime/runtime_model/test_loaded_runtime_model.py` | Tester | Dataclass, timestamp and forbidden-surface coverage |
| Runtime package tests | `tests/model_runtime/runtime_model/test_runtime_model_package_surface.py` | Tester | Empty export-surface coverage |
| Executor behavior tests | `tests/model_runtime/model_execution/test_model_execution.py` | Tester | Gate/result/failure/cancellation lifecycle |
| Executor surface tests | `tests/model_runtime/model_execution/test_model_execution_package_surface.py` | Tester | Empty exports and forbidden-import AST coverage |
| Pool behavior tests | `tests/model_runtime/model_pool/test_model_pool.py` | Tester | Generic injection and no-cache behavior |
| Pool surface tests | `tests/model_runtime/model_pool/test_model_pool_package_surface.py` | Tester | Internal acquire signature and empty export coverage |
| ONNX acquisition tests | `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py` | Tester | CPU-only acquisition regression without removed exports |
| Composition tests | `tests/model_runtime/test_local_runtime_composition.py` | Tester | Resolve-once and binding-continuity tests |
| Type fixture | `tests/typecheck/loaded_runtime_binding_refactor.py` | Tester | Strict precise pairing and outer-erasure evidence |
| Release README | `README.md` | Implementer after merge | Internal-only boundary summary |
| Release architecture | `docs/architecture.md` | Implementer after merge | Architecture status update |
| Release core spec | `docs/specs/core-abstractions-boundary.md` | Implementer after merge | Shared vocabulary/boundary update |
| Release model spec | `docs/specs/model-side-boundary.md` | Implementer after merge | Detailed model-side contract update |
| Runtime version | `src/async_model_gateway/__version__.py` | Implementer after merge | Set runtime version to 0.7.0 |
| Package version | `pyproject.toml` | Implementer after merge | Set package version to 0.7.0 |
| Lockfile | `uv.lock` | Implementer after merge | Regenerate 0.7.0 metadata |

No path appears in more than one artifact-state table. All unlisted paths are out of contract.

## Stable library metadata

- `README row`: internal-only composition and pre-acquire binding continuity; no public pool/loader/executor/composition entrypoint and no real invocation。
- `VERSION bump`: `0.6.0 -> 0.7.0` in runtime version, package metadata, lockfile。
- `timing`: release after verified merge and pre-merge clearance。
- `tag`: lightweight `v0.7.0` targets post-merge release commit。
- No GitHub Release or package publication。

## Implementation Steps

1. Tester writes/revises declared behavior, surface, AST, composition, precise ONNX loader and ONNX regression tests; writes topic Pyright config/type fixture; executes exact topic Pyright against unchanged production and writes RED evidence including actual analyzed fixture path。
2. Implementer modifies concrete runtime model/package export boundary。
3. Implementer modifies executor/package export boundary with exact gate/timestamp/direct-await lifecycle。
4. Implementer deletes old loader/helper, writes private `model_pool/loaders/` package and `_OnnxRuntime` Protocol, then modifies binding/resolver to retain precise ONNX pairing until outer routing erasure。
5. Implementer modifies composition/private factory and internal pool acquire; removes pool package export。
6. Implementer deletes all declared obsolete sources/tests/live fixtures, leaves all four historical configs untouched, runs pre-merge validation, checks path contract, updates tracker。

## Validation / Acceptance Checks

### TestCase

- **Happy path**: recording binding preserves loader/executor/runtime/invocation/result identity through exact composition sequence; production ONNX loader/executor/binding share `_OnnxRuntime` with `get_providers() -> list[str]` before outer resolver erasure。
- **Invalid input**: non-artifact stays `TypeError`; unsupported family remains `NotImplementedError`; ONNX options errors unchanged。
- **Edge case**: waiting executor does not update time; post-gate failure retains time; cancellation releases gate。
- **Regression**: ONNX CPU-only loading remains through the new loader package; explicit family wins; acquire has no reuse/cache。
- **Backward compatibility**: intentional package export removal; three invalid live fixtures absent; four historical configs exist, unchanged and unexecuted。

Additional acceptance:

- Executor AST has no forbidden imports or late dispatch。
- New strict fixture proves matching fake loader/executor/runtime/invocation/result, `_OnnxRuntime.get_providers() -> list[str]`, the loader’s sole optional-stub `cast(_OnnxRuntime, ...)`, and outer resolver’s sole `RuntimeBinding[object, object, object]` erasure cast.
- Pre-implementation and pre-merge JSON gates have exact locked shapes。
- Release versions all say 0.7.0 and lightweight tag targets release commit。

## Reviewer Handoff

```json
{
  "verdict": "needs-rework",
  "blocking_issues": [
    {
      "issue": "Awaiting independent Plan-Reviewer verdict.",
      "file": "plan/loaded-runtime-binding-refactor/loaded-runtime-binding-refactor.plan.md",
      "fix": "Replace this skeleton with the reviewer’s actual verdict."
    }
  ],
  "copilot_feedback_triage": {
    "ADDRESS": [],
    "DISCUSS": [],
    "SKIP": []
  }
}
```

## Post-merge / release actions

After verified merge and existing exact human-merge artifact:

```json
{"status":"cleared_for_merge","pr":"<actual PR identifier>"}
```

modify only declared release docs/version/lockfile, validate 0.7.0, create release commit, then create/push lightweight `v0.7.0` at that commit. Do not create GitHub Release or publish packages.

## Open Questions / Unresolved Items

None. All implementation, async, gate, artifact-path, and release decisions required
for this topic are locked above.

## Python Implementation Extension

### Goal

Implement and verify the internal sequence only; no public caller exists.

### Non-goals

See `Out-Out-Scope` and `Non-Goal`; no public surface, cache/lifecycle, real ONNX invocation, remote path, or pre-merge release work.

### Current Context

Current code exports abstract runtime model, pool, and public `ModelExecution`; pool retains loader; no composition owner exists. Existing loader/helper are monolithic and lack an internal provider-runtime Protocol. Three live type fixtures rely on removed exports. Four historical configs reference old fixtures but remain non-executed evidence.

### Requirements

1. Composition is only production `resolve()` caller.
2. Binding identity survives resolve/acquire/execute.
3. Pool accepts injected loader/concurrency and owns no resolver/executor/cache.
4. Executor owns gate/timestamp lifecycle and imports no dispatch owner.
5. `_OnnxRuntime` Protocol requires only `get_providers() -> list[str]`, preserves production loader/executor/binding generic pairing, and is cast only at optional-stub loader boundary before outer resolver erasure.
6. Old loader/helper/test and three live legacy fixtures are removed; historical configs are retained untouched.

### Decisions

- Async-planning status: triggered — cite trigger evidence: async composition/load, semaphore ownership, timestamp ordering, cancellation semantics.
- Module/package placement: composition private under `model_runtime`; `_OnnxRuntime` Protocol private under `runtime_model`; binding/pool private under `model_pool`; loaders split into private `model_pool/loaders/`; executor internal under `model_execution`.
- New public API: no.
- Interface changes: former package exports are removed; acquire is internal generic injected signature.
- Breaking changes allowed: yes; locked human choice without adapters.
- New dependencies: no.
- Error handling strategy: invalid artifact `TypeError`; unsupported family/ONNX invocation `NotImplementedError`; other errors/cancellation propagate.
- Typing strategy: strict TypeVars/new fake-runtime fixture; private `_OnnxRuntime` Protocol has only `get_providers() -> list[str]` and is the production ONNX type for loader/executor/binding; `cast(_OnnxRuntime, ...)` appears only around `asyncio.to_thread(InferenceSession, ...)` at optional-stub boundary, while only `_RuntimeBindingResolver` casts to `RuntimeBinding[object, object, object]`; no `Any`.

### Async boundary decision

Composition, split loader, pool acquire and executor remain async. Protocol/resolver/state remain sync. No task, queue or public orchestration exists.

### Resource lifecycle decision

Pool creates one wrapper/gate per acquisition and retains nothing. Executor temporarily owns gate permit. No close/unload/context-manager policy.

### Concurrency model

One composition call resolves once, awaits one injected loader and executor. `Semaphore(1)` serializes per wrapper. No sharing/fan-out/cache.

### Failure model

No wrapping/translation. PICKLE/TORCH fail before load. ONNX executor failure is inside gate lifecycle. Identity tests prevent resolver mismatch.

### Cancellation / timeout policy

Caller owns cancellation. Loader/invocation cancellation propagates unchanged; async context manager releases gate. No timeout/retry/shield policy.

### Validation plan

Fresh RED includes focused tests, exact topic Pyright analysis and AST checks. GREEN includes `_OnnxRuntime.get_providers()` contract, two locked cast boundaries, precise ONNX pairing/outer erasure, composition continuity, gate lifecycle, no-cache behavior, package removal, declared source/test/fixture deletion, four historical-config preservation and ONNX regression.

### Handoff notes for the implementer

Only composition resolves. Keep `_OnnxRuntime` precise through loader/executor/binding; cast it only after `asyncio.to_thread(InferenceSession, ...)`, and erase binding only in outer resolver. Never resolve in pool/executor, store binding in loaded model, add a public caller, or edit/delete/execute historical configs.

### Async contradiction log

| Contradiction | Source A | Source B | Risk impact | Decision owner / next action | Classification |
| --- | --- | --- | --- | --- | --- |
| Earlier draft example translated execution errors | Draft example | Locked unchanged propagation | Alters error/cancellation identity | Human lock wins; no catch | resolved |

### Public Contract / API Changes

No public API is added. Existing package exports for `ModelPool`, `LoadedRuntimeModel`, and `ModelExecution` are intentionally removed. Internal acquire uses locked generic injection.

### Affected Files / Modules

Use `ReadOnly`, `Written`, `Deleted`, and `Modify` under canonical Artifact Paths as the full path contract.

### Implementation Steps

Use the six canonical pre-merge steps. Release remains only under Post-merge actions.

### Test Plan

Use canonical `TestCase` categories and additional acceptance checks.

### Validation Commands

```bash
uv run pytest --no-cov tests/model_runtime -v
uv run pytest -v
uv run ruff check src tests plan/loaded-runtime-binding-refactor
uv run pyright
uv run pyright --project plan/loaded-runtime-binding-refactor/pyrightconfig.json tests/typecheck/loaded_runtime_binding_refactor.py
uv lock --check
test ! -e tests/typecheck/onnx_local_runtime_acquisition.py
test ! -e tests/typecheck/model_execution_minimal_consumption.py
test ! -e tests/typecheck/runtime_model_generic_erasure.py
test ! -e src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py
test ! -e src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py
test ! -e tests/model_runtime/model_pool/test_local_model_loader.py
```

Topic config must be:

```json
{
  "include": ["../../tests/typecheck/loaded_runtime_binding_refactor.py"],
  "extraPaths": ["../../src"],
  "pythonVersion": "3.10",
  "typeCheckingMode": "strict"
}
```

Release-only:

```bash
rg -n '0\.7\.0' README.md pyproject.toml src/async_model_gateway/__version__.py uv.lock
uv lock --check
```

### Risks

Resolver leakage breaks continuity; premature ONNX type erasure breaks pairing evidence; stale docs preserve obsolete architecture; unremoved live fixtures break full Pyright; editing historical configs corrupts evidence.

### Rollback Plan

Before merge, revert declared Written/Modify paths and restore all Deleted sources/tests/fixtures if reversing the change. Do not alter ReadOnly historical configs. After tag, never retarget/delete `v0.7.0`; use a new corrective topic.

### Open Questions

None.
