---
topic: cli-version-smoke-test
phase: plan-authoring
created: 2026-06-17
---

# cli-version-smoke-test — Step Tracking

> **Executor**: Mark each step `[X]` when complete.
> All Implementation Steps must be `[X]` before submitting for `python-implementation-review`.
> Update this file at: `plan/cli-version-smoke-test/cli-version-smoke-test.step.md`

## Workflow Stages

- [X] plan-authoring
- [X] plan-review
- [ ] tdd-test-authoring
- [ ] implementation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

- [ ] 1. Deliver the bounded RED-test contract in `tests/test_package_entrypoint.py` for explicit version flags so `main(["--version"])` and `main(["-V"])` produce the same stable version string, a trailing newline, and empty stderr.
- [ ] 2. Deliver the bounded regression and invalid-input contract in `tests/test_package_entrypoint.py` so `main()` and `main([])` preserve the existing scaffold output, while unsupported arguments fail without printing the version string.
- [ ] 3. Deliver a single package-local version source in `src/async_model_gateway/__init__.py` so the planned version surface stays inside the existing entrypoint module and does not depend on runtime `pyproject.toml` parsing.
- [ ] 4. Deliver the bounded CLI handling change in `src/async_model_gateway/__init__.py` so `main` accepts optional argv input, preserves the no-argument scaffold path, serves only `--version` and `-V` as new version paths, and does not widen into a broader CLI framework.
- [ ] 5. Deliver the repo-visible workflow evidence declared by this topic before PR routing begins: update `cli-version-smoke-test.step.md` during execution, record `cli-version-smoke-test.red-tests.yaml` after RED test authoring, and record `cli-version-smoke-test.implementation-review.yaml` before leaving `implement-plan`.
