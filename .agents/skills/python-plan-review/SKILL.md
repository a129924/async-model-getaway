---
name: python-plan-review
description: Review a Python *.plan.md for executability — verifying all 13 required sections, decision completeness, explicit async trigger or exemption citation, async-planning coverage when triggered, step precision, test specificity, and validation coverage before implementation begins.
complexity: high
risk_profile:
  - ambiguity_sensitive
  - multi_agent_handoff
inputs:
  - the target *.plan.md file path
  - "[optional] the project pyproject.toml, Makefile, or README path — only needed when checking whether a Validation Commands reference is resolvable"
outputs:
  - "structured verdict: approved | needs-rework | insufficient-context"
  - "blocking_issues list — each item names the section, the concrete problem, and the required fix"
  - hard failure when `Async-planning status` or an exemption citation is missing from `## Decisions`
use_when:
  - a drafted Python *.plan.md already exists and needs review before implementation
  - the workflow needs a check that the plan is complete, unambiguous, and executable
  - the expected output is a structured verdict with per-section blocking issues
do_not_use_when:
  - the task is to author or repair the plan; use python-plan-authoring instead
  - the task is to review code, a PR diff, or an implementation against a plan — use python-implementation-review
  - the task is to review Python code quality — use python-code-review
  - the plan has not yet been drafted
  - the input is a skill folder, topic plan, blueprint, or retrofit-plan contract
---

# Purpose
Review a Python `*.plan.md` document for plan quality and return a structured verdict before any implementation starts. The central question is: **can this plan be executed without guessing?**

# Trigger / When to use
Use this skill when:
- a drafted Python `*.plan.md` already exists and needs review before implementation
- the workflow needs a check that the plan is complete, unambiguous, and executable
- the expected output is a structured verdict with per-section blocking issues

Do not use this skill when:
- the task is to author or repair the plan; use `python-plan-authoring` instead
- the task is to review code, a PR diff, or an implementation against a plan — use `python-implementation-review`
- the task is to review Python code quality — use `python-code-review`
- the plan has not yet been drafted
- the input is a skill folder, topic plan, blueprint, or retrofit-plan contract

# Inputs
- the target `*.plan.md` file path
- [optional] the project `pyproject.toml`, `Makefile`, or `README` path — only needed when checking whether a `Validation Commands` reference is resolvable

# Process
1. Confirm the task is plan-document quality review only.
   - Reject authoring, code review, implementation review, and PR diff review.
   - If the input is not a `*.plan.md`, return `insufficient-context` with a reroute note in `blocking_issues`.
2. Confirm the plan text is sufficient to evaluate before proceeding.
   - If the document is truncated and one or more sections are absent from the visible text → return `insufficient-context`; name every section that cannot be assessed.
   - If the file has no recognizable `*.plan.md` heading structure → return `insufficient-context` with a reroute note instead of a verdict.
   - If `Validation Commands` names an external resource that cannot be located and provides no inline fallback → flag as `insufficient-context` for that section only.
3. Read the target `*.plan.md` in full before judging any section.
4. Detect whether async-planning should be present.
    - Trigger on plan-visible async-capable evidence such as `async def`, `await`, `asyncio`, AnyIO, FastAPI async endpoints, `AsyncSession`, `httpx.AsyncClient`, async repositories, workers, queues, semaphores, rate limits, retries, timeouts, cancellation policy, backpressure policy, or multi-call external I/O orchestration.
    - Do not trigger on syntax-only teaching, a single missing `await`, typing-only work, pure CPU work, or explicitly unchanged async baselines.
    - If the plan text itself contains the async evidence, review must not ignore it just because the author did not label the topic async.
    - Review the plan artifact, not skill invocation history. Contract-critical validity comes from plan text alone, and the designated evidence slot is `- Async-planning status:` inside `## Decisions`.
5. Check that all 13 required top-level sections are present in the document.
   Required sections (any order is acceptable):
   1. Goal
   2. Non-goals
   3. Current Context
   4. Requirements
   5. Decisions
   6. Public Contract / API Changes
   7. Affected Files / Modules
   8. Implementation Steps
   9. Test Plan
   10. Validation Commands
   11. Risks
   12. Rollback Plan
   13. Open Questions

   Any missing section → return `needs-rework` immediately and stop further quality checks. Name every missing section in `blocking_issues`.

6. Validate the **Decisions** section.
   - It must begin with a designated async-routing line in repo-visible plan text:
     - `Async-planning status: triggered — cite trigger evidence: ...`
     - or `Async-planning status: exempt — cite exemption evidence: ...`
   - Missing `Async-planning status` → `needs-rework`; this is a contract failure, not a preference.
   - `Async-planning status: exempt` without an explicit exemption citation → `needs-rework`; reviewer must not infer the reason.
   - It must explicitly address all 7 of the following required decision topics:
      - Module/package placement: names a concrete file path or package (not "somewhere in src/")
      - Public API: explicitly yes or no, with rationale if yes
     - Interface changes: described, or explicitly stated as none
     - Breaking changes: described, or explicitly stated as none
     - New dependencies: named with version constraint, or explicitly stated as none
     - Error-handling strategy: names exception type, propagation model, or error boundary
     - Typing strategy: names the approach (e.g., strict mypy, runtime-only, no-op)
   - Addressing only some of these topics → `needs-rework`; name every missing topic.
   - If async-planning is triggered, the same `## Decisions` section must also include these exact subsections:
      - `### Async boundary decision`
      - `### Resource lifecycle decision`
      - `### Concurrency model`
     - `### Failure model`
     - `### Cancellation / timeout policy`
     - `### Validation plan`
     - `### Handoff notes for the implementer`
   - If async-planning is triggered and any of those subsections are missing, return `needs-rework` and state `retrofit required` in the blocking issue.
   - If `Async-planning status` says `triggered`, missing subsections are a hard failure even when the rest of the plan looks complete.
   - If `Async-planning status` says `exempt`, async subsections may be absent only when the exemption citation is explicit and plan-visible async evidence does not contradict it.
7. Validate async contradiction handling when async-planning is triggered.
    - If the plan text contains conflicting async claims, require `### Async contradiction log` instead of choosing one interpretation.
    - The contradiction log must identify contradiction, source A, source B, risk impact, decision owner / next action, and blocking or non-blocking classification.
    - Review may not silently override the frozen async baseline.
   - If plan-visible async-capable evidence conflicts with an exemption claim, require contradiction handling or `retrofit required` instead of silently choosing one side.
8. Validate **Non-goals**.
   - Must contain ≥3 explicit "will not" items that scope what this plan excludes.
   - Fewer than 3 items, or a generic placeholder such as "nothing excluded" → `needs-rework`.
9. Validate **Implementation Steps**.
   - Steps must be numbered.
   - Each step must reference a concrete file, module, or component by name.
   - `"Refactor the parser"` alone → fails; `"Update src/parser.py to handle empty lists"` → passes.
   - `"Write tests"` without naming the test file or what to test → fails.
10. Validate **Test Plan**.
    - Must include ALL 5 of the following test case categories: happy path, invalid input, edge case, regression, backward compatibility.
    - Missing any one of these 5 categories → `needs-rework`.
    - `"Add tests for this feature"` alone → fails.
    - If async-planning is triggered and `### Validation plan` names timeout, cancellation, resource cleanup, grouped failure, or concurrency-specific checks, those checks must also appear consistently in `## Test Plan`.
11. Validate **Validation Commands**.
    - Must either name specific runnable commands (e.g., `pytest -v`, `ruff check .`, `mypy src/`)
      OR explicitly reference a project config file (`pyproject.toml`, `Makefile`, `README`).
    - Empty section, or a phrase such as `"run the tests"` → fails.
12. Validate **Risks** and **Rollback Plan**.
    - Each section must contain at least one concrete item.
    - Empty section in either → `needs-rework`.
13. Validate **Open Questions**.
    - Scan for any question explicitly marked as blocking implementation start (e.g., `"BLOCKS"`, `"must resolve before coding"`, or equivalent).
    - Any such blocking question → `needs-rework`; name the blocking question.
    - Unresolved but non-blocking open questions are acceptable.
14. Return the verdict.
    - If no blocking issues were found → `approved`.
    - Otherwise → `needs-rework` with a `blocking_issues` list that names the section, the problem, and the required fix for every failure.
    - If the plan text was insufficient to assess → `insufficient-context` as determined in step 2.

# Examples

**Positive (approved):** All 13 sections present, all quality bars met, and `## Decisions` records `Async-planning status` plus async-planning subsections when triggered.
```yaml
verdict: approved
blocking_issues: []
```

**Negative (needs-rework):** Async-capable evidence is present, but `## Decisions` omits `Async-planning status` or stops after the standard seven bullets and leaves timeout / cancellation decisions to the implementer.
```yaml
verdict: needs-rework
blocking_issues:
  - section: Decisions
    issue: Async-capable evidence is present but `Async-planning status` and the required async-planning subsections are missing. retrofit required.
    fix: Add `Async-planning status: triggered — cite trigger evidence: ...` plus all seven required async-planning subsections under `## Decisions` before implementation continues.
```

**Insufficient-context:** `feature.plan.md` is truncated mid-document; multiple sections cannot be assessed.
```yaml
verdict: insufficient-context
blocking_issues:
  - section: (document)
    issue: Plan truncated; multiple sections cannot be evaluated.
    fix: Provide the complete *.plan.md and re-run the review.
```

# Outputs
- a structured verdict in the following YAML format:

```yaml
verdict: approved | needs-rework | insufficient-context
blocking_issues:
  - section: <section name>
    issue: <what is wrong>
    fix: <what to add or change>
```

- `blocking_issues` is an empty list when `verdict` is `approved`
- `verdict` is `insufficient-context` when the plan text is too truncated or unstructured to assess one or more sections; name the unassessable sections in `blocking_issues`
- each blocking issue names the section, describes the concrete problem, and states the required fix
- use the literal phrase `retrofit required` when async risk is discovered late in an already-started plan
- no plan text is rewritten; only the verdict is returned

# Validation

## Required Checks
- all 13 required top-level sections are present in the document (Goal, Non-goals, Current Context, Requirements, Decisions, Public Contract / API Changes, Affected Files / Modules, Implementation Steps, Test Plan, Validation Commands, Risks, Rollback Plan, Open Questions)
- Decisions section addresses all 7 required decision topics (module/package placement, public API, interface changes, breaking changes, new dependencies, error-handling strategy, typing strategy)
- Decisions includes a designated `Async-planning status` line with cited trigger or exemption evidence
- plan-visible async-capable evidence is evaluated instead of ignored
- async-capable plans include all 7 required async-planning subsections under `## Decisions`
- exempt plans still include an explicit exemption citation in `Async-planning status`
- contradictions in async decisions are recorded with `### Async contradiction log` instead of being silently overridden
- Non-goals contains ≥3 explicit "will not" items
- Implementation Steps are numbered and each references a concrete file, module, or component by name
- Test Plan names all 5 required categories: happy path, invalid input, edge case, regression, backward compatibility
- Validation Commands name specific runnable commands or explicitly reference a project config file
- Risks and Rollback Plan each contain at least one concrete item
- no Open Question is explicitly marked as blocking implementation start

## Quality Checks (best effort)
- async trigger or exemption reasoning is explainable from the plan text alone
- async validation expectations in `### Validation plan` and `## Test Plan` agree with each other
- Risks and Rollback Plan items are concrete and actionable, not generic placeholders
- Open Questions have named owners or a stated resolution path
- Decisions rationale is present where `yes` or `no` alone would leave the executor guessing

## On Soft Fail
- use `verdict: insufficient-context`; do not invent an unsupported review verdict or status
- return best-effort findings for every section that could be assessed
- list each unassessable section explicitly in `blocking_issues` with `issue: Section could not be fully evaluated` and `fix: Provide complete content`
- use `needs-rework` for assessable sections that are conceptually incomplete or ambiguous enough to need repair
- do not block output; surface findings even when context is partial

# Failure Handling

## Missing Context
- BLOCKED — if the plan document is not provided or cannot be located, stop and ask for the file path before proceeding; do not attempt a review against an absent document

## Ambiguous Requirement
- if a plan section is present but critically ambiguous (e.g., a Decisions entry that names the topic but gives no resolution), treat it as a soft-fail item
- if async-capable evidence and exemption evidence conflict, require a contradiction log or explicit retrofit instead of silently choosing one side
- list the item in `needs-rework` findings with the exact section name so the author can fix it without guessing

## Execution Limitation
- if codebase files referenced in the plan (e.g., named source files in Implementation Steps) cannot be inspected, record the constraint as a `blocking_issues` entry (section: environment, issue: named file could not be inspected, fix: provide readable file or confirm path before re-review)
- review only what is present in the plan text; do not fabricate inferred content to fill gaps

# Verification
- confirm the input is a `*.plan.md`, not code or a PR diff
- confirm all 13 required top-level sections are present before running quality checks
- confirm the Decisions section addresses all 7 required decision topics
- confirm `Async-planning status` is present and exemptions were not hand-waved
- confirm triggered async plans include the exact seven async-planning subsections
- confirm contradictions are logged instead of silently resolved
- confirm retrofit cases use the phrase `retrofit required`
- confirm Non-goals has ≥3 explicit `will not` items
- confirm Implementation Steps are numbered and file-specific
- confirm Test Plan names specific test case categories and stays aligned with async validation when triggered
- confirm Validation Commands name specific commands or reference a project config file
- confirm Risks and Rollback Plan each have ≥1 concrete item
- confirm no Open Question is flagged as blocking implementation
- confirm `insufficient-context` is returned when the plan text is truncated or unstructured and cannot be fully assessed
- confirm the output is only the verdict block — no inline plan repairs

# Red Flags
- approving a plan where any of the 13 sections is missing
- treating `standard Python practices` as an adequate Decisions section
- accepting a plan with no `Async-planning status` line in `## Decisions`
- ignoring plan-visible `AsyncSession`, `AsyncClient`, queue, timeout, cancellation, or concurrency evidence because the author did not label it async
- approving an async-capable plan with no async-planning subsections
- approving an exempt plan whose exemption reason is not explicitly cited in `Async-planning status`
- silently reconciling contradictory async decisions instead of requiring a contradiction log
- accepting `Add tests` as a complete Test Plan
- accepting an empty Validation Commands section because `tests are obvious`
- ignoring a question marked `BLOCKS` in Open Questions
- rewriting plan content inline instead of flagging it as a blocking issue
- returning `needs-rework` when the plan text is simply truncated or unstructured — use `insufficient-context` instead
- confusing this skill with `python-implementation-review` or `python-code-review`

# Common Rationalizations
- `The executor can infer the module location from context.`
- `The async details are implementation concerns, not plan concerns.`
- `The reviewer can fix the async wording mentally.`
- `Two Non-goals are close enough to three.`
- `Empty validation commands are fine because CI will figure it out.`
- `The open question will probably be resolved before implementation starts.`
- `Returning suggestions is enough even if the verdict is missing.`

# Boundaries
- Do not author or repair the plan document.
- Do not look at any code, PR diff, or implementation artifact.
- Do not judge whether architecture decisions are correct — only that they are explicitly stated.
- Do not evaluate code style.
- Do not approve a plan that is missing any of the 13 required top-level sections.
- Do not approve a plan whose Decisions section omits any required decision topic.
- Do not let async-capable evidence pass without either the required async-planning coverage or a justified exemption recorded in `Async-planning status`.
- Do not silently override or normalize contradictions in the async baseline.
- Do not overlap with `python-implementation-review` (code vs plan) or `python-code-review` (code quality).
- Do not emit anything except the verdict block.

# Local references
- `checklist.md`: repeatable per-section and async-gate acceptance checklist for use before returning the final verdict
- `examples.md`: approved, needs-rework, exempt, contradiction, and retrofit scenarios with full verdict output
