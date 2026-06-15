# Atomic Commit Order (Test-First Enforcement)

This document defines the expected commit sequencing when implementing features from RED tests, and enforcement mechanisms to ensure tests are authored before implementation begins.

---

## Purpose

Enforce the test-first (TDD) principle: RED tests must be committed before any production code implementation begins. This prevents tests from being skipped or retrofitted after implementation.

---

## Canonical Commit Order

When a plan is approved and tests are ready (verdict: `red-tests-ready`), commits should follow this order:

### Phase 1: Test Authoring (Commit 1)
- **What**: RED tests (failing tests that encode requirements).
- **Files modified**: Only test files (e.g., `tests/models/test_user.py`).
- **Production code**: MUST NOT be modified.
- **Commit message**: `test: Add RED tests for Req#1–Req#N` (reference plan requirements).
- **Example**: `test: Add RED tests for UserAccount.create() feature (Req#1–4)`
- **Expected status**: Tests fail (RED).

### Phase 2: Production Implementation (Commit 2+)
- **What**: Implement production code to make tests pass.
- **Files modified**: Production code files (e.g., `src/models/user.py`).
- **Test files**: May be modified to fix issues (e.g., mock imports), but no new test cases should be added.
- **Commit message**: `feat: Implement UserAccount.create() to pass RED tests` or separate commits per requirement.
- **Expected status**: Tests gradually turn GREEN as implementation progresses.

### Phase 3: Refactor (Optional, Commit N)
- **What**: Clean up code, extract helpers, optimize.
- **Constraint**: All tests must still pass.
- **Commit message**: `refactor: Extract _validate_email() helper`
- **Expected status**: Tests remain GREEN throughout.

---

## Enforcement Mechanisms

### Mechanism 1: Git History Validation

Before merging a PR, verify that commits follow the order:

```bash
# Check git log for this PR
git log --oneline <branch> | head -20

# Expected pattern:
# [Most recent] feat: Implement UserAccount.create()
# [Earlier]     test: Add RED tests for UserAccount.create() feature
# [Earlier]     Previous work or main branch commits
```

**Violation example** (REJECT):
```
feat: Implement UserAccount.create()
test: Add RED tests for UserAccount.create() feature  # WRONG ORDER
```

**Correct order** (ACCEPT):
```
test: Add RED tests for UserAccount.create() feature
feat: Implement UserAccount.create()  # After tests
```

### Mechanism 2: CI/CD Gate (Optional)

Add a CI/CD check to enforce test-first order:

1. **On PR open**: Check if any production code commits exist without corresponding test commits.
   - If yes → Add comment: "Please add RED tests before production code commits."
2. **On test commit detection**: Verify tests are RED (failing) with appropriate markers.
   - If tests are GREEN → Comment: "Tests should be RED at authoring time; check for pre-existing implementations."
3. **On production code commit**: Verify all tests in that commit are either:
   - Tests modified to import/mock new code (OK, minimal changes).
   - No new test cases added (OK, only fixes to existing tests).

### Mechanism 3: Code Review Checklist

Reviewers should verify:

- [ ] Test commits precede production code commits in git history.
- [ ] Test commit modified only test files; no production code touched.
- [ ] Production code commit references the test commit (e.g., "Implements tests from <commit>").
- [ ] All tests authored in test commit are RED before production code commit.
- [ ] All tests are GREEN after production code commit (or note xfail/skip if intentional).

---

## Special Cases

### Case 1: Pass-Existing Refactor

When tests already exist and refactoring preserves behavior:

**Commit order** (different from normal):

1. **Commit 1** (optional): `test: Add boundary/edge case tests for UserAccount.create()`
   - Add any missing tests.
   - All new tests start RED.
2. **Commit 2**: `refactor: Extract _validate_email() helper`
   - Modify production code.
   - All tests (existing + new) should remain GREEN.

**Enforcement**: Same as above; no hard constraint on NEW tests being RED since refactor is focused on existing behavior.

### Case 2: Multi-Requirement Feature

When a plan has multiple requirements:

**Option A** (Atomic): Single test commit + single implementation commit
```
test: Add RED tests for Req#1–4 (UserAccount.create)
feat: Implement UserAccount.create to pass all RED tests
```

**Option B** (Incremental): Test commit + multiple implementation commits per requirement
```
test: Add RED tests for Req#1–4 (UserAccount.create)
feat(req1): Implement email validation
feat(req2): Implement password hashing
feat(req3): Implement database write
feat(req4): Implement return value
```

**Enforcement**: Test commit must still precede ALL implementation commits.

### Case 3: Insufficient Tests or Missing Requirements

If test authoring returns `needs-rework`:

**Halt implementation**. Do not start production code commits until test authoring verdict is `red-tests-ready`. This prevents:
- Skipped tests.
- Implementation-driven test writing (tests written after code, to pass existing code).
- Incomplete coverage.

---

## Enforcement Modes

### Mode 1: Soft (Recommendation)

- Commit history is checked, but not enforced by automation.
- Code reviewers verify order manually using git history.
- Violations are noted in review comments; PR can still merge with reviewer approval (e.g., if tests are retroactively added).

**When to use**: Existing projects transitioning to test-first; low-risk changes.

---

### Mode 2: Hard (Automated Blocker)

- CI/CD gate automatically rejects PRs that violate commit order.
- Test commits must precede any production code commits, verified by:
  - Scanning git history for pattern: `test:` commit before `feat:` or `fix:` commit.
  - Verifying test commits touch only `tests/` directory.
  - Failing the PR if order is violated.

**When to use**: New projects with strong test-first culture; high-risk changes.

---

### Mode 3: Hybrid (Warning + Approval)

- CI/CD detects order violations and posts a warning comment.
- PR can be merged only if:
  - A maintainer manually approves (override).
  - OR tests are re-committed in correct order.

**When to use**: Balance between flexibility and enforcement; medium-risk projects.

---

## Verification Examples

### Example 1: Correct Commit Order (ACCEPT)

```
$ git log --oneline feature/user-account | head -5

abc1234 feat: Implement UserAccount.create to pass RED tests
def5678 test: Add RED tests for UserAccount.create() (Req#1-4)
ghi9012 main: Previous work
```

**Verdict**: ACCEPT. Test commit (def5678) precedes implementation commit (abc1234).

---

### Example 2: Wrong Commit Order (REJECT in Hard Mode)

```
$ git log --oneline feature/user-account | head -5

abc1234 test: Add RED tests for UserAccount.create() (Req#1-4)
def5678 feat: Implement UserAccount.create to pass RED tests
ghi9012 main: Previous work
```

**Wait, this looks correct...** Oh! Let me reverse it. If this was the actual history, the FIRST commit (chronologically in the branch) was `feat:`, then `test:` was added later:

```
$ git log --oneline feature/user-account | head -5
# (reverse chronological order, so oldest commit is last)

test: Add RED tests...                # Commit on top (most recent)
feat: Implement UserAccount.create()  # Commit below (older)
main: Previous work                   # Oldest
```

**Verdict**: REJECT in Hard mode. Implementation commit precedes test commit.

---

### Example 3: Test Files Only in Test Commit (ACCEPT)

```
$ git show def5678 --name-only

commit def5678 - test: Add RED tests for UserAccount.create() (Req#1-4)

tests/models/test_user.py  # Test file: OK
tests/conftest.py          # Fixture file: OK

# No production files modified
```

**Verdict**: ACCEPT. Only test files touched.

---

### Example 4: Production Code Modified in Test Commit (REJECT)

```
$ git show def5678 --name-only

commit def5678 - test: Add RED tests for UserAccount.create() (Req#1-4)

tests/models/test_user.py    # Test file: OK
src/models/user.py           # Production file: VIOLATION
```

**Verdict**: REJECT. Production code modified in test commit; violates hard constraint #1.

---

## Reference

- See `behavior-change-classifier.md` for D1 verdict rules (trivial vs. non-trivial changes).
- See `codebase-evidence-levels.md` for D2 evidence strength (sufficient vs. insufficient context for test authoring).
- For enforcement implementation, see `.github/workflows/` in this repository for CI/CD configurations.

---

## Summary

1. **Phase 1**: Commit RED tests only. Production code untouched.
2. **Phase 2**: Commit implementation. Tests gradually turn GREEN.
3. **Phase 3** (optional): Refactor while keeping tests GREEN.
4. **Enforcement**: Use git history validation, CI/CD gates, and code review checklist.
5. **Violation**: Test commits AFTER production commits = violation; rebase and reorder.
6. **Special cases**: Pass-existing refactors, multi-requirement features, and insufficient tests each have guidance.
