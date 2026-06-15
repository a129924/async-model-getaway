# Tooling detection rules and severity calibration

## Detection priority order

The skill inspects project files in this order and stops at the first positive match.
It does NOT execute any tools — it reads configuration to calibrate judgment.

| Priority | File | What to look for |
|---|---|---|
| 1 | `pyproject.toml` | `[tool.mypy]`, `[tool.pyright]`, `[tool.ruff]`, `[tool.flake8]`, `[tool.pylint]` |
| 2 | `Makefile` | Targets named `lint`, `typecheck`, `type-check`, `test`, `check` |
| 3 | `README.md` / `CONTRIBUTING.md` | Validation commands, e.g., `ruff check .`, `mypy src/`, `pytest` |
| 4 | Fallback | None found; apply generic Python best-practice defaults |

## How detected tooling calibrates severity

- `[tool.pyright]` with `strict = true` or `[tool.mypy]` with `strict = true`:
  - `Any` annotations → `blocking`
  - Missing annotations on any public API → `blocking`
  - `# type: ignore` without inline comment → `blocking`
- `[tool.pyright]` without strict or `[tool.mypy]` without strict:
  - Missing annotations on public APIs → `warning`
  - `Any` with inline justification → `warning`
- `[tool.ruff]` or `[tool.flake8]`:
  - Naming violations, unused imports → `warning` (or `blocking` if the config sets them as errors)
- Generic fallback:
  - Apply PEP 8 and standard Python best practices
  - Missing annotations on public APIs → `warning` (never `blocking` in fallback mode)
  - Hard-discouraged anti-patterns still flagged as `blocking`
  - No strict-mode typing rules applied

Record `tooling_detected: generic fallback (no pyproject.toml or Makefile found)` in output when fallback applies.

## Severity classification

| Severity | Definition | Verdict impact |
|---|---|---|
| `blocking` | A correctness issue, a security risk, a hard anti-pattern, or a strict-mode violation. The code must not be merged as-is. | Triggers `needs-rework` |
| `warning` | A quality issue that should be addressed soon. Does not block merge on its own, but accumulation of warnings is a signal to address before the next review cycle. | Does not trigger `needs-rework` alone |
| `info` | An optional improvement, style note, or readability suggestion. Low urgency. | Does not trigger `needs-rework` |

**Verdict rule:**
- `approved` — zero `blocking` findings across all 7 dimensions.
- `needs-rework` — one or more `blocking` findings.

**Escalation:**
- A `warning` may be escalated to `blocking` if the reviewer judges the cumulative risk is
  unacceptable. State the escalation rationale explicitly in the finding.
