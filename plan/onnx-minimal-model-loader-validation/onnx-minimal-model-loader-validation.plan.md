> Semantic warning: `analysis/onnx-minimal-model-loader-validation/requirements.md`
> 與 `analysis/onnx-minimal-model-loader-validation/technical-spec.md` 均不存在。
> 本 plan 依 Human 已鎖定的 runtime-evidence、Protocol-boundary 與 typing decisions
> 撰寫，採 incomplete-layer mode；不得據此擴張 `_OnnxRuntime`、Loader production
> return contract、inference、dependencies、CI、release 或 architecture。

# onnx-minimal-model-loader-validation

## Goal / Outcome

- 建立並納版控可 deterministic 重建的最小 Identity ONNX artifact，並以真實 pipeline
  證明 `generator → minimal_identity.onnx → _OnnxModelLoader →
  onnxruntime.InferenceSession → CPU provider metadata assertion`。
- 完成後，runtime evidence 會證明真實 Loader 載入 committed artifact 並回傳真實
  CPU-only session；static evidence 只證明既有 `_OnnxRuntime` Protocol 最低能力，兩者
  不互相取代，也不執行 inference。

## Scope

### In-Scope

- 新增 `tests/model_runtime/model_pool/fixtures/build_minimal_identity_model.py` 與
  committed `minimal_identity.onnx`。generator 必須使用 `onnx==1.16.2` baseline 產生
  可供 `onnxruntime==1.22.0` 載入的最小 Identity model，並提供 `--check` byte-drift
  驗證。
- 在 `tests/model_runtime/model_pool/test_onnx_model_loader.py` 補齊真實 Loader 的
  happy path：使用 static-import 的 `onnxruntime`，驗證 session 為
  `onnxruntime.InferenceSession` 且 `get_providers()` 精確等於
  `["CPUExecutionProvider"]`。
- 同一 focused loader test 必須以 non-ONNX bytes 經真實 `_OnnxModelLoader` 載入，僅
  驗證例外的 type module 屬於 `onnxruntime.*`；不得 fake importer、monkeypatch 真實
  Loader 或主張特定 provider exception class/message。
- 將 `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py` 的 valid
  model fixture 改為 committed asset，並保留既有 async offload、cancellation、options
  rejection 與 provider-failure coverage。
- 新增 `tests/typecheck/onnx_minimal_model_loader_validation.py` 與 topic-local
  `pyrightconfig.json`。witness 不 import `onnxruntime`，只證明 Loader 回傳值可傳入
  `_OnnxRuntime` helper；config 只涵蓋 witness 與 generator，strict mode 唯一允許
  `reportPrivateUsage: "none"`。

### Out-Out-Scope

- 任何 `InferenceSession.run()`、Executor invocation、輸入/輸出 tensor assertion 或
  inference capability 主張。
- `_OnnxRuntime` Protocol、`_OnnxModelLoader.load() -> _OnnxRuntime`、ModelPool、
  runtime binding、Executor、package export 與 production type contract 的變更。
- `pyproject.toml`、`uv.lock`、依賴版本、global Pyright config、README、docs、CI、
  release、commit、push、PR state 或其他 runtime family 的修改。
- source-level type suppression、`Any`、`cast`、dynamic import、test-only runtime
  module fabrication，以及 monkeypatch 真實 Loader/provider 的測試策略。

## Locked Decisions

- D1 verdict: `non-trivial`。此 topic 同時引入 binary artifact/reproducibility
  contract、provider-backed runtime evidence、async acquisition regression evidence 與
  bounded strict static witness，因此必須有 spec、fresh RED evidence、implementation
  review 與 code review。
- Production boundary 不變：`_OnnxRuntime` 維持只含 `get_providers() -> list[str]` 的
  private Protocol，`_OnnxModelLoader.load(...)` 維持回傳 `_OnnxRuntime`。要求 Pyright
  將其在 `isinstance` 前視為 `InferenceSession` 屬 production contract 變更，未獲本
  topic 授權。
- Runtime tests 必須 static-import `onnxruntime` 並取得真實
  `onnxruntime.InferenceSession`；它們是 pytest runtime evidence，因
  `onnxruntime==1.22.0` lacks stubs，不列入 topic-local strict Pyright target。
- Dedicated strict witness 不 import `onnxruntime`，只驗證 `_OnnxRuntime` 最低能力。
  Topic-local config 使用 Python 3.10 和 strict mode，唯一 diagnostic override 是
  `reportPrivateUsage: "none"`，只供 witness 消費既有 private Protocol；不得加入其他
  override、inline ignore、`Any`、`cast` 或 dynamic import。
- Generator 和 committed asset 是同一 artifact contract：normal mode 產生固定的
  `minimal_identity.onnx`，`--check` 不寫檔且在 bytes drift 時失敗。baseline versions
  是 `onnx==1.16.2` 與 `onnxruntime==1.22.0`；本 topic 不變更 manifest 或 lockfile。
- Valid artifact 的 provider assertion 精確為
  `session.get_providers() == ["CPUExecutionProvider"]`。invalid artifact 必須走真實
  Loader，僅斷言 exception module 起首為 `onnxruntime.`，避免 lock in provider
  implementation exception details。
- Async-planning status: exempt — cite exemption evidence: existing
  `_OnnxModelLoader` async boundary、`asyncio.to_thread(...)` offload、resource
  lifecycle、concurrency、failure ownership、cancellation、timeout 與 retry policy 均不
  改變；本 topic 僅以 committed artifact 提升其 evidence，並保留既有 async coverage。
- Stable-library and release intent are explicitly absent. README、VERSION、public API
  與 release metadata 均不得變更；topic 於 merge 停止。

## Boundaries / Exclusions

- Plan-Creator 只寫 plan/spec/step；Tester 只寫 RED evidence、topic Pyright config、
  generator/asset 與 tests；Implementer 只在核准路徑實作；Reviewer 只產生獨立 verdict；
  Human 單獨關閉 human-check/human-merge gates。
- `tests/model_runtime/test_local_runtime_composition.py` 僅作 PICKLE/TORCH fail-closed
  regression evidence，為 ReadOnly；不可藉本 topic 變更 composition architecture。
- Listed ReadOnly paths 只可供理解或驗證。任何要求變更 production return type、增加
  provider capability、擴張 Pyright targets/overrides、變更依賴或改變 async policy，均
  必須回到 `spec-and-plan-finalization`。
- 本 topic 的 artifact 路徑是 executable contract；later phase 若需要未列路徑，不得
  自行擴張，必須重開 planning gate。

## Status / Allowed Transitions

- **Current**: `review-ready`；Plan-Creator 已完成 plan/spec/step，等待獨立
  Plan-Reviewer verdict。
- **Execution model**: `spec-and-plan-finalization -> implement-plan -> pr-comment ->
  pr-comment-review-pr-comments-and-fix`；本 topic 在 `merged` 停止，沒有 `release`
  workflow。
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

- `implement-plan` 的 entry gate 同時需要本 topic plan-review artifact 的 fresh
  `approved` verdict 與 Human-owned `cleared_for: implement-plan` gate。chat 同意、
  green tests 或既有 review 都不是替代品。
- Python 的第一個 implementation subphase 是 Tester 的 fresh RED test authoring；
  在 RED evidence 產生前，不得建立 generator/asset 或修改 tests/config/production。
- Plan-Creator 不得預填 reviewer、human、RED、implementation-review 或 code-review
  evidence；各 phase owner 必須在其 gate 實際完成後才建立對應 artifact。

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/onnx-minimal-model-loader-validation/onnx-minimal-model-loader-validation.plan.md` | Plan-Creator | Repo-visible execution contract |
| Python spec | `plan/onnx-minimal-model-loader-validation/onnx-minimal-model-loader-validation.spec.md` | Plan-Creator | D1 non-trivial behavior contract |
| Step tracker | `plan/onnx-minimal-model-loader-validation/onnx-minimal-model-loader-validation.step.md` | Plan-Creator, then phase owner | Workflow and actual implementation progress |
| Plan review | `plan/onnx-minimal-model-loader-validation/onnx-minimal-model-loader-validation.plan-review.json` | Plan-Reviewer | Fresh independent planning verdict |
| Human check | `plan/onnx-minimal-model-loader-validation/onnx-minimal-model-loader-validation.human-check.json` | Human | Explicit `cleared_for: implement-plan` gate |
| RED evidence | `plan/onnx-minimal-model-loader-validation/onnx-minimal-model-loader-validation.red-tests.yaml` | Tester | Fresh pre-implementation failing-test evidence |
| Topic Pyright config | `plan/onnx-minimal-model-loader-validation/pyrightconfig.json` | Tester | Dedicated strict target for generator and Protocol witness |
| Implementation review | `plan/onnx-minimal-model-loader-validation/onnx-minimal-model-loader-validation.implementation-review.yaml` | Reviewer | Post-implementation plan-conformance verdict |
| Code review | `plan/onnx-minimal-model-loader-validation/onnx-minimal-model-loader-validation.code-review.yaml` | Reviewer | Independent Python quality/boundary verdict |
| Generator | `tests/model_runtime/model_pool/fixtures/build_minimal_identity_model.py` | Tester, Implementer | Deterministically creates/checks committed Identity artifact |
| Committed ONNX asset | `tests/model_runtime/model_pool/fixtures/minimal_identity.onnx` | Tester, Implementer | Real Loader input for runtime evidence |
| Real Loader tests | `tests/model_runtime/model_pool/test_onnx_model_loader.py` | Tester, Implementer | Session identity, provider metadata, invalid artifact evidence |
| Acquisition regression tests | `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py` | Tester, Implementer | Committed-asset acquisition plus existing async/error coverage |
| Protocol witness | `tests/typecheck/onnx_minimal_model_loader_validation.py` | Tester, Implementer | Strict static evidence of existing Protocol capability |

Artifact path notes:

- `README.md`, version source, `pyproject.toml`, `uv.lock`, global Pyright config,
  `.github/`, all production modules, and release artifacts are not modified by this
  topic.
- Reserved review/gate/evidence artifacts above must not be created or pre-filled by
  Plan-Creator. An edit outside this table is scope drift and returns to
  `spec-and-plan-finalization`.

### ReadOnly

- `pyproject.toml`, `uv.lock`, `README.md`, `docs/architecture.md`, global Pyright
  configuration, all `.github/` paths, and package exports.
- `src/async_model_gateway/model_runtime/model_pool/loaders/_onnx_model_loader.py`,
  `src/async_model_gateway/model_runtime/runtime_model/_onnx_runtime.py`, all other
  production runtime modules, ModelPool, binding, Executor, and composition code.
- `tests/model_runtime/test_local_runtime_composition.py` for PICKLE/TORCH fail-closed
  regression evidence only; all other unrelated tests and historical topic artifacts.

### Written

- Plan-Creator writes only this topic's `.plan.md`, `.spec.md`, and `.step.md`.
- Later owners write only their declared plan-review, human-check, RED, Pyright,
  implementation-review, and code-review artifacts when their gates actually occur.
- Tester/Implementer write the generator, committed asset, focused tests, acquisition
  regression test, and Protocol witness only after implementation entry is cleared.

### Modify

- `tests/model_runtime/model_pool/test_onnx_model_loader.py`
- `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`

### Deleted

- None. Deleting existing tests, production abstractions, dependencies, runtime
  families, or historical evidence is scope drift.

## Implementation Steps

1. Tester creates fresh RED coverage in the two declared runtime test files and the
   dedicated Protocol witness. The tests must require the committed artifact pipeline,
   true `InferenceSession`, CPU-only provider metadata, provider-origin invalid-artifact
   failure, `--check` drift detection, and unchanged acquisition async behavior; Tester
   records results only in the declared RED artifact.
2. Tester creates `tests/model_runtime/model_pool/fixtures/build_minimal_identity_model.py`
   and `minimal_identity.onnx`. The generator builds only the fixed minimal Identity
   model with the locked ONNX baseline, supports normal generation and non-writing
   `--check`, and the committed binary exactly matches normal generation.
3. Implementer updates `tests/model_runtime/model_pool/test_onnx_model_loader.py` to
   retain the existing Protocol boundary tests and add real Loader evidence using
   static `onnxruntime` imports. It asserts a genuine `InferenceSession`, exact CPU
   provider metadata, and invalid non-ONNX bytes that fail from `onnxruntime.*`; it
   must not call `run()` or monkeypatch real Loader/provider behavior.
4. Implementer updates
   `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py` to consume
   the committed asset for valid-model paths while preserving existing options,
   provider-failure, thread-offload, and cancellation assertions. No production code,
   inference behavior, or async policy changes are allowed.
5. Tester creates the topic-local `pyrightconfig.json` and
   `tests/typecheck/onnx_minimal_model_loader_validation.py`. The config targets only
   the generator and witness with Python 3.10 strict checking; the witness proves
   `await _OnnxModelLoader().load(...)` is accepted by an `_OnnxRuntime` helper without
   importing `onnxruntime` or changing the production return annotation.
6. Implementer runs the declared validation, checks that only Artifact Paths changed,
   truthfully updates step progress, and hands the completed topic to independent
   implementation/code review without creating reviewer or human evidence.

## Validation / Acceptance Checks

- Plan/spec/step exist; the step tracker mirrors all six implementation steps and
  retains the six canonical workflow stages.
- Running the generator in normal mode and `--check` establishes byte-identical,
  committed valid ONNX input. The check mode must detect deliberate byte drift without
  rewriting the file.
- Real pytest evidence flows through the committed asset and genuine
  `_OnnxModelLoader`, returns `onnxruntime.InferenceSession`, and asserts exactly
  `["CPUExecutionProvider"]`. No test invokes `InferenceSession.run()`.
- The invalid artifact travels through the real Loader and only asserts the provider
  origin using `type(error).__module__.startswith("onnxruntime.")`; fake importer,
  dynamic import, provider monkeypatch, exception-message coupling, `Any`, and cast
  are prohibited.
- Existing `_OnnxRuntime` remains the only static Loader result contract. Dedicated
  strict Pyright passes for the generator/witness only; runtime tests are intentionally
  excluded because `onnxruntime==1.22.0` has no stubs.
- Existing acquisition offload/cancellation/options/provider-failure tests still pass;
  composition regression proves PICKLE/TORCH remain fail closed. No listed ReadOnly
  production/config/dependency path changes.
- Run:

```bash
uv run --group dev python -c 'import onnx, onnxruntime; assert onnx.__version__ == "1.16.2"; assert onnxruntime.__version__ == "1.22.0"'
uv run --group dev python tests/model_runtime/model_pool/fixtures/build_minimal_identity_model.py --check
uv run --group dev pytest --no-cov tests/model_runtime/model_pool/test_onnx_model_loader.py -v
uv run --group dev pytest --no-cov tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py -v
uv run --group dev pytest --no-cov tests/model_runtime/test_local_runtime_composition.py -v
uv run --group dev pyright --project plan/onnx-minimal-model-loader-validation/pyrightconfig.json
uv lock --check
uv run --group dev pytest -v
uv run --group dev pyright
uv run --group dev ruff check src tests plan/onnx-minimal-model-loader-validation
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

No release workflow required. After merge, stop; do not change README, version, tags,
publication, release state, or architecture documentation under this topic.

## Open Questions / Unresolved Items

None. The absent analysis layer is recorded as a semantic warning; it does not permit
implementation to rediscover or broaden the locked runtime, Protocol, typing, or
release decisions.

## Python Implementation

### Goal

Provide reproducible, real-provider parsing evidence for the committed minimal ONNX
Identity artifact while preserving the existing private Protocol and Loader return
contract.

### Non-goals

- No inference, output-value assertion, ONNX invoker, Executor behavior, GPU support,
  provider configuration, session lifecycle, cache, close/unload, timeout, or retry.
- No change to production `_OnnxRuntime`, `_OnnxModelLoader`, ModelPool, binding,
  Executor, package exports, public API, dependency manifest, lockfile, global type
  configuration, README, docs, CI, version, release, commit, or PR state.
- No `Any`, `cast`, inline type ignore, dynamic import, fabricated modules, fake
  importer, or monkeypatch of real Loader/provider in the new evidence.

### Current Context

- `src/async_model_gateway/model_runtime/model_pool/loaders/_onnx_model_loader.py`
  loads the artifact path in `asyncio.to_thread(...)` with
  `providers=["CPUExecutionProvider"]` and returns `_OnnxRuntime`; the provider
  boundary already has the sole production cast needed for missing third-party stubs.
- `_OnnxRuntime` intentionally exposes only `get_providers()`. Existing
  `test_onnx_model_loader.py` primarily tests Protocol structure and mocked loader
  delegation, while acquisition tests dynamically create a temporary Identity model.
- Dev dependencies already resolve the fixed baseline `onnx==1.16.2` and
  `onnxruntime==1.22.0`; no manifest change is needed. The global Pyright config
  excludes tests and strict-checks `src` only.

### Requirements

1. The committed `minimal_identity.onnx` is generated by the declared deterministic
   script and is a valid ONNX Identity model loadable by `onnxruntime==1.22.0`.
2. Real Loader tests use that committed file, prove the result is a true
   `onnxruntime.InferenceSession`, and assert the exact CPU-only provider list without
   calling inference.
3. Invalid non-ONNX bytes enter the real Loader and fail with an exception whose type
   module begins `onnxruntime.`; the test does not couple to a provider message/class.
4. Acquisition tests preserve their async offload/cancellation/options/provider-failure
   coverage while taking valid input from the committed asset.
5. The dedicated strict witness proves the unchanged `_OnnxRuntime` capability and
   cannot accidentally demand `InferenceSession` typing at the Loader boundary.
6. Topic-local Pyright config targets only the generator/witness and permits only
   `reportPrivateUsage: "none"`; no source-level suppression or global config change.

### Decisions

- Async-planning status: exempt — cite exemption evidence: no async boundary,
  lifecycle, concurrency, failure ownership, cancellation, timeout, or retry behavior
  changes; existing `asyncio.to_thread(...)` and async regression tests remain as-is.
- Module/package placement: generator and committed binary live only in
  `tests/model_runtime/model_pool/fixtures/`; runtime evidence modifies only the two
  declared model-pool test files; Protocol witness lives only in `tests/typecheck/`.
- New public API: no.
- Interface changes: no; `_OnnxModelLoader.load(...) -> _OnnxRuntime` and
  `_OnnxRuntime.get_providers() -> list[str]` are preserved exactly.
- Breaking changes allowed: no; this topic adds evidence/fixtures only.
- New dependencies: no; use existing dev baselines `onnx==1.16.2` and
  `onnxruntime==1.22.0` without editing manifest or lockfile.
- Error handling strategy: valid flow preserves Loader behavior; invalid artifact
  propagates the real provider failure unaltered and the test only establishes its
  `onnxruntime.` origin.
- Typing strategy: static imports in runtime pytest evidence; a separate no-provider
  Protocol witness under topic-local strict Pyright. No `Any`, `cast`, dynamic import,
  inline ignore, or production return-contract widening.

### Public Contract / API Changes

No public API changes. `_OnnxRuntime` remains private and minimal;
`_OnnxModelLoader.load(self, artifact: ModelArtifact) -> _OnnxRuntime` remains its
production return contract. Runtime `isinstance` proof is test-only provider evidence,
not a new static contract.

### Affected Files / Modules

Likely affected files:

- `tests/model_runtime/model_pool/fixtures/build_minimal_identity_model.py`
- `tests/model_runtime/model_pool/fixtures/minimal_identity.onnx`
- `tests/model_runtime/model_pool/test_onnx_model_loader.py`
- `tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`
- `tests/typecheck/onnx_minimal_model_loader_validation.py`
- `plan/onnx-minimal-model-loader-validation/pyrightconfig.json`

Candidate files to inspect:

- `src/async_model_gateway/model_runtime/model_pool/loaders/_onnx_model_loader.py`
- `src/async_model_gateway/model_runtime/runtime_model/_onnx_runtime.py`
- `tests/model_runtime/test_local_runtime_composition.py`
- `pyproject.toml`

### Implementation Steps

1. Create fresh RED tests and Protocol witness for the exact runtime/static evidence
   contract; write the RED result only to the declared Tester-owned evidence file.
2. Add the deterministic fixture generator and committed minimal Identity ONNX binary,
   then make `--check` report byte drift without rewriting the artifact.
3. Add real Loader happy/invalid-artifact evidence to
   `test_onnx_model_loader.py` using static `onnxruntime` import and no inference.
4. Replace the valid temporary-model fixture in
   `test_onnx_local_runtime_acquisition.py` with the committed asset while retaining
   its existing async/error tests.
5. Add the isolated strict Pyright config and no-provider Protocol witness without
   changing production typing or global configuration.
6. Execute all validation commands, check scope/path compliance, update actual step
   state, and hand off to independent reviewers.

### Test Plan

Test files: `tests/model_runtime/model_pool/test_onnx_model_loader.py`,
`tests/model_runtime/model_pool/test_onnx_local_runtime_acquisition.py`,
`tests/model_runtime/test_local_runtime_composition.py`, and
`tests/typecheck/onnx_minimal_model_loader_validation.py`.

#### TestCase

- Happy path: generator builds/checks the committed Identity model; the real Loader
  returns `onnxruntime.InferenceSession` with exactly `CPUExecutionProvider`.
- Invalid input: non-ONNX bytes passed through the real Loader raise a provider-origin
  exception, and existing non-empty options validation continues to reject before
  session construction.
- Edge case: `--check` fails when committed bytes drift; it does not regenerate or
  rewrite the asset during the check.
- Regression: acquisition still offloads synchronous construction, propagates
  cancellation/provider failure, and composition keeps PICKLE/TORCH fail closed.
- Backward compatibility: strict witness accepts the Loader result as `_OnnxRuntime`;
  the existing private Protocol, production return annotation, package exports, and
  no-inference boundary stay unchanged.

### Validation Commands

Use the exact commands in `Validation / Acceptance Checks`, including locked-version
preflight, generator check, focused runtime tests, composition regression, dedicated
strict Pyright, lock validation, full suite, global Pyright, Ruff, and diff check.

### Risks

- ONNX serialization can drift across generator versions; the `--check` contract must
  compare the committed bytes and the plan fixes the generator/runtime baseline.
- Testing a broad provider exception class/message would make the test fragile across
  `onnxruntime` internals; only its module origin is contractual.
- Adding `InferenceSession` to the static Loader contract merely to satisfy runtime
  tests would expand the production architecture; strict witness must remain separate.

### Rollback Plan

Revert only the generator, committed asset, two declared runtime test files,
`tests/typecheck/onnx_minimal_model_loader_validation.py`, topic-local
`pyrightconfig.json`, and this topic's gate evidence/artifacts as applicable. Do not
modify ReadOnly production, dependency, configuration, architecture, or release paths.

### Open Questions

None.
