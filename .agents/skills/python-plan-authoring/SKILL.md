---
name: python-plan-authoring
description: Create an executable Python implementation plan that freezes scope, contracts, decisions, affected files, tests, and validation commands before coding begins. Not a todo list — an implementation contract that executor can follow and reviewer can verify.
complexity: high   # creates multi-section plans that gate execution; required sections follow
risk_profile:
  - ambiguity_sensitive   # missing input fundamentally changes plan scope
  - multi_agent_handoff   # output consumed by plan-reviewer, then executor
inputs:
  - feature or change intent with scope
  - relevant codebase context (modules, packages, public APIs)
  - 'D1 structured verdict when available: `{ "verdict": "trivial|non-trivial", "reason": "..." }`'
  - all 7 required decision answers
  - at least 3 Non-goals
  - measurable requirements for the change
  - test strategy signals
  - project validation commands or config reference
  - async-capable evidence and async baseline inputs when the topic needs a frozen async baseline; use `python-async-planning` as the routing aid when helpful
  - any open questions the author cannot resolve alone
outputs:
  - "*.plan.md with all 13 required sections in order"
  - "*.step.md required co-artifact at plan/<topic>/<topic>.step.md"
  - "when D1 verdict is non-trivial: required co-artifact plan/<topic>/<topic>.spec.md"
  - frozen decisions, affected files, test plan, and validation commands
  - required `Async-planning status` decision line with cited trigger or exemption evidence
  - required async-planning subsections for async-capable topics
  - stop-and-ask questions when required information is missing
use_when:
  - Python feature, refactor, or bug fix needs a frozen contract before coding
  - change touches more than one file or module
  - multiple interfaces will be modified
  - decision records are required
  - reviewer must verify completed work against a written contract
do_not_use_when:
  - change is trivial and isolated (typo, single constant rename)
  - task is to execute or review an existing plan
  - no Python code is involved
  - request is for a generic project management plan unrelated to Python implementation
---

# Purpose
Turn Python implementation intent into a review-ready `*.plan.md` plus required `plan/<topic>/<topic>.step.md` that freeze scope, decisions, affected files, tests, and validation commands before any code changes begin. The plan is an executable implementation contract, not a todo list.

# Trigger / When to use
Use this skill when:
- a Python feature, refactor, or bug fix needs a frozen contract before coding starts
- the task touches more than one file or module and scope clarity is needed before coding
- multiple interfaces will be modified and the dependency order must be declared
- explicit decision records are required (module placement, API shape, error strategy, typing)
- a reviewer must be able to verify completed work against a written contract

Do not use this skill when:
- the change is trivial and isolated (e.g., fix a typo, rename a single constant)
- the task is to execute or review an existing plan
- no Python code is involved
- the request is for a generic project management or release plan unrelated to Python implementation

# Inputs
- the feature, change, or bug fix being planned
- the relevant current codebase context (existing modules, packages, public APIs)
- D1 structured verdict when available: `{ "verdict": "trivial|non-trivial", "reason": "..." }`
- explicit answers to all required decision points (module placement, API shape, breaking changes, dependencies, error handling, typing)
- measurable requirements for the change
- at least 3 Non-goals stating what this change will NOT do
- test strategy signals (expected test categories and test file location)
- the project's existing validation commands or config files (`pyproject.toml`, `Makefile`, `README`)
- async-capable evidence and async baseline inputs when the request changes async boundary, lifecycle, concurrency, failure, or cancellation behavior
- any open questions the author cannot resolve alone

# Process

## Stop-and-ask conditions
Stop before drafting. Ask the user for the missing information when any of the following are absent:

1. **No Decisions content** — the user has not answered all required decision points:
   - Which module or package receives the new code?
   - Is a new public API being added?
   - Are existing interfaces being modified?
   - Are breaking changes allowed?
   - Are new dependencies being added?
   - What is the error handling strategy?
   - What is the typing strategy?
2. **No Non-goals** — the user has not provided at least 3 items that this change will NOT do.
3. **No Validation Commands** — no commands are given and no project config file (`pyproject.toml`, `Makefile`, `README`) is referenced.
4. **Vague Implementation Steps** — the user describes high-level wishes rather than executable steps. `"Refactor the parser"` is not acceptable. `"1. Inspect src/parser.py. 2. Extract validate() into validators.py..."` IS acceptable.
5. **Async-capable topic without a frozen async baseline** — the request introduces async-capable evidence but does not yet answer the async boundary, resource lifecycle, concurrency model, failure model, cancellation / timeout policy, validation plan, and implementer handoff notes needed to freeze the triggered async baseline. Use `python-async-planning` only as the routing aid for gathering that baseline.

## Authoring steps
1. Confirm this is a Python implementation planning task. If the request is execution or review, stop and redirect.
2. Detect whether the request is async-capable and make that decision reviewable in the plan artifact.
   - Under `## Decisions`, add a required `- Async-planning status:` line before the seven standard decision bullets.
   - Use `triggered — cite trigger evidence: ...` when the request introduces async boundary, pooled resources, background ownership, external I/O concurrency choice, retry / timeout / cancellation policy, or sync-to-async conversion.
   - Use `exempt — cite exemption evidence: ...` when the topic falls under an allowed exemption such as syntax-only async teaching, a single missing `await`, typing-only work, or other cases with no planning-stage async risk.
   - This repo-visible status line is the contract. Do not treat skill invocation itself as evidence.
3. If any stop-and-ask condition is triggered, ask the user for the missing detail before drafting.
4. Produce a `*.plan.md` with exactly these 13 sections in order:

   **1. Goal**
   State the single concrete outcome this change achieves. One or two sentences.

   **2. Non-goals**
   List at least 3 items stating what this change will NOT do. Examples: no full module refactor, no CLI change, no new external dependency, no performance work.

   **3. Current Context**
   Briefly describe the relevant existing code, module, or system state. Name the files, classes, or functions that provide context for the change.

   **4. Requirements**
   List measurable requirements. Each item must be verifiable in tests or validation output.

   **5. Decisions**
   Record the async-routing decision plus answers to all 7 standard decision points before drafting the rest of the plan:
   - Async-planning status: `triggered` or `exempt`, with cited repo-visible trigger or exemption evidence
   - Module/package placement: which module or package receives the new code
   - New public API: yes/no — name and signature if yes
   - Interface changes: yes/no — which interfaces and how
   - Breaking changes allowed: yes/no — reason if yes
   - New dependencies: yes/no — name and version if yes
   - Error handling strategy: which exceptions are raised and when
   - Typing strategy: fully typed, use of `Any`, use of `TypeVar` or `Protocol`, etc.

   When `Async-planning status` is `triggered`, the plan artifact must append these exact subsections under `## Decisions` in this exact order:
   - `### Async boundary decision`
   - `### Resource lifecycle decision`
   - `### Concurrency model`
   - `### Failure model`
   - `### Cancellation / timeout policy`
   - `### Validation plan`
   - `### Handoff notes for the implementer`

   When the status is `exempt`, keep the `Async-planning status` line and its exemption citation in `## Decisions`; do not leave exemption reasoning implicit anywhere else.

   If request, baseline, or review notes conflict on async applicability or on an async decision, add `### Async contradiction log` rather than smoothing the conflict over. If the contradiction is discovered in an already-started plan, treat the repair as `retrofit required`.

   **6. Public Contract / API Changes**
   Describe new or changed public functions, classes, or methods. Include signatures, parameters, return types, exceptions, and backward compatibility notes. If no public API changes, state explicitly.

   **7. Affected Files / Modules**
   Use the following format:
   ```
   Likely affected files:
   - src/xxx/yyy.py
   - tests/test_yyy.py

   Candidate files to inspect:
   - src/...
   ```

   **8. Implementation Steps**
   Numbered, executable steps with explicit file references. Each step names a specific file and a specific action. NOT: `"Refactor the validation module."` YES: `"1. Open src/utils/validation.py. Add validate_email(email: str) -> bool below existing validators."`

   **9. Test Plan**
   Must be specific. Name the test file and cover all of the following categories:
   - Happy path
   - Invalid input
   - Edge case
   - Regression
   - Backward compatibility

   For async-capable topics, make the test plan and validation plan consistent with the async-planning subsections. If cancellation, timeout, grouped failure, or resource cleanup are part of the async baseline, name them explicitly here.

   **10. Validation Commands**
   Either explicit commands:
   ```
   pytest tests/test_xxx.py -v
   mypy src/xxx/yyy.py
   ruff check src/
   ```
   Or reference the project config:
   ```
   Use existing project validation commands from pyproject.toml / Makefile / README.
   ```

   **11. Risks**
   Name at least one concrete risk. Examples: `"may affect existing public API callers"`, `"adds a regex that could introduce import-time cost"`, `"type annotation changes may break downstream stubs"`.

   **12. Rollback Plan**
   State how to undo the change. At minimum: name the changed files and how to revert them (e.g., `"revert via git: src/xxx/yyy.py, tests/test_yyy.py"`).

   **13. Open Questions**
   List unresolved questions and who can answer them. State `"None"` if all questions are resolved.
5. Produce `plan/<topic>/<topic>.step.md` alongside the `*.plan.md` using `templates/step-template.md` as the canonical scaffold, then mirror every numbered item from `## Implementation Steps` as pending `- [ ]` entries.

   Keep `plan-step-tracker/reference.md` as the read-only format authority. Do not omit any of the 6 Workflow Stages, and do not use lowercase `[x]` to mark completed work.

6. If D1 verdict is `non-trivial`, produce `plan/<topic>/<topic>.spec.md` as a required co-artifact using this 3-part structure:
   - `Acceptance Criteria`
   - `Behavioral Scenarios` (Given/When/Then)
   - `Error / Edge Cases`

   Use `templates/spec-template.md` as the canonical authoring scaffold.

7. Verify the plan before handoff:
    - All 13 sections are present in order.
    - `Decisions` includes `Async-planning status` plus all 7 required standard items.
    - `Non-goals` lists at least 3 items.
    - `Implementation Steps` are executable and reference specific files.
    - `plan/<topic>/<topic>.step.md` exists, includes `topic`, `phase: plan-authoring`, and `created`, and mirrors every numbered Implementation Step as `- [ ]`.
    - If D1 verdict is `non-trivial`, `plan/<topic>/<topic>.spec.md` exists and includes all three required sections.
    - `Test Plan` covers all 5 test categories.
    - `Validation Commands` are present or reference a project config.
    - `Risks` and `Rollback Plan` name concrete items, not placeholders.
    - If `Async-planning status` is `triggered`, the exact async-planning subsections and contradiction handling are present in the plan text itself.
    - If `Async-planning status` is `exempt`, the exemption citation is explicit in that same line and can be reviewed from plan text alone.
8. Stop at `review-ready`. Do not execute or approve the plan.

# Examples

**Positive** — `validate_email()` feature plan with all 13 sections present and correctly filled:
- `Decisions` begins with `- Async-planning status: exempt — cite exemption evidence: synchronous validation helper with no async boundary, lifecycle, timeout, or concurrency change.`
- `Decisions` then names `src/utils/validation.py` as the target module, states the signature `validate_email(email: str) -> bool`, confirms no breaking changes, no new dependencies, raises `ValueError` on malformed input, and uses fully-typed annotations.
- `Non-goals` states: no changes to the existing `validate_url()` function, no CLI command added, no external dependency introduced.
- `Implementation Steps` say: `"1. Open src/utils/validation.py, add validate_email(email: str) -> bool below existing validators. 2. Raise ValueError('Invalid email format') for malformed input. 3. Add tests/test_validation.py::test_validate_email_happy_path and four additional test cases."`

**Positive** — async-capable orchestration plan:
- The request introduces `AsyncSession`, `httpx.AsyncClient`, and a timeout budget.
- `Decisions` begins with `- Async-planning status: triggered — cite trigger evidence: AsyncSession, httpx.AsyncClient, concurrent upstream I/O, and a 2-second timeout budget.`
- `Decisions` still answers the normal 7 planning questions.
- The same `## Decisions` section then appends `### Async boundary decision`, `### Resource lifecycle decision`, `### Concurrency model`, `### Failure model`, `### Cancellation / timeout policy`, `### Validation plan`, and `### Handoff notes for the implementer` before implementation begins.

**Negative** — plan that triggers `needs-rework`:
- `Decisions` is omitted entirely — the plan jumps straight to Implementation Steps without stating where the code lives or what the API is.
- `Non-goals` is absent — scope is unbounded.
- Async-capable evidence such as `AsyncClient` or a queue worker is present, but the plan omits `Async-planning status`, omits the async-planning subsections, or claims exemption without a cited reason and expects the implementer to decide later.

# Outputs
- a `*.plan.md` with all 13 required sections in order
- a required `plan/<topic>/<topic>.step.md` co-artifact with the canonical step-tracking template
- when D1 verdict is `non-trivial`, a required `plan/<topic>/<topic>.spec.md` co-artifact with the 3-part spec structure
- frozen decisions, affected files, test plan, and validation commands recorded before coding begins
- required async-planning subsections for async-capable topics
- explicit stop-and-ask questions when required information is missing
- a contract that executor can follow step-by-step and reviewer can verify against

# Validation

## Required Checks
- All 13 required sections are present and in order
- `plan/<topic>/<topic>.step.md` is produced alongside the plan and contains `topic`, `phase: plan-authoring`, and `created`
- when D1 verdict is `non-trivial`, `plan/<topic>/<topic>.spec.md` is produced alongside plan/step artifacts and follows the required 3-part structure
- `Decisions` section addresses all 7 required items (no TBD placeholders in contract-critical fields)
- `Decisions` includes a reviewable `Async-planning status` line with cited trigger or exemption evidence
- `Non-goals` lists at least 3 items
- `Implementation Steps` reference specific files and executable actions
- `*.step.md` includes the executor note, all 6 Workflow Stages, and mirrored `## Implementation Steps` entries initialized as `- [ ]`
- `Test Plan` covers all 5 categories: happy path, invalid input, edge case, regression, backward compatibility
- `Validation Commands` are present or explicitly reference a project config file
- async-capable topics with `Async-planning status: triggered` include the exact async-planning subsections
- exempt topics still cite the exemption explicitly in `Async-planning status`

## Quality Checks (best effort)
- `Risks` names a concrete risk, not a placeholder
- `Rollback Plan` names specific files and revert method
- `Open Questions` either lists items with owners or explicitly states `None`
- `*.step.md` stays format-compatible with the read-only rules in `plan-step-tracker/reference.md`
- Step granularity is sufficient for a reviewer to verify completion without ambiguity
- async-capable topics make cancellation, timeout, resource ownership, and concurrency choices explicit enough for an implementer to follow

## On Soft Fail
- mark output plan as INCOMPLETE
- list which section, decision point, or async baseline item is missing or vague
- continue with best-effort draft of all remaining sections
- do not block output if only soft conditions are unmet

# Failure Handling

## Missing Context
- BLOCKED — if any of the 5 stop-and-ask conditions are triggered (missing Decisions, Non-goals, Validation Commands, vague Steps, or missing async baseline for a triggered topic): stop, list missing items, ask user before drafting
- mark any drafted section that relies on missing context as INCOMPLETE

## Ambiguous Requirement
- if ambiguity is blocking (would change module placement, API shape, breaking-change decision, or async boundary / lifecycle ownership): stop and ask before proceeding
- if ambiguity is non-blocking: proceed with stated assumption, list it explicitly in the plan's Open Questions section

## Execution Limitation
- if codebase context is unavailable: state the limitation explicitly; use placeholder file paths clearly marked as `<to be confirmed>`
- do not invent module names, signatures, paths, or async ownership rules the user has not provided

# Boundaries
- Do not execute the plan.
- Do not approve or mark the plan as complete.
- Do not invent module names, file paths, API signatures, or async ownership rules that the user has not provided.
- Do not skip required sections or merge sections together.
- Do not accept vague Implementation Steps — stop and ask instead.
- Do not accept fewer than 3 Non-goals items.
- Do not treat this skill as a generic project planning tool for non-Python work.
- Do not treat `*.step.md` as optional when producing a `*.plan.md`.
- Do not treat `*.spec.md` as optional when D1 verdict is `non-trivial`.
- Do not let async-capable topics skip the triggered async baseline or defer async boundary decisions to the implementer; use `python-async-planning` only as a routing aid when needed.
- Do not leave async applicability implicit; every plan must record `Async-planning status` in `## Decisions`.

# Local references
- `examples.md`: complete positive examples, async-capable routing examples, anti-pattern plans, and stop-and-ask cases
- `templates/python-plan-template.md`: blank 13-section template for executor copy-paste use, including the conditional async-planning scaffold
- `templates/spec-template.md`: canonical 3-part spec template for mandatory non-trivial co-artifact authoring
- `templates/step-template.md`: canonical step-tracking template for required `plan/<topic>/<topic>.step.md` co-artifact
