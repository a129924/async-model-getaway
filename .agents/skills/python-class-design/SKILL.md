---
name: python-class-design
description: Design or review ordinary Python classes with clear public surfaces, disciplined instance state, thin constructors, and limited use of properties and name mangling.
complexity: medium
risk_profile:
  - ambiguity_sensitive
inputs:
  - whether the class is behavior-oriented or mainly a data carrier
  - which methods form the stable public surface
  - whether object creation needs parsing, normalization, or multiple named entry paths
  - whether state is instance-specific, shared, or lazily derived
  - whether inheritance is ordinary or collision-prone enough to justify name mangling
outputs:
  - a review-ready ordinary Python class-design rule set or skill draft
  - defaults for public surface size, constructor boundaries, properties, attribute lifecycle, and class-vs-instance state
  - local examples for common class-shape decisions, anti-patterns, and split signals
use_when:
  - designing or reviewing an ordinary behavior-oriented Python class
  - deciding what should be public vs internal on a class
  - deciding what belongs in __init__, a @classmethod factory, a @property, or a semantic method
  - reviewing instance-attribute lifecycle, class attributes, or name-mangling choices
do_not_use_when:
  - the main decision is whether the type should be an Enum, dataclass, ABC, or Protocol
  - the task is mainly about DDD layering, repository patterns, or framework-specific base classes
  - the task is mainly about naming, type-hint policy, testing style, or exception hierarchy design
---

# Purpose
Choose clear, durable class-shape rules for ordinary Python classes without drifting into dataclass selection, DDD, or broad clean-code doctrine.

# Trigger / When to use
Use this skill when:
- designing or reviewing an ordinary behavior-oriented Python class
- deciding what should be public vs internal on a class
- deciding what belongs in `__init__`, a `@classmethod` factory, a `@property`, or a semantic method
- reviewing instance-attribute lifecycle, class attributes, or name-mangling choices

Do not use this skill when:
- the main decision is whether the type should be an `Enum`, `dataclass`, `ABC`, or `Protocol`
- the task is mainly about DDD layering, repository patterns, or framework-specific base classes
- the task is mainly about naming, type-hint policy, testing style, or exception hierarchy design

# Inputs
- whether the class is behavior-oriented or mainly a data carrier
- which methods form the stable public surface
- whether object creation needs parsing, normalization, or multiple named entry paths
- whether state is instance-specific, shared, or lazily derived
- whether inheritance is ordinary or collision-prone enough to justify name mangling

# Process
1. Keep the skill on ordinary behavior-oriented classes; leave plain data carriers and `dataclass`-style models to `python-model-selection`.
2. Make the public surface small and stable; default helper logic, orchestration, and implementation detail to `_single_leading_underscore` names, and prefer short public-method docstrings when they clarify business intent.
3. Keep `__init__` thin: accept already-normalized data, do final cheap invariant checks, and assign attributes rather than hosting heavy setup logic.
4. When construction needs named intent, parsing, or external-data normalization, move that work into a clearly named `@classmethod` factory such as `from_xxx` or `create_xxx`.
5. Define instance attributes deliberately and usually fully in `__init__`; allow delayed attributes only for explicit lazy-cache or memoization cases.
6. Use `@property` sparingly for read-only exposure, compatibility, or cheap derived views; default against `@property.setter` when a semantic method would express state changes better.
7. Reserve `__double_leading_underscore` for narrow subclass-collision cases; do not use it as the default notion of "private" in Python.
8. Keep mutable per-instance state on the instance, not in class-level shared containers; treat method ordering only as a readability aid, not a hard gate.

# Examples
- Positive: Keep `_balance` private, expose `balance` as a cheap read-only property, and use `deposit()` / `withdraw()` as the public command surface; move payload parsing into `from_api_payload()`.
- Negative: Put parsing and branching in `__init__`, mutate business state through `@property.setter`, store per-user mutable lists on the class, or use `__double_leading_underscore` everywhere as fake hard privacy.

# Outputs
- a review-ready ordinary Python class-design rule set or skill draft
- defaults for public surface size, constructor boundaries, properties, attribute lifecycle, and class-vs-instance state
- local examples for common class-shape decisions, anti-patterns, and split signals

# Boundaries
- Do not restate `python-model-selection` rules for `Enum`, `dataclass`, `ABC`, or `Protocol`.
- Do not turn method ordering into a hard repository-wide style gate.
- Do not define DDD entity/value-object policy, framework mixin rules, or package/module layout policy.

# Validation
Before proceeding, confirm:
- The class is behavior-oriented (not mainly a data carrier or model construct)
- The class orientation and inheritance topology are clear enough to apply rules

**SOFT FAIL** — ask and wait before continuing:
- Class orientation is unclear (behavior vs data carrier) → ask whether to apply class-design rules or redirect to `python-model-selection`
- Inheritance topology is ambiguous and collision risk for name mangling cannot be assessed → ask before recommending `__double_leading_underscore`

**BLOCKED** — stop and redirect:
- The main decision is whether the type should be `Enum`, `dataclass`, `ABC`, or `Protocol` → redirect to `python-model-selection`
- The task is DDD layering, framework-specific base classes, or plugin systems → out of scope for this skill

# Failure Handling
- **Missing Context**: if class orientation, public-surface intent, or inheritance topology are unknown, ask once clearly before applying defaults.
- **Ambiguous Requirement**: if the stated goal conflicts with class-design boundaries (e.g., the class is clearly a data carrier), name the conflict, propose redirecting to `python-model-selection`, and wait for confirmation.
- **Execution Limitation**: if the task is outside scope (e.g., DDD layering, naming policy, testing style), stop and redirect to the appropriate skill.

# Local references
- `examples.md`: class-shape examples, anti-patterns, factory/property choices, name-mangling notes, and split signals
