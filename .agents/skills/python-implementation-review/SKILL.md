---
name: python-implementation-review
description: Review a Python implementation against its approved plan to confirm all Implementation Steps are complete, no scope has crept beyond Non-goals, the Public Contract is unchanged, and the Test Plan cases are present. Run BEFORE python-code-review.
complexity: high

risk_profile:
  - ambiguity_sensitive
  - multi_agent_handoff

inputs:
  - approved *.plan.md (formal approval confirmed before tracing begins)
  - optional plan/<topic>/<topic>.step.md for pre-review step gating
  - implementation: code diff or changed file set
  - plan sections: Implementation Steps, Non-goals, Public Contract / API Changes, Test Plan

outputs:
  - YAML verdict block (verdict, traceability_matrix, scope_creep_check, contract_check, test_plan_check)
  - review_status: "INCOMPLETE (when partial review)"
  - plain-text refusal output when preconditions are unmet
  - BLOCKED plain-text refusal output when pending Implementation Steps remain in *.step.md

use_when:
  - a *.plan.md has been approved by python-plan-review
  - the implementation (diff or changed file set) is available
  - the goal is to confirm the implementation matches the plan, not assess code quality

do_not_use_when:
  - the plan has not yet been formally approved
  - the implementation does not yet exist
  - the goal is to review code style, typing, linting, or Python idioms
  - the goal is to check whether the plan itself is executable (use python-plan-review)
  - the goal is to judge architecture quality, design patterns, or naming conventions
---

# Purpose
Verify that a Python implementation satisfies its approved plan — all steps done, no scope creep, Public Contract unchanged, and Test Plan cases present — while honoring the pre-review `*.step.md` gate when that file exists.

# Sequencing rule
Run `python-implementation-review` **before** `python-code-review`.
Do not optimize code quality on an incomplete or drifted implementation.

# Trigger / When to use
Use this skill when:
- a `*.plan.md` has been approved by `python-plan-review` (or the project's equivalent plan-review gate)
- the implementation (code diff or changed file set) is available
- the goal is to confirm the implementation matches the plan, not to assess code quality

Do not use this skill when:
- the plan has not yet been approved — route to `python-plan-review` first
- the implementation does not yet exist — wait until it is available
- the goal is to review code style, typing, linting, or Python idioms — use `python-code-review`
- the goal is to check whether the plan document itself is executable — use `python-plan-review`
- the goal is to judge architecture quality, design patterns, or naming conventions

# Inputs
- an approved `*.plan.md` (approval status must be confirmed before proceeding)
- optional `plan/<topic>/<topic>.step.md` for backward-compatible pre-review step gating
- the implementation: code diff or the set of changed files
- the four plan sections traced by this skill:
  - `## Implementation Steps` — completeness check
  - `## Non-goals` — scope-creep check
  - `## Public Contract / API Changes` — contract check
  - `## Test Plan` — test coverage check

# Process
1. **Confirm inputs.**
   - Verify that the `*.plan.md` was approved by `python-plan-review` (or the project's equivalent plan-review gate).
   - Verify that the implementation (diff or file set) is present.
   - If the plan has not been formally approved, refuse the review and instruct the requester to route through `python-plan-review` first. Do not proceed.
   - If the implementation is absent, halt and request it before continuing.

1.5 **Check step completion (step gate).**
   - Resolve the topic from the plan path (for example, `plan/my-feature/my-feature.plan.md` → `my-feature`).
   - If `plan/<topic>/<topic>.step.md` does not exist, emit:

     ```text
     ⚠️  WARNING: plan/<topic>/<topic>.step.md not found.
                  Proceeding without step gate check.
                  Suggestion: re-run python-plan-authoring to produce a step.md.
     ```

     Then continue to step 2.
   - If `plan/<topic>/<topic>.step.md` exists, check only the `## Implementation Steps` section for pending lines that match `^\- \[[ x]\]`. Do not scan `## Workflow Stages`.
   - Portable default:

     ```bash
     sed -n '/^## Implementation Steps/,/^## /p' plan/<topic>/<topic>.step.md | grep '^\- \[[ x]\]'
     ```

     No matches → all Implementation Steps are complete → continue to step 2.
     One or more matches → pending Implementation Steps remain. Lowercase `[x]` is pending, not done.
   - Optional helper path: a repository may also reference `python .codex/skills/plan-step-tracker/scripts/step_tracker.py ...`, but only when that path is narrowed to the same `## Implementation Steps` semantics as the portable check above. It is never a hard dependency for this skill.
   - If pending Implementation Steps are found, emit the BLOCKED refusal output below and stop immediately. Do not build the traceability matrix, and do not produce a YAML verdict block.

2. **Build the traceability matrix.**
    - For each numbered item in `## Implementation Steps`, locate evidence in the implementation.
    - Record `done` (change is fully present), `partial` (only part of the described change exists), or `missing` (no relevant code change found).
    - Record the evidence location as `file:line` or `"not found"`.

3. **Check the Non-goals boundary.**
   - For each item in `## Non-goals`, scan the implementation for any code that matches or addresses it.
   - A match means scope has crept outside the plan boundary → flag `needs-rework`.

4. **Check the Public Contract.**
   - For each API item in `## Public Contract / API Changes`, compare the expected signature, return type, raised exceptions, and compatibility notes against the actual implementation.
   - Any deviation not described in the plan (added parameter, changed return type, new exception) → `needs-rework`.
   - A missing authorized change → `needs-rework`.

5. **Check the Test Plan.**
   - For each case type in `## Test Plan`, confirm it is present in the test files.
   - If specific test file paths are named in the plan, verify the cases exist there.
   - Mark each case type `present` or `missing`.

6. **Output the verdict.**
   - `approved`: all traceability steps are `done`, no Non-goals violated, all contract items `matches`, all test cases `present`.
   - `needs-rework`: one or more gaps found. Include a fully populated verdict output with specific gap details.

# Examples
- Positive: Plan has 3 Implementation Steps and all three are found in the diff, Non-goals list "no CLI changes" and the diff touches no CLI files, `def validate_email(address: str) -> bool` matches the Public Contract exactly, and happy-path, invalid-input, and edge-case tests are present in `tests/test_email_validator.py` → return `approved` with a fully `done` traceability matrix.
- Negative: Plan's Non-goals includes "no CLI changes" but the diff adds `--validate-email` to `src/cli.py` → return `needs-rework`, cite the Non-goals violation with `src/cli.py:42` as evidence. Do not approve because the parameter has a default value or the change seems small.

# Outputs

```yaml
verdict: approved | needs-rework

traceability_matrix:
  - step: "<implementation step text from plan>"
    status: done | missing | partial
    evidence: "<file:line or 'not found'>"

scope_creep_check:
  - non_goal: "<item text from Non-goals>"
    violated: yes | no
    evidence: "<file:line or 'clean'>"

contract_check:
  - item: "<API item text from Public Contract>"
    status: matches | deviation
    detail: "<what matches or what differs>"

test_plan_check:
  - case_type: "<case type from Test Plan, e.g. happy path | invalid input | edge case>"
    status: present | missing
    location: "<test file:line or 'not found'>"
```

**Refusal output** (plain text, no YAML): produced when the plan has not been
formally approved or when the implementation has not been provided. States which
precondition is unmet and the required routing action (e.g. route the plan through
`python-plan-review` first, or provide the implementation diff). See `examples.md`
Example 5 for the exact format.

**BLOCKED — Step gate failed** (plain text, no YAML):

```text
BLOCKED — Step gate failed.

The following Implementation Steps are still pending in plan/<topic>/<topic>.step.md:

  - [ ] N. <pending step text>
  - [ ] M. <pending step text>

Action required:
  Complete all pending steps and mark them [X] in plan/<topic>/<topic>.step.md
  before re-submitting for python-implementation-review.
```

# Validation

## Required Checks
- Approved `*.plan.md` must be provided and its formal approval confirmed before tracing begins.
- Implementation diff or changed file set must be present.
- If `plan/<topic>/<topic>.step.md` exists, the review must block on any pending line inside `## Implementation Steps` before tracing begins.
- `## Workflow Stages` must never be used as blocking evidence for the step gate.
- Every numbered item in `## Implementation Steps` must be explicitly verified against the implementation.

## Quality Checks (best effort)
- No item in `## Non-goals` is violated by the implementation.
- Every API item in `## Public Contract / API Changes` matches the actual implementation signature, including parameters and exception types.
- Every case type in `## Test Plan` is present in the test files by substance, not merely by test function name.

## On Soft Fail
- Return `verdict: needs-rework` with `review_status: INCOMPLETE`.
- Continue with best-effort output, completing all checks that are possible.
- List which checks could not run and why (e.g., missing plan section, unreadable file, ambiguous step).

# Failure Handling

## Missing Context
- BLOCKED — if the approved `*.plan.md` is not provided or its formal approval cannot be confirmed, stop and request the missing artifact; do not produce a verdict.
- BLOCKED — if the implementation diff or changed file set is absent, stop and request it before continuing.
- WARN — if `plan/<topic>/<topic>.step.md` is missing, emit the warning, suggest re-running `python-plan-authoring`, and continue with the review.

## Step Gate
- BLOCKED — if `plan/<topic>/<topic>.step.md` contains pending lines under `## Implementation Steps`, stop before the traceability matrix and use the plain-text BLOCKED output format.
- Do not produce a YAML verdict block for a BLOCKED step-gate result.

## Ambiguous Requirement
- If a plan step is ambiguous (e.g., vague scope description, unclear target file), note it as a soft-fail item in the traceability matrix with `status: partial` and a short note on the ambiguity.
- Do not block the overall verdict solely on plan step ambiguity; surface it clearly and continue reviewing the remaining steps.

## Execution Limitation
- If file inspection is limited (very large diff, binary files, inaccessible paths), note the limitation explicitly in the output.
- Review whatever is available; do not fabricate evidence for unreachable files.
- Mark affected traceability steps as `partial` or `missing` with a note explaining the limitation.

# Verification
- Confirm the plan has formal approval from `python-plan-review` before tracing begins.
- Confirm every Implementation Step is explicitly mapped to a code location before returning `approved`.
- Confirm every Non-goals item is scanned — do not skip items because they seem unlikely to appear.
- Confirm each Public Contract item is compared signature-by-signature, including default parameters and exception types.
- Confirm Test Plan case types are verified by substance (the logic is present), not only by test function name.

# Red Flags
- Plan approval was informal ("looks good" in chat) rather than a formal verdict from `python-plan-review`.
- Non-goals list was not checked because "no one would add that."
- A new optional parameter (`strict: bool = False`) is treated as harmless and not flagged as a contract deviation.
- Test presence is assumed because a test file exists, without verifying the required case types.
- Code quality concerns (naming, style, typing) appear in the verdict — those belong to `python-code-review`.

# Common Rationalizations
- "The extra parameter has a default value, so it's backward-compatible — no deviation."
- "The Non-goals item wasn't relevant to this feature, so I skipped scanning for it."
- "The test file already has tests, so the Test Plan must be covered."
- "The plan was approved informally; a formal verdict would have passed anyway."
- "Step 3 is mostly done — close enough to mark as `done`."

# Boundaries
- Do not review code style, typing, linting, or Python idioms — that is `python-code-review`.
- Do not judge whether the architecture is good or whether the design is idiomatic.
- Do not comment on naming conventions, formatting, or test organization style.
- Do not approve when the plan has not been formally reviewed by `python-plan-review`.
- Do not run before the implementation is available.
- Do not rewrite or repair the implementation inline.
- Do not re-author or repair the plan.

# Local references
- `examples.md`: full scenarios for approved, missing-step, scope-creep, contract-deviation, and refuse cases, each with a populated verdict output
- `reference.md`: overview table linking to all split files in `references/`
- `references/plan-section-structure.md`: the 13-section plan structure and the four sections traced by this skill
- `references/semantic-boundaries.md`: sequence diagram and role definitions for `python-plan-review`, `python-implementation-review`, and `python-code-review`
- `references/traceability-status.md`: traceability step status definitions (`done`, `partial`, `missing`) and Test Plan coverage rules
- `references/contract-deviation-rules.md`: exhaustive list of contract deviation types and why default parameters are not exempt
