---
name: python-api-signature
description: Design or review public Python function and method signatures for safe defaults, clear parameter ordering, and explicit call-site contracts.
complexity: medium
risk_profile: [ambiguity_sensitive]
inputs:
  - whether the API is public or internal
  - whether None is a legal business value or only a missing/default signal
  - whether the call site becomes ambiguous with positional arguments
  - whether flags, modes, or repeated related values are crowding the signature
  - whether the signature is wide enough to deserve a parameter object
outputs:
  - a review-ready public Python API-signature rule set or review guide
  - defaults for safe parameter values, sentinel usage, ordering, keyword-only choices, and refactor signals
  - local examples for common signature smells, safer alternatives, and split signals
use_when:
  - designing or reviewing a public Python function or method signature
  - deciding whether defaults, keyword-only parameters, or sentinel patterns make an API safer
  - reviewing boolean flags, broad *args / **kwargs, or crowded parameter lists
  - deciding when a signature should be refactored into a clearer parameter object
do_not_use_when:
  - the main task is type-annotation syntax, strict typing policy, or container-type selection
  - the main task is choosing Enum, dataclass, ABC, or Protocol
  - the main task is ordinary class-shape design, naming policy, or error hierarchy design
---

# Purpose
Choose clear, safe public Python signature rules without drifting into full type-hint policy, class design, or runtime model selection.

# Trigger / When to use
Use this skill when:
- designing or reviewing a public Python function or method signature
- deciding whether defaults, keyword-only parameters, or sentinel patterns make an API safer
- reviewing boolean flags, broad `*args` / `**kwargs`, or crowded parameter lists
- deciding when a signature should be refactored into a clearer parameter object

Do not use this skill when:
- the main task is type-annotation syntax, strict typing policy, or container-type selection
- the main task is choosing `Enum`, `dataclass`, `ABC`, or `Protocol`
- the main task is ordinary class-shape design, naming policy, or error hierarchy design

# Inputs
- whether the API is public or internal
- whether `None` is a legal business value or only a missing/default signal
- whether the call site becomes ambiguous with positional arguments
- whether flags, modes, or repeated related values are crowding the signature
- whether the signature is wide enough to deserve a parameter object

# Process
1. Keep the skill on public signature shape; defer all concrete type-hint rules to `python-type-hints-strict`.
2. Ban mutable default values such as `[]`, `{}`, `set()`, and other shared mutable objects; prefer `None` plus fresh per-call initialization when emptiness is the real default.
3. Allow immutable defaults such as `None`, numbers, strings, booleans, tuples, frozensets, enum members, and stable constants when they match the API contract.
4. Use `None` as the default missing signal when `None` is not itself a valid business value; use a private sentinel such as `_MISSING` only when the API must distinguish "not provided" from "explicitly passed as None".
5. Keep parameter order predictable: required parameters first, then defaulted ones, then varargs only when truly needed, then keyword-only parameters.
6. Prefer keyword-only parameters when positional calls would hide intent, especially for boolean flags or easily confused same-shape values.
7. Treat a single boolean flag as a caution case and two or more boolean flags as a strong refactor signal; prefer semantic methods, clearer mode parameters, or a parameter object.
8. Reject broad public `*args` / `**kwargs` by default; allow them only for narrow wrapper, adapter, or framework-required signatures, and extract a parameter object when the explicit signature becomes too wide.

# Examples
- Positive: Use `tags: tuple[str, ...] = ()` for a fixed immutable default, or `items: list[str] | None = None` plus per-call initialization; force `send_notify` to be keyword-only when the flag must remain.
- Negative: Ship `def send(items: list[str] = []): ...`, hide public options in `**kwargs`, or stack multiple boolean flags into one crowded signature.

# Outputs
- a review-ready public Python API-signature rule set or review guide
- defaults for safe parameter values, sentinel usage, ordering, keyword-only choices, and refactor signals
- local examples for common signature smells, safer alternatives, and split signals

# Boundaries
- Do not define strict type-annotation syntax or typing escape hatches; use `python-type-hints-strict` for that.
- Do not choose the concrete parameter-object model; use `python-model-selection` when the API should extract one.
- Do not define class internals, naming rules, or framework-specific hook conventions beyond narrow signature-shape exceptions.
- Do not cover positional-only parameters (`/`) in the first draft except as an explicit out-of-scope note.

# Validation
Before proceeding, confirm:
- The question is about signature shape (parameters, defaults, keyword-only choices, refactor signals)
- Enough context exists to determine whether `None` is a legal business value and whether the API is public or internal

**SOFT FAIL** — ask and wait before continuing:
- Whether `None` is a legal business value or only a missing-signal is unstated → ask before choosing `None` vs a private sentinel
- Whether the API is public or internal is unstated → ask before applying keyword-only defaults and refactor thresholds

**BLOCKED** — stop and redirect:
- The main task is type-annotation syntax, strict typing policy, or container-type selection → redirect to `python-type-hints-strict`
- The main task is choosing `Enum`, `dataclass`, `ABC`, or `Protocol` for the parameter object → redirect to `python-model-selection`

# Failure Handling
- **Missing Context**: if `None`-semantics, public-vs-internal scope, or call-site ambiguity are unknown, ask once clearly before applying defaults.
- **Ambiguous Requirement**: if the stated goal conflicts with signature-shape scope (e.g., the question is really about type-hint syntax), name the conflict and redirect.
- **Execution Limitation**: if the task is outside scope (e.g., class internals, naming policy, framework-specific hooks), stop and redirect to the appropriate skill.

# Local references
- `examples.md`: mutable-default examples, sentinel patterns, keyword-only and flag cases, fat-signature refactors, and split signals
