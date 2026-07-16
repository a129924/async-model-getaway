> Semantic warning — analysis layer INCOMPLETE: `analysis/runtime-model-runtime-generic-erasure/requirements.md` and `analysis/runtime-model-runtime-generic-erasure/technical-spec.md` are both absent. This plan uses the human-approved generic-erasure contract; the missing optional analysis layer must not broaden scope.

# runtime-model-runtime-generic-erasure

## Goal / Outcome

Make `LoadedRuntimeModel` a covariant generic runtime boundary, preserving the provider runtime type only at its private local seam while keeping all current local acquisition APIs explicitly type-erased as `LoadedRuntimeModel[object]`.

## Scope

### In-Scope

- Genericise `LoadedRuntimeModel`, `_LocalLoadedRuntimeModel`, and `_create_loaded_runtime_model` with one covariant `RuntimeT`.
- Annotate `ModelPool.acquire()`, `LocalModelLoader.load()`, `_load_pickle()`, `_load_torch()`, and `_load_onnx()` as returning `LoadedRuntimeModel[object]`.
- Add the declared runtime-model, pool, static typecheck, RED, implementation-review, and code-review artifacts and gates.
- Preserve existing local dispatch, no-I/O, validation, direct-await, error, failure, and cancellation behavior.

### Out-Of-Scope

- Genericising `ModelArtifact`, `LoaderFamily`, or another shared read contract.
- Artifact I/O, `ModelExecution`, provider adapters or frameworks, remote acquisition, cache, lifecycle, timeout, retry, or background-task behavior.
- New public provider-runtime access or new package-root exports.
- README, architecture documentation, version metadata, dependency metadata, lockfile, release, tag, or publication changes.
- Rewriting v0.5.0 historical planning, review, or release evidence.

## Locked Decisions

- `RuntimeT = TypeVar("RuntimeT", covariant=True)` is defined only in `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py`; it is not exported from any package root.
- The public abstract contract is `class LoadedRuntimeModel(ABC, Generic[RuntimeT])` with readonly `loader_family: LoaderFamily` and `_provider_runtime(self) -> RuntimeT` as the non-public internal handoff.
- `_LocalLoadedRuntimeModel(LoadedRuntimeModel[RuntimeT])` stores `provider_model: RuntimeT`; `_create_loaded_runtime_model(..., provider_model: RuntimeT) -> LoadedRuntimeModel[RuntimeT]` retains that precision.
- `ModelPool.acquire(artifact: ModelArtifact) -> LoadedRuntimeModel[object]`, `LocalModelLoader.load(...) -> LoadedRuntimeModel[object]`, and all three private family handlers return `LoadedRuntimeModel[object]`.
- `ModelArtifact` and `LoaderFamily` remain non-generic and cannot become runtime typing authorities. Third-party framework types do not enter the public acquisition surface.
- The `runtime_model` package root continues to export only `LoadedRuntimeModel`; private implementation, factory, and `RuntimeT` stay private.
- This is D1 `non-trivial`, but async-planning is exempt because it corrects annotations only and leaves existing async boundaries, direct await, I/O, resource ownership, concurrency, failure, cancellation, timeout, and retry policy unchanged.
- Stable-library intent is merge-only with no release: static typing and annotation introspection may change, but runtime behavior does not.
- All topic planning and evidence artifacts are new; v0.5.0 artifacts retain historical truth and are not edited.

## Boundaries / Exclusions

- Plan-Creator owns only the initial plan/spec/step artifacts; it does not approve them or edit source, tests, configuration, or gate evidence.
- Plan-Reviewer owns only the plan-review verdict. Human owns the explicit `human-check` and `human merge` gates.
- Tester is the first `implement-plan` subphase and owns fresh RED tests, the static fixture, topic-local Pyright configuration, and RED evidence; Tester does not modify production source.
- Implementer changes only the declared three production source files, updates real step progress, and does not rewrite tests or gate artifacts to fit an implementation.
- Independent implementation review and code review are required before PR routing. Any scope, path, public contract, runtime behavior, or release-intent drift returns to `spec-and-plan-finalization`.
- `ModelExecution`, remote runtime acquisition, lifecycle ownership, and provider framework adaptation belong to later topics.

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: `spec-and-plan-finalization` -> `implement-plan` -> `pr-comment` -> `pr-comment-review-pr-comments-and-fix`; this topic stops at `merged` and never enters `release`.
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
- Fresh plan review with `approved` verdict and a fresh Human `human-check.json` containing `cleared_for: implement-plan` are required before Tester may start RED authoring. Chat approval is not a gate.

## Artifact Paths

### Written

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/runtime-model-runtime-generic-erasure/runtime-model-runtime-generic-erasure.plan.md` | Plan-Creator | Repo-visible implementation contract |
| Python specification | `plan/runtime-model-runtime-generic-erasure/runtime-model-runtime-generic-erasure.spec.md` | Plan-Creator | D1 non-trivial behavioral/type contract |
| Step tracker | `plan/runtime-model-runtime-generic-erasure/runtime-model-runtime-generic-erasure.step.md` | Plan-Creator, then Implementer | Workflow state and actual implementation progress |
| Plan review | `plan/runtime-model-runtime-generic-erasure/runtime-model-runtime-generic-erasure.plan-review.json` | Plan-Reviewer | Fresh planning verdict |
| Human check | `plan/runtime-model-runtime-generic-erasure/runtime-model-runtime-generic-erasure.human-check.json` | Human | Explicit implementation clearance |
| RED evidence | `plan/runtime-model-runtime-generic-erasure/runtime-model-runtime-generic-erasure.red-tests.yaml` | Tester | Fresh pytest and Pyright RED evidence |
| Topic Pyright configuration | `plan/runtime-model-runtime-generic-erasure/pyrightconfig.json` | Tester | Strict routing for the static fixture |
| Runtime-model tests | `tests/model_runtime/runtime_model/test_loaded_runtime_model.py` | Tester | Generic internal runtime seam regression coverage |
| Runtime-model package-surface tests | `tests/model_runtime/runtime_model/test_runtime_model_package_surface.py` | Tester | Export-boundary regression coverage |
| Pool behavior tests | `tests/model_runtime/model_pool/test_model_pool.py` | Tester | Acquisition, validation, failure, and cancellation coverage |
| Local loader tests | `tests/model_runtime/model_pool/test_local_model_loader.py` | Tester | Exact erased annotations, dispatch, and no-I/O coverage |
| Pool package-surface tests | `tests/model_runtime/model_pool/test_model_pool_package_surface.py` | Tester | Public annotation introspection coverage |
| Static typing fixture | `tests/typecheck/runtime_model_generic_erasure.py` | Tester | Precision, covariance, and erasure assertions |
| Runtime model source | `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py` | Implementer | Generic ABC, private local model, and factory |
| Pool source | `src/async_model_gateway/model_runtime/model_pool/pool.py` | Implementer | Erased public pool return annotation |
| Local loader source | `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` | Implementer | Erased loader and handler return annotations |
| Implementation review | `plan/runtime-model-runtime-generic-erasure/runtime-model-runtime-generic-erasure.implementation-review.yaml` | Reviewer | Plan-conformance verdict |
| Code review | `plan/runtime-model-runtime-generic-erasure/runtime-model-runtime-generic-erasure.code-review.yaml` | Reviewer | Quality and boundary verdict |

### ReadOnly

- `README.md`, `docs/architecture.md`, `pyproject.toml`, `uv.lock`, and `src/async_model_gateway/__version__.py`.
- `src/async_model_gateway/model_runtime/runtime_model/__init__.py`, `src/async_model_gateway/model_runtime/model_pool/__init__.py`, `src/async_model_gateway/model_runtime/__init__.py`, and `src/async_model_gateway/__init__.py`.
- `src/async_model_gateway/model_runtime/model_artifact/__init__.py`, `src/async_model_gateway/model_runtime/model_artifact/artifact.py`, and `src/async_model_gateway/model_runtime/model_artifact/loader_family.py`.
- Every artifact under `plan/runtime-model-minimal-consumption-contract/`.

### Deleted

None. This topic deletes no source, test, planning, metadata, documentation, or historical file.

Any required path outside Written, or any change to ReadOnly, returns to `spec-and-plan-finalization`.

## Stable library metadata

- `README row`: no change.
- `VERSION bump`: no bump; version metadata remains `0.5.0`.
- `timing`: merge-only; no `release` phase.
- `rationale`: this is a bounded static typing correction with no changed runtime behavior or published release intent.
- Release notes, tag, package publication, and lockfile changes: none.

## Implementation Steps

1. Tester updates the five declared runtime-model/model-pool test files, adds `tests/typecheck/runtime_model_generic_erasure.py` and the topic-local `pyrightconfig.json`, then records fresh focused pytest and dedicated Pyright RED evidence in `runtime-model-runtime-generic-erasure.red-tests.yaml` before production source changes.
2. Implementer changes `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py` to define covariant `RuntimeT`, genericise the ABC and private local implementation, and make the private factory preserve `RuntimeT` without exporting private symbols.
3. Implementer changes `src/async_model_gateway/model_runtime/model_pool/pool.py` only to make `ModelPool.acquire()` return `LoadedRuntimeModel[object]`, retaining its validation, retained loader, and direct-await behavior.
4. Implementer changes `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` only to make `load()` and `_load_pickle()`, `_load_torch()`, and `_load_onnx()` return `LoadedRuntimeModel[object]`, retaining explicit dispatch, `assert_never`, no-I/O, and propagation behavior.
5. Implementer runs the declared validation commands, confirms focused RED is GREEN, confirms ReadOnly and historical paths have no diff, and marks only actually completed entries in `runtime-model-runtime-generic-erasure.step.md`.

## Validation / Acceptance Checks

- `LoadedRuntimeModel` accepts a covariant generic parameter, private factory and `_provider_runtime()` preserve `RuntimeT`, and provider identity is unchanged.
- Pool, loader, and three family handlers have exact `LoadedRuntimeModel[object]` return annotations; no public acquisition API leaks a provider type.
- `ModelArtifact` and `LoaderFamily` remain non-generic; `RuntimeT`, private factory, and private implementation are not package-root exports.
- Static fixture uses only static imports and `typing_extensions.assert_type`; private diagnostics are line-local only, with no file-wide `reportPrivateUsage` disable or dynamic module loading.
- Existing explicit family dispatch, `assert_never`, path independence, retained loader, no-I/O `NotImplementedError`, validation exceptions, generic failure, and `CancelledError` propagation remain covered.
- Dedicated Pyright receives its positional fixture path and reports nonzero source analysis, preventing a zero-source false green.
- Fresh plan review, Human check, RED evidence, implementation review, and code review exist at their declared paths before PR routing. ReadOnly and Deleted contracts remain satisfied.

## Reviewer Handoff

```json
{
  "verdict": "approved | needs-rework",
  "blocking_issues": [
    {
      "issue": "string",
      "file": "string",
      "fix": "string"
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

No release workflow required. Human merge ends this topic at `merged`; do not modify README, version, lockfile, release notes, tags, or package publication state.

## Open Questions / Unresolved Items

None.

# Python Implementation Plan Extension

## Goal

Introduce the generic internal runtime seam and explicit local acquisition erasure without changing runtime behavior.

## Non-goals

- Do not genericise `ModelArtifact`, `LoaderFamily`, or shared read contracts.
- Do not add I/O, execution, provider adapters, lifecycle, cache, remote acquisition, timeout, retry, or concurrency semantics.
- Do not add package-root exports or public provider-runtime access.
- Do not modify stable metadata, documentation, historical artifacts, or release state.

## Current Context

`loaded_runtime_model.py` currently supplies a non-generic abstract consumption contract plus a private local implementation and factory. `pool.py` and `_local_model_loader.py` already expose an async local acquisition boundary with direct await and explicit family dispatch. The existing public runtime semantic is readonly `loader_family`; provider runtime is private to the local seam.

## Requirements

1. `LoadedRuntimeModel[RuntimeT]`, `_LocalLoadedRuntimeModel[RuntimeT]`, and the private factory retain an exact covariant `RuntimeT` internally.
2. `ModelPool.acquire()`, `LocalModelLoader.load()`, and the three family handlers are annotated exactly as `LoadedRuntimeModel[object]`.
3. `RuntimeT`, private local implementation, and private factory remain unexported; `ModelArtifact` and `LoaderFamily` remain non-generic.
4. Strict static checking demonstrates internal precision, covariance, and public erasure with real fixture analysis.
5. Existing runtime behavior and failure/cancellation semantics stay unchanged.

## Decisions

- Async-planning status: exempt — cite exemption evidence: this is a typing-only correction; existing async `acquire()` boundaries, direct await, I/O absence, resource lifecycle, concurrency, failure propagation, cancellation propagation, timeout, and retry policy do not change.
- Module/package placement: generic runtime contract changes live in `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py`; erased acquisition annotations live only in `src/async_model_gateway/model_runtime/model_pool/pool.py` and `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`.
- New public API: yes — the existing public class becomes `LoadedRuntimeModel[RuntimeT]`; no new package-root name or callable API is added.
- Interface changes: yes — the abstract class gains covariant generic typing and specified acquisition annotations become `LoadedRuntimeModel[object]`.
- Breaking changes allowed: yes — static typing and annotation introspection correction only; runtime call behavior remains compatible.
- New dependencies: no.
- Error handling strategy: preserve current `TypeError`, `ValueError`, `NotImplementedError`, generic failure, and `CancelledError` behavior without translation.
- Typing strategy: strict types, no `Any`, one covariant `TypeVar`, private precision/public erasure, static imports, and only line-local private-use ignores in the dedicated fixture.

## Public Contract / API Changes

`LoadedRuntimeModel` becomes `LoadedRuntimeModel[RuntimeT]`; its only public semantic remains `loader_family`. `_provider_runtime() -> RuntimeT` stays non-public. `ModelPool.acquire(artifact: ModelArtifact) -> LoadedRuntimeModel[object]` is the public acquisition contract. Loader and handler annotation changes are private. Runtime behavior and exception behavior are unchanged.

## Affected Files / Modules

Likely affected files:

- `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py`
- `src/async_model_gateway/model_runtime/model_pool/pool.py`
- `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py`
- The seven declared test/typecheck/config paths in the Written table.

Candidate files to inspect:

- `src/async_model_gateway/model_runtime/runtime_model/__init__.py`
- `src/async_model_gateway/model_runtime/model_artifact/artifact.py`
- `src/async_model_gateway/model_runtime/model_artifact/loader_family.py`

## Implementation Steps

1. Tester updates the five declared runtime-model/model-pool test files, adds `tests/typecheck/runtime_model_generic_erasure.py` and the topic-local `pyrightconfig.json`, then records fresh focused pytest and dedicated Pyright RED evidence in `runtime-model-runtime-generic-erasure.red-tests.yaml` before production source changes.
2. Implementer changes `src/async_model_gateway/model_runtime/runtime_model/loaded_runtime_model.py` to define covariant `RuntimeT`, genericise the ABC and private local implementation, and make the private factory preserve `RuntimeT` without exporting private symbols.
3. Implementer changes `src/async_model_gateway/model_runtime/model_pool/pool.py` only to make `ModelPool.acquire()` return `LoadedRuntimeModel[object]`, retaining its validation, retained loader, and direct-await behavior.
4. Implementer changes `src/async_model_gateway/model_runtime/model_pool/_local_model_loader.py` only to make `load()` and `_load_pickle()`, `_load_torch()`, and `_load_onnx()` return `LoadedRuntimeModel[object]`, retaining explicit dispatch, `assert_never`, no-I/O, and propagation behavior.
5. Implementer runs the declared validation commands, confirms focused RED is GREEN, confirms ReadOnly and historical paths have no diff, and marks only actually completed entries in `runtime-model-runtime-generic-erasure.step.md`.

## Test Plan

Test files: `tests/model_runtime/runtime_model/test_loaded_runtime_model.py`, `tests/model_runtime/runtime_model/test_runtime_model_package_surface.py`, `tests/model_runtime/model_pool/test_model_pool.py`, `tests/model_runtime/model_pool/test_local_model_loader.py`, `tests/model_runtime/model_pool/test_model_pool_package_surface.py`, and `tests/typecheck/runtime_model_generic_erasure.py`.

- Happy path: factory preserves provider identity and its precise inferred runtime type.
- Invalid input: abstract construction, invalid acquisition, and artifact validation errors remain unchanged.
- Edge case: covariance and runtime subscription work; artifact and loader-family contracts remain non-generic; private symbols remain unexported.
- Regression: exact erased annotations, explicit dispatch, path independence, `assert_never`, retained loader, no-I/O, generic failure, and `CancelledError` behavior remain covered.
- Backward compatibility: `loader_family` is the same readonly public semantic and no public instance surface is added.

## Validation Commands

```bash
uv run pytest --no-cov tests/model_runtime/runtime_model tests/model_runtime/model_pool -v
uv run pyright --project plan/runtime-model-runtime-generic-erasure/pyrightconfig.json tests/typecheck/runtime_model_generic_erasure.py
uv run pytest -v
uv run ruff check src tests plan/runtime-model-runtime-generic-erasure
uv run pyright
uv lock --check
git diff --check
```

## Risks

- Factory typing could be erased too early, making the private runtime handoff imprecise.
- A public acquisition annotation could leak a provider type or remain a bare generic.
- The Pyright command could pass without analysing the fixture if config/path routing drifts.
- Annotation edits could accidentally change existing dispatch or propagation behavior.

## Rollback Plan

Before merge, revert the three declared production files, the declared test/typecheck/config paths, and this topic's planning/evidence artifacts. Do not alter ReadOnly or historical artifacts. After merge, use a new correction topic rather than rewriting prior evidence.

## Open Questions

None.
