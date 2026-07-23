> Semantic warning: `analysis/local-runtime-acquisition-documentation-consistency/requirements.md`
> 與 `analysis/local-runtime-acquisition-documentation-consistency/technical-spec.md`
> 均不存在。未找到 topic-local explorer/planner repo-visible evidence；本 plan 依 Human
> 已鎖定的 docs-only outcome、現有四份文件與已落地 source contract 撰寫。這是
> incomplete-layer mode，不得擴張為 execution、provider adapter 或 API design work。

# local-runtime-acquisition-documentation-consistency

## Goal / Outcome

- 對齊四份 canonical 文件，使其一致描述已落地的 local acquisition path：
  `ModelArtifact → LocalModelLoader → provider session → LoadedRuntimeModel →
  ModelExecution → result`。
- 完成後文件必須同時明確限制：provider session 僅透過 opaque handle 的 non-public
  handoff 交給既有 injected invoker；這不是 public `execute(...)`、ONNX invoker 或
  完整 provider execution integration。

## Scope

### In scope

- 更新 `README.md` 的 first-read local runtime summary，移除「真實 local
  runtime acquisition 尚未實作」的過時說法，保留 invocation/deferred boundaries。
- 更新 `docs/architecture.md` 的 model-side local path 與 responsibility wording，
  使 private loader-local handle construction、`ModelExecution` ownership 與 result
  handoff 相符。
- 更新 `docs/specs/model-side-boundary.md`，以 explicit local flow 說明
  `ModelArtifact`、`LocalModelLoader`、provider session、`LoadedRuntimeModel` 及
  `ModelExecution` 的責任與限制。
- 更新 `docs/specs/core-abstractions-boundary.md` 的依賴方向摘要，使其交叉文件
  用語與相同 flow 一致。
- 建立本 topic 的 plan、spec、step、plan-review 與 human-check artifacts；使用
  existing tests/type/lint checks 驗證文件未誤述已鎖定行為。

### Out of scope

- public API、`LoadedRuntimeModel.execute(...)`、provider getter、runtime factory、
  `ExecuteRequest`/`ExecuteResult`、invoker、provider adapter、provider dispatch 或
  ONNX inference。
- `ModelArtifact`、`LoaderFamily`、`ModelPool`、`LocalModelLoader`、
  `LoadedRuntimeModel`、`ModelExecution`、optional dependencies、lockfile、tests 或
  source code 的任何變更。
- session cache/reuse/close/unload、retry、timeout、cancellation policy、remote
  `ModelGateway`、orchestrator wiring、batching、preprocessing 或 tensor schema。
- version、release notes、tag、package publication、commit、push 或 PR。

## Locked Decisions

- D1 verdict: `non-trivial` docs-only change。四份 canonical documents 必須就已落地
  的 multi-boundary flow 說同一件事，且不可將 acquisition 描述誤升級為 execution。
- Async-planning status: exempt — cite exemption evidence: `Artifact Paths` 的唯一
  implementation targets 是 Markdown docs；不改任何 async function、task/lifecycle、
  concurrency、failure、cancellation、timeout 或 retry policy。fresh checks 只驗證
  existing behavior，並不改變它。
- Document the fixed flow as `ModelArtifact → LocalModelLoader → provider session →
  LoadedRuntimeModel → ModelExecution → result`. `ModelPool.acquire(...)` remains the
  public local entrypoint that retains the private loader; it is not a new node or API
  in the requested explanatory chain.
- `LoadedRuntimeModel` remains the public opaque acquisition handle. Its only public
  semantic is `loader_family`; no document may imply a public provider getter or
  executable `execute(...)` method.
- `LocalModelLoader` performs explicit `LoaderFamily` routing. Current ONNX acquisition
  builds a CPU-only provider session and creates a loader-local private handle; PICKLE
  and TORCH remain fail closed. This documentation topic does not change those facts.
- `ModelExecution` is the sole production owner of the non-public provider handoff. It
  direct-awaits an injected async invoker and returns that invocation result; it does
  not make the loader invoke a provider or establish a real ONNX invoker.
- Stable-library intent: documentation-only update with no version bump and no release
  workflow. `README.md` changes are made during implementation/publish preparation,
  but merge remains the terminal state.
- No source/test/dependency changes and no new test files. Existing tests are validation
  probes, not authorization to widen the topic.

## Boundaries / Exclusions

- Plan-Creator writes only this topic's planning artifacts. Implementer may update only
  the four declared documents after independent plan review and repo-visible Human check.
  Reviewer verifies wording/contract alignment; Human closes planning and merge gates.
- `README.md` remains concise first-read material. `docs/architecture.md` explains
  responsibility boundaries; `model-side-boundary.md` owns model-side detail; and
  `core-abstractions-boundary.md` remains an index/dependency summary rather than a
  duplicate specification.
- Do not re-open the loader-local opaque-handle, `ModelExecution` sole-consumer, or
  no-public-execution decisions from the preceding implementation topic.
- Any need to alter source, tests, dependency policy, public surface, release timing, or
  to document an unimplemented provider operation returns to
  `spec-and-plan-finalization`.

## Status / Allowed Transitions

- **Current**: `review-ready`; planning artifacts are ready for an independent
  Plan-Reviewer.
- **Execution model**: `spec-and-plan-finalization -> implement-plan -> pr-comment ->
  pr-comment-review-pr-comments-and-fix`; this topic stops at `merged` and has no
  conditional `release` workflow.
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

- Implementation is forbidden until the declared plan-review artifact records
  `approved` and the declared human-check artifact records clearance for
  `implement-plan`.
- This docs-only topic does not have a RED-test authoring subphase. Implementer first
  makes the four bounded documentation edits, then runs fresh existing validation and
  records actual step progress before independent documentation review/PR routing.
- A plan-review or implementation finding that changes the fixed flow or a path in
  `Artifact Paths` routes back to `spec-and-plan-finalization`.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/local-runtime-acquisition-documentation-consistency/local-runtime-acquisition-documentation-consistency.plan.md` | Plan-Creator | Repo-visible execution contract |
| Documentation spec | `plan/local-runtime-acquisition-documentation-consistency/local-runtime-acquisition-documentation-consistency.spec.md` | Plan-Creator | D1 behavior and wording contract |
| Step tracker | `plan/local-runtime-acquisition-documentation-consistency/local-runtime-acquisition-documentation-consistency.step.md` | Plan-Creator, then phase owner | Workflow state and actual documentation progress |
| Plan review | `plan/local-runtime-acquisition-documentation-consistency/local-runtime-acquisition-documentation-consistency.plan-review.json` | Plan-Reviewer | Independent planning verdict |
| Human check | `plan/local-runtime-acquisition-documentation-consistency/local-runtime-acquisition-documentation-consistency.human-check.json` | Human | Explicit clearance for `implement-plan` |
| First-read documentation | `README.md` | Implementer | Concise current local runtime availability and deferral summary |
| Architecture documentation | `docs/architecture.md` | Implementer | Model-side responsibility and local acquisition/execution flow |
| Model-side specification | `docs/specs/model-side-boundary.md` | Implementer | Detailed local acquisition and internal handoff contract |
| Core abstractions specification | `docs/specs/core-abstractions-boundary.md` | Implementer | Cross-boundary dependency flow summary |

### ReadOnly

- `src/async_model_gateway/model_runtime/model_artifact/artifact.py`
- `src/async_model_gateway/model_runtime/model_artifact/loader_family.py`
- `src/async_model_gateway/model_runtime/model_pool/pool.py`
- `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`
- `src/async_model_gateway/model_runtime/model_pool/_onnx_runtime_loader.py`
- `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py`
- `src/async_model_gateway/model_runtime/model_execution/execution.py`
- `tests/model_runtime/model_artifact/test_model_artifact.py`
- `tests/model_runtime/model_pool/test_local_model_loader.py`
- `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`
- `tests/model_runtime/runtime_model/test_loaded_runtime_model.py`
- `tests/model_runtime/model_execution/test_model_execution.py`
- `pyproject.toml`
- `uv.lock`
- `src/async_model_gateway/__version__.py`
- all artifacts under `plan/local-runtime-handle-ownership-clarification/`

### Written

- The five topic-local plan/spec/step/plan-review/human-check paths listed above.

### Updated

- `README.md`
- `docs/architecture.md`
- `docs/specs/model-side-boundary.md`
- `docs/specs/core-abstractions-boundary.md`

### Deleted

- None. Any deletion, test/source/dependency modification, or path outside this table is
  plan drift.

Artifact path notes:

- `README.md` is the only stable first-read surface affected. No package export, version,
  dependency, release-note, or publication artifact changes.
- Listed paths are the executable contract; implementation must stop rather than alter an
  undeclared file.

## Stable library metadata

- `README row`: update only the `目前階段` local runtime/runtime-model summary and
  `尚未實作` wording needed to distinguish completed ONNX acquisition from deferred
  invocation; do not perform a full README rewrite.
- `VERSION bump`: no bump. `src/async_model_gateway/__version__.py`, `pyproject.toml`,
  and `uv.lock` remain ReadOnly.
- `timing`: documentation changes occur in `publish-in-progress` after the planning
  gates; no separate release action is declared.
- `rationale`: first-read and canonical architecture documentation must not contradict
  the already released acquisition boundary or overstate execution capability.

## Implementation Steps

1. In `README.md`, revise only the existing local runtime/runtime-model paragraphs to
   state that ONNX local acquisition exists through the opaque handle and that execution
   remains a separate injected-invoker boundary; retain all non-goals as deferred.
2. In `docs/architecture.md`, replace stale local-handle ownership wording and add the
   fixed acquisition-to-result flow with `ModelExecution` result handoff, while retaining
   its explicit non-claims about real provider invocation and orchestration.
3. In `docs/specs/model-side-boundary.md`, make the detailed local path consistently
   describe explicit family routing, ONNX provider-session acquisition, loader-local
   private handle construction, opaque `LoadedRuntimeModel`, and sole
   `ModelExecution` internal consumption; do not add an adapter/invoker API.
4. In `docs/specs/core-abstractions-boundary.md`, update only the dependency-direction
   summary so the same chain and deferred execution boundaries are discoverable without
   duplicating model-side detail.
5. Run fresh focused and full validation, Pyright, Ruff, and diff checks; confirm all
   changed paths are the four declared documents plus topic evidence/step state, then
   record actual progress without closing any Human or PR gate.

## Validation / Acceptance Checks

- The same ordered local flow appears consistently across the four declared documents;
  each names `ModelArtifact`, `LocalModelLoader`, provider session,
  `LoadedRuntimeModel`, `ModelExecution`, and result at an appropriate level of detail.
- README and architecture documentation no longer say real local runtime acquisition is
  absent, while all documents continue to say ONNX inference/provider invoker, public
  execution APIs, remote/orchestrator wiring, lifecycle, retry, and timeout are deferred.
- The four documents agree that `LoadedRuntimeModel` is opaque, `loader_family` is its
  sole public semantic, and provider runtime crosses only through a non-public handoff
  owned by existing `ModelExecution`.
- Existing source tests continue to validate explicit routing, CPU-only ONNX acquisition,
  opaque provider identity handoff, direct-await, exception propagation, and cancellation
  propagation; no test files are added or modified.
- Run:

```bash
uv run --extra onnx pytest --no-cov tests/model_runtime/model_artifact tests/model_runtime/model_pool tests/model_runtime/runtime_model tests/model_runtime/model_execution -v
uv run --extra onnx pytest -v
uv run --extra onnx pyright
uv run --extra onnx ruff check docs src tests plan/local-runtime-acquisition-documentation-consistency
git diff --check
```

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

No release workflow required. Human merge ends this documentation-only topic; do not
change version, tag, release notes, or package publication state.

## Open Questions / Unresolved Items

- None. Analysis/explorer/planner artifacts are absent but the Human-locked flow,
  exact document paths, and behavior boundaries are sufficient for this bounded plan.
