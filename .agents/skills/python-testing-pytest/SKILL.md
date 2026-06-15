---
name: python-testing-pytest
description: Design or review pure Python unit tests in pytest. Use this when choosing assertions, parametrization, fixtures, and unittest.mock patterns without real I/O.

complexity: medium

risk_profile:
  - code_modification

inputs:
  - the behavior under test
  - whether collaborators can be replaced with mocks or fakes
  - whether repeated cases differ only in data
  - whether setup is local or shared
  - whether the effect is observable through state or only through side effects

outputs:
  - review-ready pure pytest unit-testing rule set or skill draft
  - clear defaults for fixtures, parametrization, assertions, and mocks
  - local examples for common cases, anti-patterns, and split signals

use_when:
  - writing or reviewing pytest unit tests for Python code
  - deciding between inline setup and fixtures
  - deciding between state assertions, interaction assertions, and parametrized cases

do_not_use_when:
  - the test needs a real database, filesystem, network, browser, or cross-service call
  - the task is mainly about CI config, coverage tooling, or test-runner setup
  - the task is mainly about naming, typing, model selection, control flow, or DDD-specific workflow policy
---

# Purpose
Choose clear, durable pytest unit-test patterns that verify behavior without real I/O.

# Trigger / When to use
Use this skill when:
- writing or reviewing pytest unit tests for Python code
- deciding between inline setup and fixtures
- deciding between state assertions, interaction assertions, and parametrized cases

Do not use this skill when:
- the test needs a real database, filesystem, network, browser, or cross-service call
- the task is mainly about CI config, coverage tooling, or test-runner setup
- the task is mainly about naming, typing, model selection, control flow, or DDD-specific workflow policy

# Inputs
- the behavior under test
- whether collaborators can be replaced with mocks or fakes
- whether repeated cases differ only in data
- whether setup is local or shared
- whether the effect is observable through state or only through side effects

# Process
1. Keep the first draft in pure unit tests: no real I/O, real DB, or cross-service calls.
2. Default to inline arrange; extract fixtures only for true reuse, shared preconditions, or obvious noise reduction.
3. Use `pytest.mark.parametrize` only when the behavior stays the same and only the data changes.
4. Prefer state or output assertions; use mock call assertions only when the interaction itself is the contract or unavoidable side effect.
5. Use stdlib `unittest.mock` as the baseline; keep `pytest` `monkeypatch` as supplementary detail in `examples.md`.
6. Cover core decision branches and critical behaviors; treat coverage as a supporting signal, not a gate.

# Examples
- Positive: Parametrize one pure function across data-only cases and assert the returned value; mock a notifier only when sending it is the behavior.
- Negative: Put real DB access in this skill, extract every setup into fixtures by default, or assert mock call order when the returned result already proves the behavior.

# Outputs
- a review-ready pure pytest unit-testing rule set or skill draft
- clear defaults for fixtures, parametrization, assertions, and mocks
- local examples for common cases, anti-patterns, and split signals

# Workflow State Contract

## Allowed States
- `COMPLETE`: required checks pass and no blocking ambiguity or missing context remains.
- `INCOMPLETE`: missing context, soft-fail conditions, or execution limitations prevent a fully reliable outcome.

## Output Requirements by State
- Always include a `status` field with one allowed state value.
- `COMPLETE` output must include: final recommendation/rule set and key rationale.
- `INCOMPLETE` output must include: missing inputs or blocking constraints, explicit assumptions (if any), and concrete next-step requests.

# Validation

## Required Checks
- the test does not include real I/O (no database, filesystem, network, browser, or cross-service calls)
- mocks are used appropriately: for side effects or unavoidable collaborators, not as the default

## Quality Checks (best effort)
- inline arrange is preferred over fixtures when setup is short and local
- parametrization is used only when behavior stays the same and only data changes
- state or output assertions are preferred over mock call assertions when the result is observable
- coverage checks focus on whether core decision branches and critical behaviors are exercised

## On Soft Fail
- mark status as INCOMPLETE
- continue with best-effort output
- list specific real-I/O dependencies or missing context explicitly

# Failure Handling

## Missing Context
- mark output as INCOMPLETE
- list required additional inputs explicitly (e.g., behavior contract, collaborator interfaces, expected side effects)

## Ambiguous Requirement
- if the distinction between pure unit test and integration test is unclear: stop and ask before proceeding
- if non-blocking (e.g., whether to use fixture vs inline arrange): proceed with inline-first default, list assumption explicitly

## Execution Limitation
- state the limitation explicitly in output
- do not fabricate test behavior or expected results to fill gaps

# Boundaries
- Do not define CI policy, coverage gates, or test-runner config.
- Do not cover real I/O integration tests, browser or e2e tests, or framework-specific test clients.
- Do not let coverage targets replace behavior-focused test design.

# Local references
- `examples.md`: pure unit test examples, anti-patterns, split signals, and supplementary `monkeypatch` notes
