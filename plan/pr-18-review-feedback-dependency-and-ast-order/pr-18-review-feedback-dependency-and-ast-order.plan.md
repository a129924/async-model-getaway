> Semantic warning: `analysis/pr-18-review-feedback-dependency-and-ast-order/requirements.md`
> 與 `analysis/pr-18-review-feedback-dependency-and-ast-order/technical-spec.md` 均不存在。
> 本 plan 依 PR #18 的兩個明確 review threads 與 Human 已鎖定 decisions 撰寫；不得
> 擴張為 runtime、API、architecture、documentation 或其他 PR feedback work。

# pr-18-review-feedback-dependency-and-ast-order

## Goal / Outcome

在正常 dev environment 中提供既有 ONNX Runtime test dependency，讓 CI 回復 plain
frozen dev sync，並使 `_provider_runtime_call_paths()` 的 AST scan 回傳順序可重現，以
完成 PR #18 的兩個指定 review threads。

## Scope

### In scope

- 處理 PR #18 thread
  [`discussion_r3629182514`](https://github.com/a129924/async-model-getaway/pull/18#discussion_r3629182514)：
  保留 published `[project.optional-dependencies].onnx` 的既有
  `onnxruntime>=1.22.0,<1.22.1` constraint，並將同一 constraint 加入 dev group。
- 更新 `uv.lock`，使 direct dev-group dependency metadata 與 `pyproject.toml` 一致，
  不升級或變更既有 resolved package versions。
- 將 `.github/workflows/ci.yml` 的 `Sync dependencies` command 回復為
  `uv sync --frozen --group dev`；CI 不再以 `--extra onnx` 補足 test dependency。
- 處理 PR #18 thread
  [`discussion_r3629184495`](https://github.com/a129924/async-model-getaway/pull/18#discussion_r3629184495)：
  僅在 `_provider_runtime_call_paths()` AST helper 對 collected `Path` values 做
  deterministic sort。
- 完成此 topic 的 plan/step，並在 implementation 前取得 fresh plan-review 與 Human
  `cleared_for: implement-plan` gate。

### Out of scope

- `onnxruntime` optional-extra constraint 的移除、版本變更、移至 `[project.dependencies]`
  或新增其他 dependency。
- 任何 runtime source、public API、`ModelExecution` behavior、ONNX acquisition、async
  semantics、package export 或 architecture 變更。
- README、architecture/spec documentation、release/version、CI trigger/action/Python
  version/其他 validation command 的修改。
- 新增或重設 test scenario；只修正既有 AST helper 的 deterministic return ordering。
- 在 PR #18 reply、resolve、re-request review、commit、push、open/update PR；這些動作
  需要 implementation/review gates 完成後的另一個 explicit Human permission。

## Locked Decisions

- D1 verdict: `trivial`。這是 existing dependency placement 與 existing test helper
  ordering 的 bounded review-feedback repair；不建立 `*.spec.md` 或 fresh RED artifact。
- `onnxruntime>=1.22.0,<1.22.1` 保留在 published `onnx` optional extra，並以完全相同
  constraint 同時列入 `[dependency-groups].dev`。
- CI 的唯一 allowed change 是 `Sync dependencies` 回復為
  `uv sync --frozen --group dev`；不得保留或新增 `--extra onnx`，不得改其他 CI line。
- AST deterministic repair 只發生於
  `tests/model_runtime/model_execution/test_model_execution_package_surface.py` 的
  `_provider_runtime_call_paths()`；在 return 前排序 collected relative `Path` list，
  不改 scan predicate、assertion target 或 production source。
- 無 public API、interface、runtime behavior、error handling、typing contract 或 async
  behavior change；stable-library intent 與 release intent 均明確缺席。
- Fresh Plan-Reviewer `approved` verdict 與 Human `cleared_for: implement-plan` 是
  implementation 前的必要 gates。PR reply/resolve 不是 implementation authorization 的
  一部分，必須另有 explicit Human permission。

## Boundaries / Exclusions

- Plan-Creator 只建立/更新 plan 與 step；Plan-Reviewer、Human、Implementer、Reviewer
  分別只更新其 own gate、implementation 或 review artifacts。
- Implementer writable implementation paths 僅限 `pyproject.toml`、`uv.lock`、
  `.github/workflows/ci.yml`、
  `tests/model_runtime/model_execution/test_model_execution_package_surface.py`。
- 所有未列 Artifact Path 的 source、test、docs、CI、planning artifact 與 PR state
  都是 ReadOnly；需要額外 path 或 contract change 時回到
  `spec-and-plan-finalization`。
- 不得以 CI-only extra、lazy-import suppression、test skip 或 order-insensitive assertion
  來迴避兩個 review findings。

## Status / Allowed Transitions

- **Current**: `review-ready`；plan/step 已建立，等待 fresh independent Plan-Reviewer
  verdict。
- **Execution model**: `spec-and-plan-finalization -> implement-plan -> pr-comment ->
  pr-comment-review-pr-comments-and-fix`；本 topic 在 `merged` 停止，沒有 `release`
  workflow。
- **Allowed transitions**:
  - `review-ready` -> `reviewer-in-progress`
  - `reviewer-in-progress` -> `approved`
  - `reviewer-in-progress` -> `needs-rework`
  - `needs-rework` -> `creator-in-progress`
  - `approved` -> `publish-in-progress`
  - `publish-in-progress` -> `pr-open`
  - `pr-open` -> `needs-rework`
  - `pr-open` -> `merged`

Routing notes:

- Human must record `cleared_for: implement-plan` only after the declared plan-review
  artifact records `approved`.
- D1 is trivial: no fresh spec or RED artifact is required. The first implementation
  step updates the existing test helper before dependency/CI edits.
- PR reply/resolve is deferred beyond code review and requires separate Human permission;
  this plan does not infer that authorization from the implementation gates.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.plan.md` | Plan-Creator | Repo-visible execution contract |
| Step tracker | `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.step.md` | Plan-Creator, then phase owner | Workflow and implementation progress |
| Plan review | `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.plan-review.json` | Plan-Reviewer | Fresh independent planning verdict |
| Human check | `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.human-check.json` | Human | Explicit `cleared_for: implement-plan` gate |
| Implementation review | `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.implementation-review.yaml` | Reviewer | Bounded plan-conformance verdict |
| Code review | `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.code-review.yaml` | Reviewer | Independent quality/boundary verdict |
| Project dependency declaration | `pyproject.toml` | Implementer | Keep published extra; add same ONNX Runtime constraint to dev group |
| Resolved dependency metadata | `uv.lock` | Implementer | Lock direct dev-group dependency placement without package-version drift |
| CI workflow | `.github/workflows/ci.yml` | Implementer | Plain frozen dev sync only |
| AST ownership test | `tests/model_runtime/model_execution/test_model_execution_package_surface.py` | Implementer | Deterministic sort only in `_provider_runtime_call_paths()` |

### ReadOnly

- All paths not declared above, including `src/`, README, `docs/`, other tests, other
  topic artifacts, PR state, and all other CI workflow lines.

### Written

- This topic's plan and step are created by Plan-Creator. Future plan-review,
  human-check, implementation-review, and code-review artifacts are written only by
  their declared owners.

### Updated

- Only the four Implementer-owned implementation paths declared above may change after
  the two implementation gates pass.

### Deleted

- None. Any deleted path or removed dependency is scope drift.

## Implementation Steps

1. In `tests/model_runtime/model_execution/test_model_execution_package_surface.py`,
   update `_provider_runtime_call_paths()` to return the collected relative `Path`
   values in deterministic sorted order; retain the existing AST traversal, predicate,
   type annotation, and expected sole execution-path assertion.
2. In `pyproject.toml`, retain `onnxruntime>=1.22.0,<1.22.1` in the published `onnx`
   optional extra and add that identical constraint to `[dependency-groups].dev`; update
   `uv.lock` with the normal uv lock workflow without unrelated resolution drift.
3. In `.github/workflows/ci.yml`, change only `Sync dependencies` to
   `uv sync --frozen --group dev`; leave workflow trigger, action pins, Python version,
   and all existing validation commands byte-for-byte unchanged.
4. Run the declared normal-dev validation sequence, inspect the four implementation
   diffs for scope/order/constraint correctness, update actual step evidence, and hand
   off to independent implementation review. Do not reply to or resolve either PR
   thread.

## Validation / Acceptance Checks

- `pyproject.toml` retains the exact `onnxruntime>=1.22.0,<1.22.1` published optional
  extra and declares the same exact constraint in dev.
- `uv.lock` represents that dev-group placement without unrelated package-version or
  dependency changes.
- CI `Sync dependencies` is exactly `uv sync --frozen --group dev`; no other workflow
  line changes.
- A clean normal dev sync supports `import onnxruntime` without `--extra onnx`.
- `_provider_runtime_call_paths()` returns deterministically sorted relative `Path`
  values while preserving the single expected production handoff caller.
- The only implementation diffs are the four declared paths; no runtime/API/docs/source
  change and no PR reply/resolve is performed.
- Run:

```bash
uv lock --check
uv sync --frozen --group dev
uv run --no-sync python -c "import onnxruntime"
uv run --no-sync pyright
uv run --no-sync pytest --no-cov tests/model_runtime/model_execution/test_model_execution_package_surface.py -v
uv run --no-sync pytest -v
uv run --no-sync ruff check src tests
uv run --no-sync pre-commit run --all-files
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

No release workflow required. After merge, stop. PR #18 reply/resolve may occur only
after a separate explicit Human permission; it is not an automatic post-merge action.

## Open Questions / Unresolved Items

None. The two bound threads and all implementation decisions are explicit.

## Python Implementation

### Goal

Resolve the two bounded PR #18 findings without changing Python runtime behavior or any
public contract.

### Non-goals

- No production Python source or public API modification.
- No new dependency/version, optional-extra removal, lockfile-wide refresh, or CI policy
  change.
- No new test scenario, dynamic module loading, or assertion semantic change.
- No README/docs/architecture/release/PR reply or resolve action.

### Current Context

- `pyproject.toml` publishes `onnxruntime>=1.22.0,<1.22.1` through the `onnx` optional
  extra, while the dev group has the ONNX model fixture but not ONNX Runtime.
- `.github/workflows/ci.yml` currently compensates with `--extra onnx` on frozen dev
  sync.
- `_provider_runtime_call_paths()` appends results from `Path.rglob("*.py")` without
  sorting, so list equality can vary by filesystem traversal order.

### Requirements

1. Normal `uv sync --frozen --group dev` installs an importable ONNX Runtime.
2. The published `onnx` extra remains a supported independent installation surface with
   its exact existing ONNX Runtime constraint.
3. CI sync does not request an optional extra.
4. The AST helper order is deterministic and its ownership assertion stays unchanged.
5. All declared normal-dev, focused, full, static, lint, pre-commit, and diff checks
   pass.

### Decisions

- Async-planning status: exempt — cite exemption evidence: this topic changes dependency
  metadata, one CI sync flag, and deterministic ordering in a test helper; it introduces
  no async boundary, lifecycle, concurrency, failure, cancellation, or timeout policy.
- Module/package placement: `pyproject.toml`, `uv.lock`, `.github/workflows/ci.yml`,
  and the existing AST helper test only; no package module receives code.
- New public API: no.
- Interface changes: no.
- Breaking changes allowed: no; the published optional extra remains intact and normal
  dev setup becomes complete for existing tests.
- New dependencies: no new package or version; the existing ONNX Runtime constraint is
  additionally declared in the dev group.
- Error handling strategy: no runtime error path changes; uv resolution/import failures
  remain command failures and existing test assertions remain unchanged.
- Typing strategy: retain `list[Path]` and `Path` values; use the standard deterministic
  sort without `Any`, casts, or suppression.

### Public Contract / API Changes

No public API changes. The published `onnx` optional extra remains available with the
same ONNX Runtime constraint; dev installation metadata only gains the same existing
test-runtime dependency.

### Affected Files / Modules

Likely affected files:

- `pyproject.toml`
- `uv.lock`
- `.github/workflows/ci.yml`
- `tests/model_runtime/model_execution/test_model_execution_package_surface.py`

Candidate files to inspect:

- `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.plan.md`
- `plan/pr-18-review-feedback-dependency-and-ast-order/pr-18-review-feedback-dependency-and-ast-order.step.md`

### Implementation Steps

1. Make the deterministic AST-helper sort in the declared package-surface test.
2. Add the existing ONNX Runtime constraint to dev, regenerate only required lock
   metadata, and restore plain frozen dev sync in CI.
3. Run normal-dev validation and inspect scope before independent review; do not take PR
   thread actions.

### Test Plan

Test file: `tests/model_runtime/model_execution/test_model_execution_package_surface.py`

Test cases:

- Happy path: normal dev sync imports `onnxruntime` and the focused package-surface test
  passes.
- Invalid input: no new input handling is introduced; the existing AST predicate remains
  unchanged for non-handoff calls.
- Edge case: filesystem-dependent `rglob` order cannot change the helper's returned
  list order after sorting.
- Regression: full pytest preserves ONNX acquisition and `ModelExecution` coverage under
  plain dev sync.
- Backward compatibility: the published `onnx` extra and its exact constraint remain
  unchanged, with no public API or runtime source diff.

### Validation Commands

```bash
uv lock --check
uv sync --frozen --group dev
uv run --no-sync python -c "import onnxruntime"
uv run --no-sync pyright
uv run --no-sync pytest --no-cov tests/model_runtime/model_execution/test_model_execution_package_surface.py -v
uv run --no-sync pytest -v
uv run --no-sync ruff check src tests
uv run --no-sync pre-commit run --all-files
git diff --check
```

### Risks

- Adding a non-identical dev constraint could create resolver drift or silently change
  published optional-extra behavior.
- Editing more than the CI sync line could alter CI policy instead of addressing the
  dependency placement finding.
- Sorting a different collection or changing the AST predicate could weaken ownership
  governance rather than only remove filesystem-order nondeterminism.

### Rollback Plan

Revert via git only `pyproject.toml`, `uv.lock`, `.github/workflows/ci.yml`, and
`tests/model_runtime/model_execution/test_model_execution_package_surface.py`. Do not
alter PR thread state as part of rollback.

### Open Questions

None.
