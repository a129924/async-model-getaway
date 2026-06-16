# Behavior-Change Classifier (D1)

This document defines the D1 classifier rules for determining whether a change is **trivial** (skip test authoring) or **non-trivial** (require test authoring).

---

## Purpose

The D1 classifier makes a binary decision: Is this change significant enough to require RED test authoring before implementation?

- **Trivial** = Skip test authoring. Examples: doc-only, config-only, dependency upgrades with no API changes, comment-only.
- **Non-trivial** = Require test authoring. Examples: new feature, bug fix, refactor, API change, error handling improvement.

---

## Classifier Rules (D1)

### Trivial (skip test authoring)

The change is trivial if **ALL** of the following are true:

1. **No public API changes**: Function signatures, class methods, return types, or error types are unchanged.
2. **No behavior changes**: The system behaves identically from the caller's perspective.
3. **No new error conditions**: No new exceptions or error paths.
4. **One of these applies**:
   - Documentation-only (docstrings, comments, README updates; no code changes).
   - Configuration-only (config files, environment variables; no code changes).
   - Dependency upgrade (with no API changes to code using the dependency).
   - Internal refactor with zero observable behavior change (e.g., rename a private variable, extract a helper function).
   - Comment-only or whitespace-only (no functional changes).

**D1 output**: `{ "verdict": "trivial", "reason": "<reason>" }` (e.g., `doc_only`, `config_only`, `internal_refactor`).

---

### Non-Trivial (require test authoring)

The change is non-trivial if **ANY** of the following are true:

1. **New public function or method**: A new function, class method, or public interface is added.
2. **Changed public API**: Function signature, return type, or error type is modified.
3. **New behavior**: New feature, business logic, or side effect is introduced.
4. **Bug fix**: Behavior is changed to fix a defect (e.g., validation now rejects previously-accepted inputs).
5. **Error handling improvement**: New error conditions, error messages, or exception types are added.
6. **Refactor with observable behavior change**: Refactor where the external contract changes or new edge cases emerge.
7. **State or side effect change**: Code now writes to database, filesystem, cache, or other external system in a new way.

**D1 output**: `{ "verdict": "non-trivial", "reason": "<change_type>" }` (e.g., `feature`, `bug_fix`, `refactor`, `error_handling`, `api_change`).

---

## D1 Decision Tree

```
Does the change involve any new public API, new behavior, or bug fixes?
│
├─ YES → D1 = non-trivial
│   │ (Classify: feature, bug_fix, refactor, api_change, error_handling, etc.)
│   └─ Proceed to test authoring
│
└─ NO → Is it doc-only, config-only, or internal refactor?
    │
    ├─ YES → D1 = trivial
    │   └─ Skip test authoring
    │
    └─ NO → Unclear. Review plan and requirements again.
        └─ If still unclear, classify as D1 = non-trivial (conservative default)
```

---

## Examples

### Example 1: Non-Trivial (Feature)

**Change**: Add `UserAccount.create(email, password)` class method.

**D1 Analysis**:
- New public API? YES (new method).
- New behavior? YES (user creation logic).
- Error handling? YES (validation errors for email, password).

**D1 output**: `{ "verdict": "non-trivial", "reason": "feature" }`

**Action**: Require test authoring.

---

### Example 2: Trivial (Doc-Only)

**Change**: Update docstrings in `UserAccount` class and add type hints to existing methods (no code logic changes).

**D1 Analysis**:
- New public API? NO (signatures unchanged).
- New behavior? NO (type hints are metadata).
- Bug fix? NO.

**D1 output**: `{ "verdict": "trivial", "reason": "doc_only" }`

**Action**: Skip test authoring.

---

### Example 3: Non-Trivial (Bug Fix)

**Change**: Fix bug in `UserAccount.create()`: now rejects emails with leading/trailing whitespace.

**D1 Analysis**:
- API unchanged? YES (method signature same).
- Behavior changed? YES (previously accepted `" user@example.com "`, now rejects).
- Bug fix? YES.

**D1 output**: `{ "verdict": "non-trivial", "reason": "bug_fix" }`

**Action**: Require test authoring. Tests must verify the new behavior (rejection of whitespace).

---

### Example 4: Trivial (Internal Refactor)

**Change**: Extract private method `_validate_email()` from `UserAccount.create()`. Public behavior unchanged; all existing tests still pass.

**D1 Analysis**:
- New public API? NO (only private method extracted).
- Public behavior changed? NO (create() still works the same).
- Observable change? NO.

**D1 output**: `{ "verdict": "trivial", "reason": "internal_refactor" }`

**Action**: Skip test authoring. Existing tests already cover the behavior.

---

### Example 5: Non-Trivial (Config + API Change)

**Change**:
- Add new config file `config.yaml` for database connection strings.
- Change `get_user(id)` method signature: now accepts both `id: int` and `user_ref: UserRef`.

**D1 Analysis**:
- Config change: trivial on its own.
- API change? YES (signature changed).

**Overall D1 output**: `{ "verdict": "non-trivial", "reason": "api_change" }` (the API change dominates; config is secondary).

**Action**: Require test authoring for the new `user_ref` parameter path.

---

### Example 6: Trivial (Dependency Upgrade, No API Change)

**Change**: Upgrade `requests` library from 2.28.0 to 2.31.0. No code changes in `src/` or `tests/`.

**D1 Analysis**:
- Code changed? NO.
- API changed? NO.
- Behavior changed? NO (just dependency update).

**D1 output**: `{ "verdict": "trivial", "reason": "dependency_upgrade" }`

**Action**: Skip test authoring. (Possibly run existing tests to verify compatibility, but no new tests needed.)

---

## Boundary Rules

1. **When in doubt, classify as non-trivial**. It is safer to author tests and later mark them as "pass_existing" than to skip test authoring for a change that actually needs coverage.

2. **D1 decision gates the verdict in python-tdd-test-authoring skill**. If D1 says `trivial`, the skill must honor it and return `skip_with_reason`. If D1 says `non-trivial` but `spec.md` is missing, skill-level verdict must be `BLOCKED` and route to plan-authoring.

3. **D1 is agnostic to test authoring difficulty**. Even if test authoring is complex, if the change is non-trivial, test authoring is required.

4. **`insufficient-context` is a skill-level verdict, not a D1 verdict**. D1 output is always `{ "verdict": "trivial|non-trivial", "reason": "..." }`.

---

## Reference

See `references/codebase-evidence-levels.md` for guidance on evidence strength (insufficient, minimal, sufficient) when deciding whether the plan provides enough context to author tests.
