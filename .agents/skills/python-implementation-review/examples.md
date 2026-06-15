# Python Implementation Review Examples

Use these examples after `SKILL.md` has already confirmed that an approved
`*.plan.md` and implementation (diff or file set) are both available.

---

## Example 1: Approved — all steps done, no scope creep, contract matches, tests present

### Plan (relevant sections)

```markdown
## Non-goals
- No changes to the CLI interface
- No changes to logging configuration

## Public Contract / API Changes
- New function: `def validate_email(address: str) -> bool` added to `src/validators/__init__.py`

## Implementation Steps
1. Create `src/validators/email_validator.py` with `validate_email(address: str) -> bool`
2. Re-export `validate_email` from `src/validators/__init__.py`
3. Update `CHANGELOG.md` with the new public function entry

## Test Plan
- Happy path: valid email address returns `True` — in `tests/test_email_validator.py`
- Invalid input: malformed email (missing `@`) returns `False` — in `tests/test_email_validator.py`
- Edge case: empty string returns `False` — in `tests/test_email_validator.py`
```

### Implementation diff summary

- `src/validators/email_validator.py` created; line 1 defines `def validate_email(address: str) -> bool`
- `src/validators/__init__.py` line 5: `from .email_validator import validate_email`
- `CHANGELOG.md` line 3: entry for `validate_email`
- No changes to `src/cli.py` or any logging module
- `tests/test_email_validator.py` contains `test_valid_email` (line 12), `test_malformed_email` (line 20), and `test_empty_string` (line 28)

### Verdict output

```yaml
verdict: approved

traceability_matrix:
  - step: "Create src/validators/email_validator.py with validate_email(address: str) -> bool"
    status: done
    evidence: "src/validators/email_validator.py:1"
  - step: "Re-export validate_email from src/validators/__init__.py"
    status: done
    evidence: "src/validators/__init__.py:5"
  - step: "Update CHANGELOG.md with the new public function entry"
    status: done
    evidence: "CHANGELOG.md:3"

scope_creep_check:
  - non_goal: "No changes to the CLI interface"
    violated: no
    evidence: "clean"
  - non_goal: "No changes to logging configuration"
    violated: no
    evidence: "clean"

contract_check:
  - item: "def validate_email(address: str) -> bool in src/validators/__init__.py"
    status: matches
    detail: "Signature, return type, and re-export location all match the plan"

test_plan_check:
  - case_type: "happy path (valid email → True)"
    status: present
    location: "tests/test_email_validator.py:12"
  - case_type: "invalid input (malformed email → False)"
    status: present
    location: "tests/test_email_validator.py:20"
  - case_type: "edge case (empty string → False)"
    status: present
    location: "tests/test_email_validator.py:28"
```

---

## Example 2: Needs-rework — missing implementation step

### Plan (relevant section)

```markdown
## Implementation Steps
1. Create `src/validators/email_validator.py` with `validate_email(address: str) -> bool`
2. Re-export `validate_email` from `src/validators/__init__.py`
3. Update `CHANGELOG.md` with the new public function entry
```

### Implementation diff summary

- `src/validators/email_validator.py` created ✓
- `src/validators/__init__.py` updated ✓
- `CHANGELOG.md` is unchanged — step 3 not done

### Verdict output

```yaml
verdict: needs-rework

traceability_matrix:
  - step: "Create src/validators/email_validator.py with validate_email(address: str) -> bool"
    status: done
    evidence: "src/validators/email_validator.py:1"
  - step: "Re-export validate_email from src/validators/__init__.py"
    status: done
    evidence: "src/validators/__init__.py:5"
  - step: "Update CHANGELOG.md with the new public function entry"
    status: missing
    evidence: "not found"

scope_creep_check:
  - non_goal: "No changes to the CLI interface"
    violated: no
    evidence: "clean"
  - non_goal: "No changes to logging configuration"
    violated: no
    evidence: "clean"

contract_check:
  - item: "def validate_email(address: str) -> bool in src/validators/__init__.py"
    status: matches
    detail: "Signature and location match the plan"

test_plan_check:
  - case_type: "happy path (valid email → True)"
    status: present
    location: "tests/test_email_validator.py:12"
  - case_type: "invalid input (malformed email → False)"
    status: present
    location: "tests/test_email_validator.py:20"
  - case_type: "edge case (empty string → False)"
    status: present
    location: "tests/test_email_validator.py:28"
```

**Why this is `needs-rework`:** Implementation Step 3 (`CHANGELOG.md` update) has no evidence in the diff. The step is `missing`, not `partial`, because no changelog entry was added at all. The reviewer must not mark this `approved` and note the gap as a comment — it must return `needs-rework`.

---

## Example 3: Needs-rework — scope creep (Non-goals boundary violated)

### Plan (relevant section)

```markdown
## Non-goals
- No changes to the CLI interface
- No changes to logging configuration
```

### Implementation diff summary

- All 3 Implementation Steps are done ✓
- `src/cli.py` line 42: new argument `--validate-email` added to the argument parser — this is inside the Non-goals boundary

### Verdict output

```yaml
verdict: needs-rework

traceability_matrix:
  - step: "Create src/validators/email_validator.py with validate_email(address: str) -> bool"
    status: done
    evidence: "src/validators/email_validator.py:1"
  - step: "Re-export validate_email from src/validators/__init__.py"
    status: done
    evidence: "src/validators/__init__.py:5"
  - step: "Update CHANGELOG.md with the new public function entry"
    status: done
    evidence: "CHANGELOG.md:3"

scope_creep_check:
  - non_goal: "No changes to the CLI interface"
    violated: yes
    evidence: "src/cli.py:42"
  - non_goal: "No changes to logging configuration"
    violated: no
    evidence: "clean"

contract_check:
  - item: "def validate_email(address: str) -> bool in src/validators/__init__.py"
    status: matches
    detail: "Signature and location match the plan"

test_plan_check:
  - case_type: "happy path (valid email → True)"
    status: present
    location: "tests/test_email_validator.py:12"
  - case_type: "invalid input (malformed email → False)"
    status: present
    location: "tests/test_email_validator.py:20"
  - case_type: "edge case (empty string → False)"
    status: present
    location: "tests/test_email_validator.py:28"
```

**Why this is `needs-rework`:** The CLI change at `src/cli.py:42` falls inside the "No changes to the CLI interface" Non-goal boundary. The fact that all Implementation Steps are done does not override the scope-creep finding. Do not rationalize that the CLI addition is "just a helper flag" or "backward-compatible" — any Non-goals violation is an automatic `needs-rework`.

---

## Example 4: Needs-rework — unauthorized contract deviation

### Plan (relevant section)

```markdown
## Public Contract / API Changes
- Modified function: `def process(data: str) -> Result` in `src/processor.py`
  - Behaviour change: raises `ValueError` on empty input instead of returning `Result(ok=False)`
```

### Implementation diff summary

- `src/processor.py`: function signature is `def process(data: str, strict: bool = False) -> Result`
- The `strict` parameter was not in the plan and is not mentioned anywhere in the Public Contract section
- The `ValueError` on empty input is present ✓

### Verdict output

```yaml
verdict: needs-rework

traceability_matrix:
  - step: "Update process() in src/processor.py to raise ValueError on empty input"
    status: done
    evidence: "src/processor.py:18"

scope_creep_check:
  - non_goal: "No changes to the public retry logic"
    violated: no
    evidence: "clean"

contract_check:
  - item: "def process(data: str) -> Result in src/processor.py"
    status: deviation
    detail: "Implementation signature is def process(data: str, strict: bool = False) -> Result. The `strict` parameter was not authorized in the plan's Public Contract section."

test_plan_check:
  - case_type: "happy path (non-empty data returns Result)"
    status: present
    location: "tests/test_processor.py:9"
  - case_type: "invalid input (empty string raises ValueError)"
    status: present
    location: "tests/test_processor.py:17"
```

**Why this is `needs-rework`:** Adding `strict: bool = False` changes the public function signature even though the default value preserves backward compatibility at the call site. The Public Contract section does not authorize this parameter. The rationale "it has a default value so it's safe" is a known rationalization — any undocumented signature addition is a contract deviation and requires `needs-rework`. The plan must be updated and re-approved before the parameter is accepted.

---

## Example 5: Refuse case — plan not yet approved by python-plan-review

### Request

> Here is the implementation diff for the email validator feature. The plan looks
> good — the team agreed on it in the PR description. Please review the implementation.

### Correct behavior

Do not begin tracing. The plan has not been formally approved by `python-plan-review` (or equivalent). A team agreement in a PR description or chat message does not satisfy the approval precondition.

Return a refusal that routes the requester back to the correct gate:

```
Refusal: The plan has not been formally approved by python-plan-review.

python-implementation-review requires a plan that has passed python-plan-review
(or the project's equivalent plan-review gate) before tracing begins.

Required action: Route the plan through python-plan-review first. Once the plan
bears a formal approved verdict, resubmit both the approved plan and this
implementation diff for implementation review.
```

**Why this is the correct behavior:** Running implementation review against an unapproved plan means tracing an implementation against a contract that may still change. If the plan is later revised, the implementation review result becomes invalid. The approval gate is a precondition, not a courtesy check. Do not proceed even if the implementation diff looks straightforward.

---

## Anti-pattern summary

| Anti-pattern | Why it fails |
| --- | --- |
| Accept informal plan approval ("team agreed in chat") | Approval precondition requires a formal verdict from `python-plan-review` |
| Mark a step `done` when only part of it is implemented | Partial work is `partial`, not `done`; the verdict stays `needs-rework` |
| Skip Non-goals check because "no one would add that" | Every Non-goals item must be explicitly scanned |
| Treat a new optional parameter as a harmless addition | Any signature change not in the plan is a contract deviation |
| Assume tests are present because the test file exists | Case types must be verified by substance, not file existence |
| Include code style or typing feedback in the verdict | Code quality belongs to `python-code-review`, not here |
| Return `approved` with a note about a small gap | Any gap that does not meet `done` / `matches` / `present` requires `needs-rework` |
