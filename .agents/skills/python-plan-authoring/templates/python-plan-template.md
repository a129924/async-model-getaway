# <Feature / Change Name>

<!-- Copy this template into your project, rename the file to describe the feature,
     and fill in every section. All 13 sections are required. Do not delete any heading.
     Replace every placeholder with real content before handing the plan to an executor. -->

## Goal
<!-- State the single concrete outcome this change achieves. One or two sentences.
     Example: "Add validate_email(email: str) -> bool to src/utils/validation.py so
     callers can check basic email format without an external library." -->

## Non-goals
<!-- List at least 3 items stating what this change will NOT do.
     Be specific — vague entries do not constrain scope. -->
- This change will not ...
- This change will not ...
- This change will not ...

## Current Context
<!-- Briefly describe the relevant existing code, module, or system state.
     Name the specific files, classes, or functions that are affected or provide
     context. Example: "src/utils/validation.py already contains validate_url()
     and validate_phone(). The module imports only re from the standard library." -->

## Requirements
<!-- List measurable requirements. Each item must be verifiable in tests or
     validation output. Avoid vague statements like "should work correctly."
     Example:
     1. validate_email("user@example.com") returns True.
     2. validate_email("") raises ValueError. -->
1.
2.

## Decisions
<!-- Answer ALL of the following before drafting the rest of the plan.
     Leaving any item blank is a stop-and-ask condition. -->
- Async-planning status: <!-- required in every plan. Use `triggered — cite trigger evidence: ...` when async-capable evidence is present, or `exempt — cite exemption evidence: ...` when the topic stays outside the async-planning gate. This is a repo-visible contract field, not proof that a skill was invoked. -->
- Module/package placement: <!-- which module or package receives the new code -->
- New public API: <!-- yes/no — if yes, name the function/class and its signature -->
- Interface changes: <!-- yes/no — if yes, which interfaces and how -->
- Breaking changes allowed: <!-- yes/no — if yes, state the reason -->
- New dependencies: <!-- yes/no — if yes, name the package and version -->
- Error handling strategy: <!-- which exceptions are raised and when; what is returned on failure -->
- Typing strategy: <!-- fully typed, use of Any, use of TypeVar/Protocol, etc. -->

<!-- Async-planning block — keep the Async-planning status line above in all cases.
     When `Async-planning status` is `triggered`, keep the exact subsection headings below in this exact order. Delete the block for exempt topics. -->

### Async boundary decision
<!-- what stays sync, what becomes async, and why -->

### Resource lifecycle decision
<!-- who owns creation, sharing, cleanup, and closure of async clients / sessions / workers -->

### Concurrency model
<!-- direct await, bounded fan-out, batching, streaming, worker ownership, or explicit sequential execution -->

### Failure model
<!-- which failures propagate, which are translated, and how grouped failures surface -->

### Cancellation / timeout policy
<!-- cancellation owner, timeout boundary, retry boundary, cleanup behavior -->

### Validation plan
<!-- async-specific tests or validation coverage such as timeout, cancellation, cleanup, grouped failure -->

### Handoff notes for the implementer
<!-- short execution notes so implementation does not rediscover async assumptions from chat -->

### Async contradiction log
<!-- required when request, plan, review notes, or exemption-vs-trigger evidence conflict.
     Use the table below or write "No async contradictions." after checking. -->
| Contradiction | Source A | Source B | Risk impact | Decision owner / next action | Classification |
| --- | --- | --- | --- | --- | --- |
| ... | ... | ... | ... | ... | blocking / non-blocking |

## Public Contract / API Changes
<!-- Describe new or changed public functions, classes, or methods.
     Include: signatures, parameter types, return types, exceptions raised,
     and backward compatibility notes.
     If no public API changes, state "No public API changes." explicitly.

     Example:
     New function added to src/utils/validation.py:
       def validate_email(email: str) -> bool
         - Returns True for valid basic email structure.
         - Returns False for non-empty strings that fail the pattern.
         - Raises ValueError if email is empty.
     Backward compatibility: no existing signatures changed. -->

## Affected Files / Modules
<!-- Use this exact format. Name real paths — do not use placeholders like "some file". -->

Likely affected files:
-
-

Candidate files to inspect:
-

## Implementation Steps
<!-- Numbered, executable steps with explicit file references.
     Each step must name a specific file and a specific action.
     NOT acceptable: "Refactor the parser to support X."
     Acceptable: "1. Open src/parser.py. Locate the parse_line() function.
                  Add a call to validate_format() before the return statement."

     If you cannot write specific steps yet, resolve the Decisions section first. -->
1.
2.
3.

## Test Plan
<!-- Name the test file and list test cases for all five required categories.
     "Add tests" is not acceptable — be specific about what each test covers.
     If async-planning is triggered, include the async-specific validation cases named
     in `### Validation plan`. -->

Test file: `tests/test_<name>.py`

Test cases:
- Happy path: ...
- Invalid input: ...
- Edge case: ...
- Regression: ...
- Backward compatibility: ...

## Validation Commands
<!-- Choose one of the two options below. Delete the option you are not using. -->

<!-- Option A: explicit commands -->
```
pytest tests/test_<name>.py -v
mypy src/<path>/<name>.py
ruff check src/
```

<!-- Option B: reference the project config -->
```
Use existing project validation commands from pyproject.toml / Makefile / README.
```

## Risks
<!-- Name at least one concrete risk. Generic entries like "it might break something"
     are not acceptable.
     Examples:
     - "May affect existing callers of validate_url() if the import path changes."
     - "Adds a module-level compiled regex; could slow import time if the module is
       imported in a hot path." -->
-

## Rollback Plan
<!-- State how to undo this change. Name the specific files to revert.
     Example: "Revert via git: src/utils/validation.py, tests/test_validation.py.
               Remove validate_email from src/utils/__init__.py __all__ if added." -->
-

## Open Questions
<!-- List any questions that remain unresolved and who can answer them.
     If all questions are resolved, write: None -->
-
