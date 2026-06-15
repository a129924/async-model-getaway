---
name: python-type-hints-strict
description: Define or enforce Python type-hint rules for projects that run pyright in strict mode. Use this when drafting typing guidance or reviewing code against a strict typing baseline.
complexity: medium
risk_profile: [ambiguity_sensitive]
inputs:
  - the Python version and typing baseline
  - any allowed escape hatches
  - repository policy or examples that already constrain typing
  - whether a repo-owned or domain type already exists for the position under review
  - whether a proposed `object` site is a true untrusted boundary or narrowing-helper input
outputs:
  - a review-ready strict typing rule set or skill draft
  - explicit allowed and disallowed typing patterns
  - an explicit decision order for repo-owned types, refinements, and boundary-only `object`
  - local reference files for compatibility rules, edge cases, and anti-patterns
use_when:
  - a project mandates `pyright --strict`
  - code review must decide whether a typing pattern is acceptable
  - a coding standard needs a strict type-hint section
do_not_use_when:
  - the task is only about naming conventions
  - the task mainly chooses runtime models or control-flow style
---

# Purpose
Define one strict typing contract for Python code that must pass `pyright --strict`.

# Trigger / When to use
Use this skill when:
- a project mandates `pyright --strict`
- code review must decide whether a typing pattern is acceptable
- a coding standard needs a strict type-hint section

Do not use this skill when:
- the task is only about naming conventions
- the task mainly chooses runtime models or control-flow style

# Inputs
- the Python version and typing baseline
- any allowed escape hatches
- repository policy or examples that already constrain typing
- whether a repo-owned or domain type already exists for the position under review
- whether a proposed `object` site is a true untrusted boundary or narrowing-helper input

# Process
1. Start from `pyright --strict` as the default baseline.
2. Require explicit parameter and return annotations on public functions and methods.
3. Match syntax to the supported Python version: for Python 3.10+ prefer `User | None`; for Python 3.9+ prefer `list[str]`; for Python 3.8/3.9 compatibility use `Optional[User]`, `Union[...]`, and `List[str]` where needed.
4. Before accepting `object`, check whether a repo-owned alias, value type, model, protocol, or other concrete domain type already exists for that position.
5. If a repo-owned or domain type already exists, keep or reuse it; changing that position to `object` is invalid unless the position is a true untrusted boundary or narrowing-helper input.
6. If no existing repo-owned type fits, prefer an explicit refinement or named alias before considering `object`.
7. Allow `object` only at true untrusted boundaries or narrowing-helper inputs such as decoder output, validator input, or type-guard input, and narrow it back to a precise type before normal business use.
8. Require every surviving `object` usage to include a short justification naming the boundary or narrowing role it serves.
9. Limit `Any`, `cast`, and ignore comments to explicit, justified edge cases.
10. Put reusable compatibility notes, object-boundary rules, and escape-hatch rules in `reference.md`, and put version-path examples and strict typing anti-patterns in `examples.md`.

# Examples
- Positive: Reuse an existing repo-owned type such as `UserId` or `UserPayload` for normal APIs; if a validator or `TypeGuard` helper accepts `object`, add a short note such as `boundary: external JSON payload` and narrow immediately back to the precise type.
- Negative: Change a known service parameter or return type from a repo-owned/domain type to `object`, or justify `object` with convenience phrases such as `easier type checking` or `not sure of the type yet`.

# Outputs
- a review-ready strict typing rule set or skill draft
- explicit allowed and disallowed typing patterns
- an explicit decision order for repo-owned types, refinements, and boundary-only `object`
- local reference files for compatibility rules, edge cases, and anti-patterns

# Boundaries
- Do not choose between `Enum`, `dataclass`, `ABC`, or `Protocol`.
- Do not define naming policy or branch-selection rules.
- Do not relax strict typing without an explicit repository-level exception.
- Do not allow `object` to replace ordinary repo-owned parameters, returns, or service-layer contracts when a stronger type already exists.

# Validation

Before proceeding, confirm:
- **Python version target known**: which Python baseline (3.8, 3.9, 3.10+) governs syntax choices?
- **Escape-hatch list available**: are allowed uses of `Any`, `cast`, and `# type: ignore` defined?
- **Repository typing policy present**: are there existing type-hint examples or constraints that must be respected?
- **Repo-owned type check completed**: for each proposed `object` site, is there already a repo-owned alias, value type, model, protocol, or other concrete domain type for that position?
- **Boundary justification present**: does every surviving `object` usage name the true untrusted boundary or narrowing-helper role it serves, and is the value narrowed quickly?

**SOFT FAIL** — ask and wait before continuing:
- Python version target is unknown → cannot determine correct syntax (e.g., `User | None` vs `Optional[User]`); ask before outputting any rule
- Escape-hatch list is undefined → cannot declare which patterns are disallowed; ask before proceeding
- No existing repo typing examples or policy → flag the gap and ask whether to establish a baseline from scratch or infer from existing code
- A proposed `object` usage has no short boundary or narrowing justification → flag it as incomplete and ask for the missing justification before accepting it

**BLOCKED** — stop and redirect:
- Task is choosing between `Enum`, `dataclass`, `ABC`, or `Protocol` → redirect to `python-model-selection`
- Task is naming conventions or branch-selection style → redirect to `python-naming` or `python-control-flow`
- `object` is proposed only because the author is unsure of the domain type or wants a placeholder → stop, reuse the repo-owned type if it exists, or refine the contract explicitly before continuing

# Failure Handling

## Missing Context
- If Python version, escape-hatch rules, existing policy, or whether a repo-owned type already exists cannot be determined, mark output as INCOMPLETE and list the missing inputs before proceeding.

## Ambiguous Requirement
- If blocking: stop and ask whether the position is a true untrusted boundary or narrowing-helper input before accepting `object`.
- If non-blocking: proceed with the strictest contract-preserving assumption and document it explicitly.

## Execution Limitation
- State the limitation explicitly in the output.
- Do not fabricate a typing rule or placeholder `object` annotation that cannot be justified from the available inputs.

# Local references
- `reference.md`: strict typing defaults, compatibility rules, `object` boundary rules, and allowed exceptions
- `examples.md`: version-path examples, `object` boundary cases, and strict typing anti-patterns
