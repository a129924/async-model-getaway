> Semantic warning: `analysis/cli-version-smoke-test/requirements.md` and
> `analysis/cli-version-smoke-test/technical-spec.md` were not found at
> authoring time. This plan is authored from repo exploration and the explicit
> topic request only.

# cli-version-smoke-test

## Goal / Outcome

- Define a bounded Python implementation topic that gives the existing
  `async-model-gateway` CLI a stable, testable version surface without
  broadening the CLI beyond a small smoke-test feature.
- Use this topic to validate that the current workflow baseline can carry a real
  Python topic through plan review, TDD, step tracking, implementation review,
  and later PR routing.

## Scope

- **In scope**:
  - Add a bounded plan for a CLI version surface on the existing
    `async-model-gateway` package entrypoint.
  - Keep the planned implementation inside
    `src/async_model_gateway/__init__.py` and
    `tests/test_package_entrypoint.py`.
  - Declare repo-visible companion artifacts for plan review, TDD,
    implementation progress, and implementation review.

- **Out of scope**:
  - Any new CLI command tree, subcommand framework, or general argument parser
    expansion.
  - README, VERSION, release, or stable-library publication work.
  - Any source or test implementation outside the bounded entrypoint module and
    its smoke-test file.

## Locked Decisions

- This topic is not a stable-library topic and does not declare release-facing
  timing. `## Stable library metadata` is intentionally absent.
- This topic explicitly adopts the Python planning extension path.
- TDD is required. RED test authoring is the first mandatory Python subphase
  inside `implement-plan`.
- D1 verdict: `non-trivial` — this topic adds new observable CLI behavior,
  introduces a package-level version surface, changes the callable contract of
  the existing entrypoint, and requires companion spec / step / review artifacts
  to validate the baseline handoff path.
- The implementation stays in the existing package entrypoint module instead of
  introducing a new source module for this smoke test.
- The planned version source is a single package-local Python source of truth in
  `src/async_model_gateway/__init__.py`; runtime behavior must not depend on
  parsing `pyproject.toml`.
- The default scaffold output remains stable for no-argument execution.
- The version surface is activated only by explicit version flags on the
  existing entrypoint.

## Boundaries / Exclusions

- The planning actor only authors repo-visible planning artifacts for this
  topic.
- The implementer may only change the exact source and test paths declared in
  `## Artifact Paths`; drift outside those paths returns the topic to
  `spec-and-plan-finalization`.
- The reviewer validates contract adherence and bounded evidence only; the
  reviewer does not rewrite plan or implementation files.
- Packaging metadata centralization, release automation, or broader CLI UX
  improvements belong in later topics.

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

- `approved` requires both the repo-visible plan-review artifact with an
  `approved` verdict and an explicit repo-visible `human check`.
- This topic uses the Python extension path. During `implement-plan`,
  RED test authoring must complete before production-code edits.
- This topic declares `*.step.md`, `*.spec.md`, `*.red-tests.yaml`, and
  `*.implementation-review.yaml` as companion artifacts for later workflow
  phases; they do not count as approval by themselves until the declared gates
  are satisfied.
- Any scope change to version sourcing, artifact paths, or CLI behavior beyond
  the declared flags returns to `spec-and-plan-finalization`.

## Artifact Paths

| Artifact | Path | Owner | Role |
| --- | --- | --- | --- |
| Topic plan | `plan/cli-version-smoke-test/cli-version-smoke-test.plan.md` | Planning actor | Repo-visible execution contract for this topic |
| Topic step tracking | `plan/cli-version-smoke-test/cli-version-smoke-test.step.md` | Planning actor | Repo-visible implementation-progress companion artifact |
| Topic behavior spec | `plan/cli-version-smoke-test/cli-version-smoke-test.spec.md` | Planning actor | Non-trivial Python behavior contract for TDD and later review |
| Plan review artifact | `plan/cli-version-smoke-test/cli-version-smoke-test.plan-review.json` | Reviewer | Repo-visible planning gate verdict |
| RED test artifact | `plan/cli-version-smoke-test/cli-version-smoke-test.red-tests.yaml` | Implementer | Repo-visible TDD gate evidence produced during `implement-plan` |
| Implementation review artifact | `plan/cli-version-smoke-test/cli-version-smoke-test.implementation-review.yaml` | Reviewer | Repo-visible implementation-review gate evidence |
| Package entrypoint module | `src/async_model_gateway/__init__.py` | Implementer | Bounded CLI version surface and package-local version source |
| Package entrypoint smoke tests | `tests/test_package_entrypoint.py` | Implementer | Stable smoke-test coverage for scaffold and version behavior |

Artifact path notes:

- This topic does not modify `README.md`, `VERSION`, or
  `.github/copilot-instructions.md`.
- Treat listed paths as an executable contract.
- If later work needs `pyproject.toml`, a new source module, or additional test
  files, stop and route back through `spec-and-plan-finalization`.

## Implementation Steps

1. Deliver the bounded RED-test contract in `tests/test_package_entrypoint.py`
   for explicit version flags so `main(["--version"])` and `main(["-V"])`
   produce the same stable version string, a trailing newline, and empty stderr.
2. Deliver the bounded regression and invalid-input contract in
   `tests/test_package_entrypoint.py` so `main()` and `main([])` preserve the
   existing scaffold output, while unsupported arguments fail without printing
   the version string.
3. Deliver a single package-local version source in
   `src/async_model_gateway/__init__.py` so the planned version surface stays
   inside the existing entrypoint module and does not depend on runtime
   `pyproject.toml` parsing.
4. Deliver the bounded CLI handling change in
   `src/async_model_gateway/__init__.py` so `main` accepts optional argv input,
   preserves the no-argument scaffold path, serves only `--version` and `-V` as
   new version paths, and does not widen into a broader CLI framework.
5. Deliver the repo-visible workflow evidence declared by this topic before PR
   routing begins: update `cli-version-smoke-test.step.md` during execution,
   record `cli-version-smoke-test.red-tests.yaml` after RED test authoring, and
   record `cli-version-smoke-test.implementation-review.yaml` before leaving
   `implement-plan`.

## Validation / Acceptance Checks

- Canonical sections, status names, artifact paths, and reviewer handoff shape
  remain compatible with the repo workflow contracts.
- The plan remains bounded to `src/async_model_gateway/__init__.py` and
  `tests/test_package_entrypoint.py`.
- `cli-version-smoke-test.spec.md` exists because this topic is locked as
  `non-trivial`.
- `cli-version-smoke-test.step.md` mirrors every numbered implementation step.
- Later TDD work can produce a repo-visible
  `cli-version-smoke-test.red-tests.yaml` artifact before production-code
  implementation starts.
- Later implementation review can trace `## Non-goals`,
  `## Public Contract / API Changes`, `## Implementation Steps`, and
  `## Test Plan` without relying on chat-only context.

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
- After merge, stop; do not change README, VERSION, tags, or release state under
  this topic.

## Open Questions / Unresolved Items

- None.

## Non-goals

- This topic does not replace the scaffold output with version output on the
  default no-argument path.
- This topic does not introduce subcommands, config loading, or provider
  wiring.
- This topic does not centralize version management across packaging metadata,
  docs, or release tooling.
- This topic does not add new source modules or new test files beyond the
  bounded entrypoint surfaces.

## Current Context

- `src/async_model_gateway/__init__.py` currently defines the package docstring
  and a minimal `main() -> None` that prints
  `async-model-gateway foundation scaffold`.
- `pyproject.toml` defines the package version as `0.1.0` and maps the console
  script `async-model-gateway` to `async_model_gateway:main`.
- `tests/test_package_entrypoint.py` currently verifies only the default
  scaffold output and has no version-surface coverage.
- The repository already has baseline workflow contracts in
  `plan/agent-handoff-workflow.md` and `plan/topic-plan-contract.md`, so this
  topic can exercise the Python extension path without modifying those
  contracts.

## Requirements

1. The existing CLI entrypoint must expose a stable version surface that can be
   triggered from the current package entrypoint without adding a new command
   tree.
2. The default no-argument scaffold behavior must remain unchanged.
3. Version output must come from one package-local Python source of truth rather
   than runtime parsing of `pyproject.toml`.
4. The planned implementation must be testable through TDD and bounded to the
   existing entrypoint module and smoke-test file.
5. The topic must declare all repo-visible companion artifacts needed for plan
   review, step tracking, RED-test gating, and implementation review.

## Decisions

- Async-planning status: exempt — cite exemption evidence: the topic is a small,
  synchronous CLI entrypoint change with no async boundary, resource lifecycle,
  concurrency, timeout, or cancellation behavior.
- Module/package placement: keep all planned source changes in
  `src/async_model_gateway/__init__.py`.
- New public API: yes — export a package-level `__version__: str` surface and
  change the callable contract of `main` to accept optional argv input while
  keeping zero-argument invocation valid.
- Interface changes: yes — `main()` becomes a testable CLI shim for explicit
  version flags in addition to the existing scaffold output path.
- Breaking changes allowed: no — the no-argument entrypoint behavior and
  existing console-script name remain stable.
- New dependencies: no.
- Error handling strategy: accept only the bounded no-argument path plus
  `--version` and `-V`; unsupported arguments should fail cleanly with a
  non-zero CLI exit path and no version output.
- Typing strategy: fully typed using the standard library typing surface only.

## Public Contract / API Changes

- `async_model_gateway.__version__`
  - New package-level string surface that provides the stable version value used
    by the bounded CLI version path.
- `async_model_gateway.main`
  - Planned signature: `def main(argv: Sequence[str] | None = None) -> None`
  - Backward compatibility: direct zero-argument calls stay valid and continue
    to print the scaffold output.
  - New behavior: explicit `--version` and `-V` arguments print the stable
    version string.
  - Failure behavior: unsupported arguments fail through a non-zero CLI exit
    path instead of silently printing version output.

## Affected Files / Modules

Likely affected files:
- `src/async_model_gateway/__init__.py`
- `tests/test_package_entrypoint.py`

Candidate files to inspect:
- `pyproject.toml`

## Test Plan

Test file: `tests/test_package_entrypoint.py`

Test cases:
- Happy path: `main(["--version"])` prints the stable version string with a
  newline and no stderr.
- Invalid input: an unsupported argument path exits non-zero and does not print
  the version string.
- Edge case: `main(["-V"])` matches the long-form version output exactly.
- Regression: `main()` still prints
  `async-model-gateway foundation scaffold`.
- Backward compatibility: `main([])` behaves like `main()` and direct imports
  from `async_model_gateway` remain valid.

## Validation Commands

```text
pytest tests/test_package_entrypoint.py -v
pyright src
ruff check src tests
```

## Risks

- A package-local version source can drift from the version declared in
  `pyproject.toml` if a later topic does not unify the update process.
- Even a small CLI argument shim can expand accidentally into broader command
  parsing unless the implementation stays inside the declared file boundary.

## Rollback Plan

- Revert `src/async_model_gateway/__init__.py` and
  `tests/test_package_entrypoint.py` to the scaffold-only state.
- Mark any later `*.red-tests.yaml` or `*.implementation-review.yaml` artifacts
  for this topic as superseded if the implementation is rolled back before merge.
