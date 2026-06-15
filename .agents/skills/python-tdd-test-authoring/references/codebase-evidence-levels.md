# Codebase Evidence Levels (D2)

This document defines the D2 evidence classifier for determining whether the plan and codebase provide sufficient context to author RED tests.

---

## Purpose

The D2 classifier measures the **completeness and clarity of evidence** needed to author tests:

- **Insufficient** = Plan is too vague, incomplete, or missing key details. Cannot author tests confidently.
- **Minimal** = Plan has basic requirements but some clarification may be needed during test authoring. Proceed with caution.
- **Sufficient** = Plan has clear, specific requirements; test structure exists; existing tests provide patterns. Proceed with confidence.

---

## Evidence Classification (D2)

### Insufficient Context

One or more of the following apply:

1. **Plan not approved**: Plan lacks stakeholder or reviewer approval.
2. **Requirements are vague**: Requirements use unclear language like "improve", "handle", "better", "edge cases" without specifics.
3. **No examples or acceptance criteria**: Plan does not show what success looks like or how to verify the change.
4. **No test structure detected**: No existing test files or test directories; unclear where tests should live.
5. **Public API undefined**: Plan does not specify which functions, methods, or classes are public/affected.
6. **Error cases not listed**: Plan does not document which error conditions should be handled or tested.
7. **State/side effects unclear**: Plan does not describe what state changes or side effects should occur.

**Verdict**: Return `insufficient-context`. Do not proceed to test authoring. Ask for clarifications:
- "Requirements section must be approved."
- "Req#3 is too vague; specify the edge cases."
- "Test structure not found; where should tests live?"

**Examples**:
- ❌ "Create login flow" (vague; what steps? what errors? what data?)
- ❌ "Improve error handling" (unclear; for which errors? what should the new behavior be?)
- ✓ "Add validation to reject emails with leading/trailing whitespace; raise InvalidEmailError with message containing the raw email."

---

### Minimal Evidence

One or more of the following apply, but not all requirements are clear:

1. **Plan is approved** but requirements are somewhat vague.
2. **Test structure exists** but patterns are unclear (e.g., fixtures, mocking style).
3. **Some requirements are specific**, others are general.
4. **Error cases are partially listed**.
5. **Public API is mostly clear**, but edge cases are not enumerated.

**Verdict**: `minimal_evidence`. Proceed to test authoring with caution:
- Author tests for the specific requirements.
- For vague requirements, ask clarifying questions or make reasonable assumptions (and document them).
- May need to re-map or add tests as implementation reveals missed cases.

**Example**:
- ✓ "Create UserAccount.create(email, password) method. Must validate email and hash password."
- ⚠️ But no mention of: What happens if email is invalid? How is password hashing verified? What if database write fails?
- **Action**: Author tests for what is clear; ask or assume reasonable behaviors for unclear parts.

---

### Sufficient Evidence

All of the following apply:

1. **Plan is approved** by stakeholder or reviewer.
2. **Requirements are specific and measurable**: Each requirement states exactly what behavior should occur (e.g., "reject emails with leading whitespace" instead of "validate email").
3. **Test structure exists**: Existing test directory, file naming conventions, fixtures, and test patterns are evident.
4. **Public API is explicit**: Plan clearly lists which functions, methods, classes, or error types are public.
5. **Error cases are enumerated**: Plan lists specific error conditions and expected behavior for each.
6. **State/side effects are documented**: Plan describes what state changes or external interactions occur (e.g., "write to database", "send email").
7. **Examples or acceptance criteria are provided**: Plan shows example inputs/outputs or how to verify success.

**Verdict**: `sufficient_evidence`. Proceed with confidence to test authoring.

**Example**:
```
Plan: Add UserAccount.create(email: str, password: str) → UserAccount

Requirements:
- Req#1: Validate email format (RFC 5322). Raise InvalidEmailError if invalid.
- Req#2: Hash password using bcrypt. Store hashed password, never plaintext.
- Req#3: Write new UserAccount record to database. Raise DatabaseError if write fails.
- Req#4: Return UserAccount object with id, email, created_at fields.

Error Cases:
- InvalidEmailError: email is malformed (e.g., leading/trailing whitespace, no @, invalid domain).
- PasswordTooWeakError: password < 8 characters.
- DatabaseError: database write fails (connection error, constraint violation, etc.).

Acceptance Criteria:
- Test: create(email="user@example.com", password="securePass123") returns UserAccount with id > 0.
- Test: create(email=" user@example.com", password="...") raises InvalidEmailError.
- Test: Password is hashed; stored value != plain password.
```

---

## D2 Decision Tree

```
Is the plan approved?
│
├─ NO → Insufficient context
│
└─ YES → Are requirements specific and measurable?
    │
    ├─ NO (mostly vague) → Insufficient context
    │
    └─ YES (mostly specific) → Do error cases and examples exist?
        │
        ├─ NO (mostly missing) → Minimal evidence
        │
        └─ YES (mostly documented) → Is test structure apparent?
            │
            ├─ NO → Minimal evidence (can infer; proceed with caution)
            │
            └─ YES → Sufficient evidence (proceed with confidence)
```

---

## Examples

### Example 1: Insufficient Context

```
Plan Snippet:
- Req#1: Create UserAccount class
- Req#2: Add validation
- Req#3: Handle errors better
- Req#4: Improve performance

Status: DRAFTED (not yet approved)
Test Structure: Unknown
Error Cases: Not listed
Public API: Unclear which methods are public
```

**D2 Analysis**:
- Plan approved? NO
- Requirements specific? NO (vague)
- Error cases documented? NO
- Test structure? UNKNOWN

**Verdict**: `insufficient_context`

**Action**: "Plan must be approved. Requirements are too vague. Specify error cases and public API."

---

### Example 2: Minimal Evidence

```
Plan Snippet:
- Req#1: Add login(username, password) method. Must authenticate against user database.
- Req#2: Return User object if valid, raise InvalidCredentialsError if not.
- Req#3: ???

Status: APPROVED
Test Structure: tests/auth/test_login.py exists (similar tests in same file)
Error Cases: InvalidCredentialsError mentioned; other cases unclear
Public API: login() is public; internal helpers undefined
```

**D2 Analysis**:
- Plan approved? YES
- Requirements specific? MOSTLY (Req#1-2 specific; Req#3 missing)
- Error cases? PARTIAL (one listed; edge cases not enumerated)
- Test structure? YES (but patterns may need clarification)

**Verdict**: `minimal_evidence`

**Action**: "Proceed to test authoring. Ask about Req#3. Author tests for login success, InvalidCredentialsError. Assume reasonable behaviors for edge cases (e.g., empty username, null password). Add tests as needed."

---

### Example 3: Sufficient Evidence

```
Plan Snippet:
- Req#1: Add UserAccount.create(email: str, password: str) → UserAccount
  - Validate email format (RFC 5322). Raise InvalidEmailError if invalid.
  - Hash password with bcrypt. Store hashed password.
  - Write to database. Raise DatabaseError if write fails.
  - Return UserAccount(id, email, created_at).

Error Cases:
  - InvalidEmailError: email malformed or has leading/trailing whitespace.
  - PasswordTooWeakError: password < 8 characters.
  - DatabaseError: database write fails.

Public API: UserAccount.create() class method, InvalidEmailError, PasswordTooWeakError.

Acceptance Criteria:
  - create(email="valid@test.com", password="secure1234") returns UserAccount.
  - create(email=" valid@test.com", password="...") raises InvalidEmailError.
  - Password is hashed before storage.

Status: APPROVED
Test Structure: tests/models/test_user.py exists with 15+ tests showing pytest patterns, fixtures.
```

**D2 Analysis**:
- Plan approved? YES
- Requirements specific? YES
- Error cases? YES (all enumerated)
- Test structure? YES (clear patterns)
- Public API? YES (explicit)

**Verdict**: `sufficient_evidence`

**Action**: "Proceed with confidence. Author tests covering all 3 requirements, all 3 error cases, happy path, boundary (password length), state (hashed password). Use existing test patterns."

---

## Usage in python-tdd-test-authoring Skill

When the skill encounters insufficient or minimal evidence during test authoring:

1. **Insufficient context** → Return verdict `insufficient-context` with specific gaps listed.
2. **Minimal evidence** → Proceed cautiously; flag assumptions in test_mapping and next_step.
3. **Sufficient evidence** → Proceed with confidence; return `red-tests-ready` if all other checks pass.

---

## Reference

See `atomic-commit-order.md` for how evidence levels influence commit sequencing and test-first requirements.
