---
name: python-code-review
description: Review Python code quality across typing, lint, readability, error handling, anti-patterns, test quality, and observability. Use this after python-implementation-review has already approved the implementation against the plan.
complexity: high
risk_profile:
  - ambiguity_sensitive
  - multi_agent_handoff
inputs:
  - Python source files under review (or git diff)
  - Project tooling config (pyproject.toml, Makefile, README.md, CONTRIBUTING.md) — absence acceptable
  - Confirmation that python-implementation-review has already approved the implementation
outputs:
  - verdict: approved | needs-rework
  - tooling_detected: detected tools or "generic fallback"
  - findings: per-dimension list with severity, location, issue, and fix
use_when:
  - A Python implementation has already passed python-implementation-review
  - A code review must assess quality independent of plan alignment
  - A PR is being evaluated for merge readiness on quality grounds
do_not_use_when:
  - python-implementation-review has not yet run or has returned needs-rework
  - The task is to compare code against a plan document (use python-implementation-review)
  - The task is only about naming conventions (use python-naming)
  - The task is only about type hints in isolation (use python-type-hints-strict)
  - The task is only about test structure in isolation (use python-testing-pytest)
  - The task is only about error handling in isolation (use python-error-handling)
---

# Purpose

Judge whether a Python implementation meets quality standards across seven dimensions:
typing correctness, lint compliance, readability/maintainability, error handling discipline,
anti-pattern avoidance, test quality, and logging/observability.

This skill does NOT check whether code matches the plan — that is `python-implementation-review`.
This skill does NOT decide whether a feature should be built — that is planning.
This skill does NOT dictate which tools must be installed — it auto-detects and adapts.

# Trigger / When to use

Use this skill when:
- a Python implementation has already passed `python-implementation-review`
- a code review must assess code quality independent of plan alignment
- a PR is being evaluated for merge readiness on quality grounds

Do NOT use this skill when:
- `python-implementation-review` has not yet run or has returned `needs-rework`
- the task is to compare code against a plan document (use `python-implementation-review`)
- the task is only about naming conventions (use `python-naming`)
- the task is only about type hints in isolation (use `python-type-hints-strict`)
- the task is only about test structure in isolation (use `python-testing-pytest`)
- the task is only about error handling in isolation (use `python-error-handling`)

# Inputs

- The Python source files under review (or git diff)
- The project's `pyproject.toml`, `Makefile`, `README.md`, or `CONTRIBUTING.md` (used for tooling detection; absence is acceptable)
- Confirmation that `python-implementation-review` has already approved the implementation

# Process

## Step 0 — Sequencing gate (MUST execute first)

Confirm that `python-implementation-review` has already approved this implementation.

- If confirmation is absent or the implementation has not been reviewed: **refuse**, output a routing message, and stop.
  > "Sequencing gate: python-implementation-review must approve the implementation before python-code-review runs. Please run python-implementation-review first."

## Step 1 — Detect project tooling

Inspect the project in this order and stop at the first positive match:

1. **`pyproject.toml`** — check for `[tool.mypy]`, `[tool.pyright]`, `[tool.ruff]`, `[tool.flake8]`
2. **`Makefile`** — check for `lint`, `typecheck`, `test` targets
3. **`README.md` / `CONTRIBUTING.md`** — check for validation command references
4. **Fallback** — no tooling found; apply generic Python best-practice judgment without failing

Record detected tools in the output as `tooling_detected`. Use detected configuration to frame judgment — for example, if `[tool.pyright]` has `strict = true`, then `Any` usage is flagged as blocking.

The skill does NOT execute tools. It reads configuration to calibrate severity.

## Step 2 — Review all 7 quality dimensions

For each dimension, record findings with severity, location, issue, and fix:

| Severity | Meaning |
|---|---|
| `blocking` | Must fix before approval |
| `warning` | Should fix; not a hard blocker |
| `info` | Optional improvement or style note |

### Dimension 1 — Typing

- Public functions and methods must have parameter and return annotations.
- In strict-mode projects (`pyright strict` or `mypy --strict`): `Any`, `cast`, and `# type: ignore` without inline justification are `blocking`.
- In non-strict projects: missing annotations on public APIs are `warning`; missing on private helpers are `info`.
- Implicit `Optional` (e.g., `def f(x: str = None)`) is always `blocking`.
- `# type: ignore` without an inline comment explaining why is always `warning`.

### Dimension 2 — Lint

- Unused imports are `warning`.
- Naming violations (PEP 8 by default; project linting config overrides) are `warning`.
- Inconsistent style that the detected linter would flag is `warning`.
- Anything the detected linter config marks as error-level becomes `blocking`.

### Dimension 3 — Readability / Maintainability

- Functions longer than 50 lines: flag as `warning`; do not auto-fail.
- Deeply nested logic (more than 3 levels): `warning`.
- Nested list comprehensions beyond 2 levels: `warning`.
- Unclear names that make intent ambiguous: `info`.
- Magic numbers without named constants: `info`.

### Dimension 4 — Error handling

- `except:` (bare) or `except Exception:` without re-raise or logging: `blocking`.
- Bare `pass` in an exception handler (silently swallows the error): `blocking`.
- Missing specific exception types where the failure mode is known: `warning`.
- Exception chaining omitted (`raise X from exc` not used): `warning`.

### Dimension 5 — Anti-patterns

Hard-discouraged (always `blocking`):
- `except:` or `except Exception:` without re-raise or logging (also Dimension 4)
- Mutable default arguments: `def f(x=[])` or `def f(x={})`
- `__getattr__` / `__setattr__` used for general attribute routing when not a proxy/adapter — for full escape-hatch rules, see `python-descriptors-attribute-access`
- `eval()` / `exec()` without explicit sandboxing justification documented in code
- Implicit `Optional`: `def f(x: str = None)` without `Optional[str]` or `str | None`

Flag with context (explain when acceptable — `warning` unless justified):
- `# type: ignore` without an inline comment explaining why
- `Any` type annotation in strict-mode projects
- Very long functions (>50 lines) — flag, do not auto-fail
- Nested list comprehensions beyond 2 levels

### Dimension 6 — Test quality

If test files are included in the review:
- Tests with no assertions: `blocking`.
- Tests that test implementation details (mock every internal call) rather than observable behavior: `warning`.
- No parametrization when only data varies: `info`.
- Real I/O (filesystem, network, DB) in unit tests without justification: `warning`.
- Assertion messages absent when the failing message would be ambiguous: `info`.
- Coverage signal: note obviously untested branches; do not enforce a hard coverage gate.

### Dimension 7 — Logging / Observability

- `print()` used where structured logging is expected: `warning`.
- `logging.debug()` used for information that operators need in production: `warning`.
- Sensitive data (passwords, tokens, PII) logged at any level: `blocking`.
- Exceptions caught and silently swallowed without any log: `blocking` (overlaps Dimension 4).
- Log messages without context (no variable interpolation for dynamic state): `info`.

## Step 3 — Output verdict

Aggregate findings across all dimensions:
- `approved`: zero `blocking` findings.
- `needs-rework`: one or more `blocking` findings.

# Examples

## Positive — clean implementation, approved

`UserService.create_user` with full type hints, specific exception handling, structured
logging, and a test asserting returned state. Tooling: `pyproject.toml` with `[tool.ruff]`
and `[tool.pyright]` (non-strict). Result: `approved` — one `info` finding (magic number),
no `blocking` findings. See **examples.md Example 1** for full output.

## Negative — needs-rework: bare except + mutable default

```python
def add_item(items=[], value=None):
    try:
        items.append(value)
    except:
        pass
```

Generic fallback tooling. Result: `needs-rework` — three `blocking` findings: mutable
default argument (`items=[]`), bare `except:`, and bare `pass` in handler.
See **examples.md Example 4** for full output.

# Outputs

```
verdict: approved | needs-rework
tooling_detected: <detected tools or "generic fallback">

findings:
  typing:
    - severity: blocking | warning | info
      location: file:line
      issue: "..."
      fix: "..."
  lint: [...]
  readability: [...]
  error_handling: [...]
  anti_patterns: [...]
  test_quality: [...]
  observability: [...]
```

Each finding includes `severity`, `location`, `issue`, and `fix`.
Dimensions with no findings are emitted as empty lists `[]`.

# Validation

## Required Checks

- Code diff or source files must be provided; the review cannot proceed without reviewable content.
- Confirmation that `python-implementation-review` has already approved this implementation must be present before any dimension is assessed.

## Quality Checks (best effort)

- All 7 quality dimensions are reviewed: typing, lint, readability, error handling, anti-patterns, test quality, observability.
- All findings are recorded with severity, location, issue, and fix — even when not blocking.
- Detected tooling is recorded and used to calibrate severity (e.g., strict-mode escalation for `pyright strict`).
- Dimensions with no findings are emitted as empty lists `[]`, not omitted.

## On Soft Fail

- If code is not provided: mark the review INCOMPLETE; list which axes could not be assessed; do not emit a verdict.
- If only some files are available (e.g., test files omitted): note the gap explicitly in the findings; review available code only.

# Failure Handling

## Missing Context

BLOCKED — if no code diff or file content is provided, stop immediately and request the missing input before proceeding. Do not emit a partial verdict.

## Ambiguous Requirement

If code is present but surrounding context (project conventions, caller intent) is unclear: note the assumption explicitly in the output and proceed. Do not block; flag any finding that depends on the assumed context with an `info`-level note.

## Execution Limitation

If referenced test files, dependency modules, or configuration files cannot be inspected: state the limitation explicitly in the output; review only the code that is available; do not fabricate findings for unseen code.

# Boundaries

- Do not check whether the code matches the plan document — that is `python-implementation-review`.
- Do not decide whether the feature should be built — that is planning.
- Do not execute lint, type-check, or test tools — read configuration to calibrate judgment.
- Do not enforce a hard coverage gate — note obviously untested branches as `info` or `warning`.
- Do not apply strict-mode typing rules unless the project's configuration enables strict mode.
- Do not flag `__getattr__` / `__setattr__` usage without first checking the escape-hatch conditions in `python-descriptors-attribute-access`.
- Do not approve an implementation if `python-implementation-review` has not already run.

**Cross-skill signposts:**
- `python-implementation-review` — verifies code matches the plan; must run before this skill
- `python-type-hints-strict` — deep strict-mode typing guidance
- `python-testing-pytest` — deep unit test design guidance
- `python-error-handling` — deep exception hierarchy and translation guidance
- `python-descriptors-attribute-access` — `__getattr__` / `__setattr__` escape-hatch conditions

# Local references

- `reference.md`: short overview index — names and roles of all split reference files
- `references/tooling-detection.md`: detection priority order, severity calibration per tool, fallback behavior, and verdict rules
- `references/anti-patterns.md`: hard-discouraged patterns (always `blocking`) and contextual patterns (`warning` unless justified)
- `references/test-quality.md`: good vs bad unit test criteria and coverage signal guidance
- `references/observability.md`: log level discipline, structured logging preference, and what to flag
- `references/cross-skill-signposts.md`: routing table — which skill owns each adjacent topic
- `examples.md`: full worked examples — approved case, needs-rework cases (bare except, strict-mode typing, mutable default), tooling fallback case, and sequencing-gate refusal case
