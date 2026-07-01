> Semantic warning:
> `analysis/tests-canonical-hash-direct-import-fix/requirements.md` and
> `analysis/tests-canonical-hash-direct-import-fix/technical-spec.md` were not
> found at authoring time. This plan is authored from repo exploration and the
> explicit frozen scope only.

# tests-canonical-hash-direct-import-fix

## Goal / Outcome

- Remove dynamic module loading from
  `tests/model_registry/model_payload/test_canonical_hash.py` by replacing
  `importlib.import_module(...)` usage with normal direct Python imports.
- When this topic is complete, the three existing public-surface assertions in
  that test file keep the same verification intent, bounded validation passes,
  and the topic has the repo-visible planning artifacts needed to enter review.

## Scope

- **In scope**:
  - Create the repo-visible topic plan, step-tracking artifact, and pending
    human-check artifact for `tests-canonical-hash-direct-import-fix`.
  - Update only
    `tests/model_registry/model_payload/test_canonical_hash.py` to replace
    dynamic module loading with direct imports.
  - Run validation that is directly related to
    `tests/model_registry/model_payload/test_canonical_hash.py`.

- **Out of scope**:
  - Any other file under `tests/`.
  - Any file under `src/`.
  - Any change to `AGENTS.md`, existing governance topic artifacts, workflow
    contracts, or repo-wide import policy.
  - Any repo-wide import cleanup, test-structure reorganization, or unrelated
    refactor.

## Locked Decisions

- This topic is not a stable-library topic and does not declare release-facing
  timing. `## Stable library metadata` is intentionally absent.
- This topic adopts the Python planning extension path only for
  `*.step.md` support and frozen implementation decisions.
- D1 verdict: `trivial` — this is an isolated test-only import rewrite with no
  production-code change, no public-API change, and no new behavioral contract;
  therefore this topic does not declare `*.spec.md`, `*.red-tests.yaml`, or
  `*.implementation-review.yaml` artifacts.
- Async-planning status is locked as exempt because the topic changes only a
  synchronous test import pattern and introduces no async boundary, resource
  lifecycle, concurrency, cancellation, or timeout behavior.
- The direct-import rewrite must use normal module imports for the package
  surfaces under test instead of `importlib.import_module(...)`.
- The three existing public-surface assertions must keep their current meaning:
  `model_payload` exposes `ModelPayloadHasher`,
  `model_payload` does not expose `hash_model_payload`,
  and `model_registry` does not re-export `ModelPayloadHasher`.
- `src/async_model_gateway/model_registry/__init__.py` and
  `src/async_model_gateway/model_registry/model_payload/__init__.py` are
  read-only inspection surfaces for this topic and must not be modified.
- The plan-review artifact path is declared now, but the file is not prebuilt
  during planning because `plan-review.json` is reviewer-owned and the workflow
  contract does not define a pending-compatible verdict shape.

## Boundaries / Exclusions

- The planning actor authors only the repo-visible planning artifacts for this
  topic.
- The implementer may change only the exact test and planning artifacts listed
  in `## Artifact Paths`; any drift into other tests, source files, or
  governance surfaces returns the topic to `spec-and-plan-finalization`.
- The reviewer issues an independent repo-visible verdict and does not reuse a
  planner-authored placeholder as the review result.
- The human gate is explicit and separate from plan review; chat agreement does
  not clear this topic for `implement-plan`.
- Broader `tests/` cleanup, governance changes, or production-code rewrites
  belong to different topics.

## Status / Allowed Transitions

- **Current**: `review-ready`
- **Execution model**: follow
  `spec-and-plan-finalization -> implement-plan -> pr-comment -> pr-comment-review-pr-comments-and-fix`;
  stop at `merged` because this topic does not use the conditional `release`
  workflow.
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

- `spec-and-plan-finalization` completes only after the repo-visible topic plan
  exists, the reviewer creates
  `plan/tests-canonical-hash-direct-import-fix/tests-canonical-hash-direct-import-fix.plan-review.json`
  with an `approved` verdict, and the human-owned gate at
  `plan/tests-canonical-hash-direct-import-fix/tests-canonical-hash-direct-import-fix.human-check.json`
  explicitly clears the approved plan for `implement-plan`.
- The pending `human-check.json` artifact is precreated for this topic because
  the workflow requires explicit human-gate evidence and the repository
  already uses that pending-gate pattern.
- The reviewer-owned `plan-review.json` artifact is declared but not prebuilt
  during planning because the contract has no valid pending verdict.
- Any request to widen scope beyond the locked test file, direct validation, or
  declared planning artifacts must return to
  `spec-and-plan-finalization`.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/tests-canonical-hash-direct-import-fix/tests-canonical-hash-direct-import-fix.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Topic step tracking | `plan/tests-canonical-hash-direct-import-fix/tests-canonical-hash-direct-import-fix.step.md` | Implementer | Repo-visible implementer-progress companion artifact |
| Plan review artifact | `plan/tests-canonical-hash-direct-import-fix/tests-canonical-hash-direct-import-fix.plan-review.json` | Reviewer | Repo-visible planning gate verdict created during plan review |
| Human check gate evidence | `plan/tests-canonical-hash-direct-import-fix/tests-canonical-hash-direct-import-fix.human-check.json` | Human | Human-owned repo-visible gate evidence that clears the approved plan for `implement-plan` |
| Canonical hash test | `tests/model_registry/model_payload/test_canonical_hash.py` | Implementer | Sole implementation target for removing dynamic module loading from this topic |
| Model registry public surface | `src/async_model_gateway/model_registry/__init__.py` | Implementer | Read-only inspection surface for confirming `model_registry` does not re-export `ModelPayloadHasher` |
| Model-payload public surface | `src/async_model_gateway/model_registry/model_payload/__init__.py` | Implementer | Read-only inspection surface for confirming `model_payload` exposes `ModelPayloadHasher` directly |

Artifact path notes:

- This topic does not modify `README.md`, `VERSION`, `AGENTS.md`, workflow
  contracts, governance topic artifacts, or any file under `src/`.
- The two `src/.../__init__.py` paths above are inspection-only and must not
  be edited under this topic.
- `tests-canonical-hash-direct-import-fix.plan-review.json` is an exact
  reserved path for reviewer output; planning work declares it but does not
  pre-fill a review verdict.
- Treat listed paths as an executable contract.
- If later work needs other test files, production code changes, or governance
  edits, stop and route back through `spec-and-plan-finalization`.

## Implementation Steps

1. Update `tests/model_registry/model_payload/test_canonical_hash.py` to
   replace `from importlib import import_module` and each
   `import_module(...)` call with direct module imports while preserving the
   existing `ModelPayloadHasher` import and the same three public-surface
   assertion semantics.
2. Re-check
   `src/async_model_gateway/model_registry/__init__.py` and
   `src/async_model_gateway/model_registry/model_payload/__init__.py` as
   read-only inspection surfaces so the rewritten test continues to assert the
   intended package boundaries without modifying those source files.
3. Run `uv run ruff check tests/model_registry/model_payload/test_canonical_hash.py`
   and
   `uv run pytest tests/model_registry/model_payload/test_canonical_hash.py --cov-fail-under=0`,
   then update
   `plan/tests-canonical-hash-direct-import-fix/tests-canonical-hash-direct-import-fix.step.md`
   to reflect implementer-owned completion truthfully.

## Validation / Acceptance Checks

- Canonical topic-plan sections, status names, artifact paths, and reviewer
  handoff shape remain compatible with the repo workflow contracts.
- Stable-library intent remains explicitly absent and `Post-merge / release
  actions` continues to say no release workflow is required.
- `tests/model_registry/model_payload/test_canonical_hash.py` no longer
  imports `import_module` and no longer calls `import_module(...)`.
- The test still verifies that
  `async_model_gateway.model_registry.model_payload` exposes
  `ModelPayloadHasher`.
- The test still verifies that
  `async_model_gateway.model_registry.model_payload` does not expose
  `hash_model_payload`.
- The test still verifies that
  `async_model_gateway.model_registry` does not re-export
  `ModelPayloadHasher`.
- No file outside the declared planning artifacts and
  `tests/model_registry/model_payload/test_canonical_hash.py` is modified.
- The bounded validation commands for `ruff` and `pytest` pass against the
  declared test file.
- `tests-canonical-hash-direct-import-fix.step.md` mirrors every numbered
  implementation step as pending items and does not pre-fill implementer
  completion.
- `tests-canonical-hash-direct-import-fix.human-check.json` exists in
  `pending` state, and `implement-plan` remains blocked until both reviewer
  approval and explicit human clearance exist repo-visibly.

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
- After merge, stop; do not change README, VERSION, tags, or release state
  under this topic.

## Open Questions / Unresolved Items

- None.

## Non-goals

- This topic does not change any file under `src/`.
- This topic does not rewrite any test file other than
  `tests/model_registry/model_payload/test_canonical_hash.py`.
- This topic does not alter `ModelPayloadHasher`, `ModelRegistry`, or any
  public import surface in production code.
- This topic does not add new governance rules or reopen the existing
  governance topic.
- This topic does not expand into repo-wide import cleanup or test-structure
  refactoring.

## Current Context

- `tests/model_registry/model_payload/test_canonical_hash.py` currently
  imports `import_module` and uses it to inspect
  `async_model_gateway.model_registry.model_payload` and
  `async_model_gateway.model_registry`.
- `src/async_model_gateway/model_registry/model_payload/__init__.py` already
  re-exports `ModelPayloadHasher`, and
  `src/async_model_gateway/model_registry/__init__.py` already re-exports only
  `ModelRegistry`, so static reading shows no direct-import blocker.
- The existing governance topic records this test file as a grandfathered
  dynamic-import exception, so this follow-up topic is the bounded path that
  removes that exception from the test itself without widening scope.

## Requirements

1. `tests/model_registry/model_payload/test_canonical_hash.py` must stop using
   `importlib.import_module(...)` and use direct Python imports instead.
2. The three existing public-surface assertions must preserve their current
   meaning after the rewrite.
3. Validation must stay bounded to the directly related test file and its lint
   check.
4. No `src/` file, other `tests/` file, governance artifact, or workflow
   contract file may be modified.
5. Repo-visible planning artifacts for this topic must exist and leave the
   topic ready for plan review rather than implementation.

## Decisions

- D1 verdict: `trivial` — isolated test-only import rewrite with no production
  behavior change.
- Async-planning status: exempt — cite exemption evidence: the topic changes
  only synchronous test imports and validation commands, with no async
  boundary, lifecycle, timeout, concurrency, or cancellation risk.
- Module/package placement:
  `tests/model_registry/model_payload/test_canonical_hash.py` is the only code
  file that receives implementation changes; planning artifacts live under
  `plan/tests-canonical-hash-direct-import-fix/`.
- New public API: no.
- Interface changes: no — test intent stays the same; only the import style
  inside the test changes.
- Breaking changes allowed: no — the topic must not change production behavior
  or public package surfaces.
- New dependencies: no.
- Error handling strategy: preserve the existing pytest-based assertions and
  failure surfaces; do not add new exception translation or helper wrappers.
- Typing strategy: keep the existing typed test style and do not introduce new
  `Any`, protocol, or runtime abstraction layers.

## Public Contract / API Changes

- No public API changes.
- This topic only rewrites how the test imports the already-existing package
  surfaces that it inspects.

## Affected Files / Modules

Likely affected files:
- `tests/model_registry/model_payload/test_canonical_hash.py`
- `plan/tests-canonical-hash-direct-import-fix/tests-canonical-hash-direct-import-fix.step.md`

Candidate files to inspect:
- `src/async_model_gateway/model_registry/__init__.py`
- `src/async_model_gateway/model_registry/model_payload/__init__.py`

## Test Plan

Test file: `tests/model_registry/model_payload/test_canonical_hash.py`

Test cases:
- Happy path: direct module imports still allow the test to confirm
  `model_payload` exposes `ModelPayloadHasher`.
- Invalid input: the existing invalid top-level payload parametrized cases keep
  raising `TypeError`.
- Edge case: empty-payload golden digest and empty nested container hashing
  remain unchanged.
- Regression: direct imports still prove that `model_registry` does not
  re-export `ModelPayloadHasher`.
- Backward compatibility: dict-order-insensitive hashing, list-order
  sensitivity, and scalar distinction assertions remain unchanged.

## Risks

- A careless rewrite could accidentally turn package-surface checks into simple
  imported-name checks, weakening the original assertion intent.
- Importing the wrong module alias could mask a re-export problem and make the
  test look green for the wrong reason.

## Rollback Plan

- Revert via git:
  `tests/model_registry/model_payload/test_canonical_hash.py`,
  `plan/tests-canonical-hash-direct-import-fix/tests-canonical-hash-direct-import-fix.plan.md`,
  `plan/tests-canonical-hash-direct-import-fix/tests-canonical-hash-direct-import-fix.step.md`,
  and
  `plan/tests-canonical-hash-direct-import-fix/tests-canonical-hash-direct-import-fix.human-check.json`.
