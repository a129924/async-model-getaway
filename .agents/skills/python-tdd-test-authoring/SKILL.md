---
name: python-tdd-test-authoring
description: Create RED tests from an approved Python implementation plan before implementation begins. Use this when a plan is approved, run internal D1 classification, and produce structured verdict-driven test authoring.
complexity: high

risk_profile:
  - ambiguity_sensitive
  - multi_agent_handoff
  - code_modification

inputs:
  - approved `plan/<topic>/<topic>.plan.md`
  - optional `plan/<topic>/<topic>.spec.md` (primary behavior contract when present)
  - existing test structure (test file layout, naming conventions, helper utilities)
  - validation commands that can verify test status (e.g., `pytest --no-header -rN <test_file>`)
  - evidence that production code is NOT modified yet

outputs:
  - 'D1 structured verdict: `{ "verdict": "trivial|non-trivial", "reason": "..." }`'
  - YAML verdict result file (machine-readable `verdict`, `d1_verdict`, `test_mapping`, `validation_checks`, `issues`, `next_step`)

use_when:
  - implementation plan is approved and ready for test authoring
  - existing test structure exists and can be extended with new RED tests
  - production code has not yet been modified

do_not_use_when:
  - plan is not yet approved
  - production code has already been modified
  - plan context is insufficient to map requirements to test cases
  - test structure does not exist or cannot be determined
---

# Purpose

Create RED (failing) tests from an approved implementation plan, mapping all requirements to test cases before implementation starts. Output a machine-readable YAML result with verdict enum: `red-tests-ready`, `needs-rework`, `insufficient-context`, `skip_with_reason`, or `BLOCKED`.

# Trigger / When to use

Use this skill when:
- an implementation plan is approved and ready for test authoring
- existing test structure exists and can be extended with new RED tests
- you have validated that production code is not modified (only tests are added)

Do not use this skill when:
- the plan is not yet approved
- production code has already been modified (test authoring must happen first)
- plan context is insufficient to map requirements to test cases
- test structure does not exist or cannot be determined

# Inputs

- approved `plan/<topic>/<topic>.plan.md`
- optional `plan/<topic>/<topic>.spec.md` (primary behavior contract when present)
- existing test structure (test file layout, test naming conventions, helper utilities)
- validation commands that can verify test status (e.g., `pytest --no-header -rN <test_file>`)
- evidence that production code is NOT modified yet

# Process

1. **Verify prerequisites**: Confirm the plan is approved and no production code is modified.
2. **Run internal D1 classification**: Produce exactly `{ "verdict": "trivial|non-trivial", "reason": "..." }`.
3. **Handle trivial path early**: If D1 verdict is `trivial`, return `skip_with_reason` with the structured D1 verdict and stop.
4. **Resolve behavior contract for non-trivial path**:
   - If `plan/<topic>/<topic>.spec.md` exists, use it as the primary behavior contract.
   - If `spec.md` conflicts with `plan.md` Requirements, `spec.md` wins and the conflict is recorded in `issues`.
   - If D1 verdict is `non-trivial` and `spec.md` is missing, return `BLOCKED` and route back to `python-plan-authoring` to add `plan/<topic>/<topic>.spec.md`.
5. **Map requirements to tests**: Create `test_mapping` entries (requirement_id → test_case_name) from the active behavior contract.
6. **Check existing tests**: Query test structure for `expected_initial_status` (pass, skip, xfail, or red).
7. **Validate public contract coverage**: Ensure tests cover public functions, return types, error cases, and documented behavior.
8. **Verify 5 test categories present**: Cover (1) happy path, (2) error/exception, (3) boundary/edge, (4) state/side effects, (5) integration points.
9. **Enforce production_code_modified guard**: Verify `production_code_modified: false` before proceeding.
10. **Build output YAML**: Construct result with verdict, `d1_verdict`, test_mapping, validation checks, issues, and next_step.
11. **Return verdict**: `red-tests-ready` (all checks pass), `needs-rework` (fixable gaps), `insufficient-context` (plan gaps), `skip_with_reason` (D1 trivial path), or `BLOCKED` (non-trivial path missing required `spec.md` and routed to `python-plan-authoring`).

# Examples

- **Positive**: Plan with clear Requirements (feature, two bug fixes, refactor), D1 says non-trivial, tests map to all requirements, coverage includes happy path + 3 error cases + boundary case + state assertion + endpoint mock, expected_initial_status is red, production code unmodified → verdict: `red-tests-ready`.
- **Negative**: Invoking this skill when production code has already been modified — hard constraint violated; return `insufficient-context` immediately, do not produce `test_mapping`. Another misuse: invoking when the plan has not yet been approved — return `insufficient-context`, stop, and ask for the approved plan before proceeding.

# Outputs

- YAML verdict result file with schema:
  - `verdict: "red-tests-ready" | "needs-rework" | "insufficient-context" | "skip_with_reason" | "BLOCKED"`
  - `d1_verdict: { "verdict": "trivial|non-trivial", "reason": "..." }`
  - `test_mapping: [{requirement_id, test_case_name, coverage_category}]`
  - `validation_checks: {d1_decision, behavior_contract_source, requirements_mapped, public_contract_coverage, test_categories_present, expected_initial_status, production_code_modified}`
  - `issues: []` (list of specific gaps or failures)
  - `next_step: string` (e.g., "Proceed to implementation" or "Fix test_mapping for Req#2")

# Validation

## Required Checks

- Approved plan is provided and contains a Requirements section.
- D1 behavior-change classification is executed internally with structured verdict output.
- For D1 `non-trivial`, `plan/<topic>/<topic>.spec.md` must exist.
- Test file path is determinable from the plan (target module or package identifiable).

## Quality Checks (best effort)

- Tests cover all 5 categories: happy path, error/exception, boundary/edge, state/side effects, integration points.
- Each generated test contains at least one clear assertion.
- Tests are genuinely RED — they fail before any production code is written (verify by running `pytest --no-header -rN <test_file>` and confirming all new tests fail).

## On Soft Fail

- If plan Requirements section is missing or incomplete, return `insufficient-context`.
- Generate tests only for requirements that are determinable from plan context.
- List skipped requirements explicitly in the `issues` field of the output YAML.

# Failure Handling

## Missing Context

BLOCKED — if the approved plan is not provided, stop immediately and ask for `plan/<topic>/<topic>.plan.md`.

BLOCKED — if D1 verdict is `non-trivial` and `plan/<topic>/<topic>.spec.md` is missing, route to `python-plan-authoring` to create the mandatory spec co-artifact before continuing.

## Ambiguous Requirement

If a plan step is too vague to produce a testable assertion:
- Note the ambiguous step in the `issues` field.
- Skip that step rather than fabricating test logic.
- Continue generating tests for all determinable requirements.
- Return `needs-rework` with a clear description of which steps need clarification.

## Execution Limitation

If existing test files cannot be read (e.g., file system access error):
- Note the limitation explicitly in the output YAML `issues` field.
- Generate tests based on plan context only; do not fabricate assertions about existing test structure.
- Return `needs-rework` unless all required schema fields can still be completed with sufficient confidence.

# Verification

- Confirm D1 classifier decision matches verdict path (non-trivial → proceed; trivial → skip).
- Count test functions to verify 5 categories present (happy, errors, boundary, state, integration).
- Validate test_mapping cardinality: at least one test per requirement.
- Confirm `production_code_modified: false` in all cases.
- Query test file for expected_initial_status and assertion count.

# Red Flags

- Plan missing Requirements section or requirements are vague (insufficient-context).
- D1 verdict is `trivial`: this is a valid skip path and must return `skip_with_reason`.
- D1 verdict is `non-trivial` but `spec.md` is missing (BLOCKED route required).
- Production code has been modified (hard constraint violated; abort immediately).
- Fewer than 5 test categories found (needs-rework).
- Tests map to fewer requirements than listed in plan (incomplete coverage).

# Common Rationalizations

- "D1 says it's a trivial change, can we skip?": Yes, return `skip_with_reason` with D1 verdict; this is a valid outcome, not an error.
- "Some requirements don't have obvious test cases": Needs-rework; add at least one test per requirement or clarify requirement.
- "Test file doesn't exist yet": That's OK; create the file structure and set expected_initial_status to red; still red-tests-ready if coverage is complete.
- "Production code is already half-written": Stop; this violates the hard constraint. Test authoring must happen first.

# Boundaries

- **Hard constraint 1: Never modify production code.** Test authoring happens first; violation → abort with error.
- **Hard constraint 2: D1 classifier decision gates the verdict.** If D1 says `trivial`, honor it and return `skip_with_reason`; do not override.
- **Hard constraint 2.5: D1 verdict output format is fixed.** Emit `{ "verdict": "trivial|non-trivial", "reason": "..." }` exactly.
- **Hard constraint 3: Test mapping must be complete.** Every requirement must have at least one test; partial coverage → needs-rework.
- **Hard constraint 4: Expected initial status must be set.** Verdict must declare whether tests start red, xfail, skip, or pass (for pass_existing case); absence → needs-rework.
- **Hard constraint 5: For non-trivial paths, spec.md is mandatory.** Missing `plan/<topic>/<topic>.spec.md` must return `BLOCKED` and route back to plan-authoring.

# Local references

- `examples.md`: 6 detailed scenarios（含 `d1_verdict`、`BLOCKED` 路由、`non-trivial` enum）與完整輸入/輸出。
- `checklist.md`: 9-item repeatable verification checklist (D1 decision, requirements mapped, public contract, test categories, expected_initial_status, production_code_modified guard, test file structure, YAML schema, boundaries enforced).
- `references/behavior-change-classifier.md`: D1 classifier rules and examples (`trivial|non-trivial` only; maps to skill-level verdict paths).
- `references/codebase-evidence-levels.md`: D2 evidence classification (insufficient, minimal, sufficient context to author tests).
- `references/atomic-commit-order.md`: Commit sequencing rules (test-first, atomic requirements, enforcement modes).
