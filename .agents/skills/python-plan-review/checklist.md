# Python Plan Review Checklist

Use this checklist before returning a verdict for a Python `*.plan.md`.

## Pre-review checks

- [ ] The input is a `*.plan.md` file — not code, a PR diff, a blueprint, or an implementation artifact.
- [ ] The plan is for a Python project (skill is portable to any Python project).
- [ ] The task is plan-document quality review only — not authoring, code review, implementation-vs-plan review, or blueprint review.

## Async-capable gate

- [ ] Scan the plan for async-capable evidence: `async def`, `await`, `asyncio`, AnyIO, FastAPI async endpoints, `AsyncSession`, `httpx.AsyncClient`, queues, workers, semaphores, rate limits, retries, timeouts, cancellation policy, backpressure policy, or multi-call external I/O orchestration.
- [ ] Do not over-trigger on exempt cases such as syntax-only async teaching, a single missing `await`, typing-only work, or pure CPU work with no async design decision.
- [ ] `## Decisions` includes the designated `Async-planning status` line.
- [ ] If `Async-planning status` is `exempt`, the same line explicitly cites the exemption evidence or reason.
- [ ] If async-capable evidence is present, require the exact triggered async-planning subsections under `## Decisions` unless a contradiction-free exemption line stays reviewable from plan text alone.
- [ ] If async risk is discovered in an already-started plan with no async-planning subsections, the blocking issue says `retrofit required`.
- [ ] If async claims conflict, or if plan-visible async evidence conflicts with an exemption claim, require `### Async contradiction log` or `retrofit required` instead of silently choosing one side.

## Section completeness — all 13 required top-level sections

- [ ] **Goal** — present and states a single concrete, measurable outcome
- [ ] **Non-goals** — present; ≥3 explicit "will not" items (see Non-goals quality below)
- [ ] **Current Context** — present; describes the existing state of the codebase or system being changed
- [ ] **Requirements** — present; lists concrete acceptance criteria, not just "make it work"
- [ ] **Decisions** — present; addresses all 7 required decision topics (see Decisions quality below)
- [ ] **Public Contract / API Changes** — present; explicitly states changes or "no changes"
- [ ] **Affected Files / Modules** — present; names at least one concrete file path or module
- [ ] **Implementation Steps** — present; numbered and file-specific (see Implementation Steps quality below)
- [ ] **Test Plan** — present; names specific test case types (see Test Plan quality below)
- [ ] **Validation Commands** — present; names specific commands or references a config file (see Validation Commands quality below)
- [ ] **Risks** — present; ≥1 concrete risk item
- [ ] **Rollback Plan** — present; ≥1 concrete rollback action
- [ ] **Open Questions** — present; may be empty or contain non-blocking items

If any section above is absent → stop and return `needs-rework` naming every missing section before proceeding to quality checks.

## Decisions section quality — async status plus 7 required topics

- [ ] **Async-planning status**: present in `## Decisions` and uses either `triggered — cite trigger evidence: ...` or `exempt — cite exemption evidence: ...`
- [ ] Missing exemption citation is treated as a hard failure, not a quality preference

- [ ] **Module/package placement**: names a concrete file path or package (e.g., `src/weather/parser.py`), not vague phrases such as `somewhere in src/` or `in the right module`
- [ ] **Public API**: explicitly states yes or no; if yes, includes rationale and names the affected surface
- [ ] **Interface changes**: described with before/after, or explicitly stated as none
- [ ] **Breaking changes**: described with migration notes, or explicitly stated as none
- [ ] **New dependencies**: named with version constraint (e.g., `pydantic>=2.0`), or explicitly stated as none
- [ ] **Error-handling strategy**: names exception type(s), propagation model, or error boundary — not just `handle errors properly`
- [ ] **Typing strategy**: names the approach (e.g., strict mypy, runtime-only, no-op) — not just `we use types`

## Async-planning subsection quality — required only when async-capable evidence is present

- [ ] `### Async boundary decision` is present
- [ ] `### Resource lifecycle decision` is present
- [ ] `### Concurrency model` is present
- [ ] `### Failure model` is present
- [ ] `### Cancellation / timeout policy` is present
- [ ] `### Validation plan` is present
- [ ] `### Handoff notes for the implementer` is present
- [ ] If async claims conflict, `### Async contradiction log` is present and names contradiction, source A, source B, risk impact, decision owner / next action, and classification

## Non-goals quality

- [ ] At least 3 items are present
- [ ] Each item is an explicit `will not` or `out of scope` statement
- [ ] No item is a vague placeholder such as `nothing excluded` or `TBD`

## Implementation Steps quality

- [ ] Steps are numbered
- [ ] Each step names a specific file, module, or component (e.g., `src/parser.py`, `tests/test_parser.py`)
- [ ] No step is a high-level wish without a file reference:
  - ❌ `Refactor the parser module.`
  - ✅ `Update src/parser.py to handle empty lists by raising ValueError.`
- [ ] No step says only `Write tests` without naming the test file or what to cover

## Test Plan quality

- [ ] Includes ALL 5 of the following test case categories (missing any one → `needs-rework`):
  - happy path
  - invalid input
  - edge case
  - regression
  - backward compatibility
- [ ] Does not rely solely on `add tests for this feature` or equivalent vague language
- [ ] Test cases are tied to the concrete changes described in Implementation Steps
- [ ] If async-planning is triggered, async validation cases named in `### Validation plan` also appear here

## Validation Commands quality

- [ ] Names specific runnable commands (e.g., `pytest -v`, `ruff check .`, `mypy src/`, `make test`) OR explicitly references a project config file (`pyproject.toml`, `Makefile`, `README`) with a named section or target
- [ ] Not empty
- [ ] Not a vague phrase such as `run the tests` or `CI will handle it`

## Risks quality

- [ ] At least one concrete risk item is present (not a placeholder)
- [ ] Each risk is specific enough to act on (e.g., `pydantic upgrade may break schema validation in adjacent services`, not just `things could break`)

## Rollback Plan quality

- [ ] At least one concrete rollback action is present (not a placeholder)
- [ ] The action is actionable (e.g., `revert commit SHA and redeploy previous image tag`)

## Open Questions gate

- [ ] No question is explicitly marked as blocking implementation start (e.g., `BLOCKS`, `must resolve before coding`, or equivalent)
- [ ] If a blocking question exists → flag in `blocking_issues` and return `needs-rework`
- [ ] Unresolved but non-blocking questions are acceptable and do not fail the review

## Verdict integrity

- [ ] If any check above failed → verdict is `needs-rework`
- [ ] `blocking_issues` names the section, issue, and fix for every failure
- [ ] No plan section was repaired or rewritten inline — verdict only
- [ ] Missing `Async-planning status` or missing exemption citation is returned as `needs-rework`
- [ ] If the plan text is truncated or has no recognizable `*.plan.md` structure → verdict is `insufficient-context`, not `needs-rework`
- [ ] Output is exactly the verdict block in the specified YAML format
