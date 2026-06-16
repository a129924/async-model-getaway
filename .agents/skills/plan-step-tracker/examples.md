# Examples — plan-step-tracker

## Setup: Sample `.step.md` File

```yaml
---
topic: my-feature
phase: implementation
created: 2025-01-15
---

# my-feature — Step Tracking

## Workflow Stages
- [X] plan-authoring
- [X] plan-review
- [ ] implementation
- [ ] implementation-review
- [ ] code-review

## Implementation Steps

### Phase 1: Core
- [X] 1. Setup environment
- [ ] 2. Implement main logic
- [X] 3. Add basic tests

### Phase 2: Polish
- [ ] 4. Write documentation
- [x] 5. Code review (lowercase—incorrect)
- [ ] 6. Integration tests
```

---

## Operation 1: `read_all` — List All Steps

Returns both done and pending steps.

### Python CLI

```bash
$ python skills/plan-step-tracker/scripts/step_tracker.py read_all my-feature
[X] plan-authoring
[X] plan-review
[ ] implementation
[ ] implementation-review
[ ] code-review
[X] 1. Setup environment
[ ] 2. Implement main logic
[X] 3. Add basic tests
[ ] 4. Write documentation
[x] 5. Code review
[ ] 6. Integration tests
```

**Output**: 11 lines (5 workflow stage + 6 implementation checkboxes)
**Exit code**: 0
**Note**: Lowercase `[x]` included; Agent should see the formatting inconsistency

### Grep Fallback

```bash
$ grep '^\- \[.\]' plan/my-feature/my-feature.step.md
- [X] plan-authoring
- [X] plan-review
- [ ] implementation
- [ ] implementation-review
- [ ] code-review
- [X] 1. Setup environment
- [ ] 2. Implement main logic
- [X] 3. Add basic tests
- [ ] 4. Write documentation
- [x] 5. Code review
- [ ] 6. Integration tests
```

---

## Operation 2: `read_not_run` — List Pending Steps Only

Returns only steps with `[ ]` or `[x]` (pending markers).

### Python CLI

```bash
$ python skills/plan-step-tracker/scripts/step_tracker.py read_not_run my-feature
[ ] implementation
[ ] implementation-review
[ ] code-review
[ ] 2. Implement main logic
[ ] 4. Write documentation
[x] 5. Code review
[ ] 6. Integration tests
```

**Note**: Stderr warning issued:
```
Warning: Found lowercase [x] at line 25; treating as pending
```

**Output**: 7 lines (3 pending workflow stages + 4 pending implementation steps)
**Exit code**: 0

### Grep Fallback

```bash
$ grep '^\- \[ \]' plan/my-feature/my-feature.step.md
- [ ] implementation
- [ ] implementation-review
- [ ] code-review
- [ ] 2. Implement main logic
- [ ] 4. Write documentation
- [ ] 6. Integration tests
```

**Limitation**: Grep catches only space-bracket `[ ]`, not lowercase `[x]`. Combine with:
```bash
$ grep '^\- \[[ x]\]' plan/my-feature/my-feature.step.md  # captures both [ ] and [x]
```

---

## Operation 3: `read_success` — List Completed Steps Only

Returns only steps with `[X]` (done marker).

### Python CLI

```bash
$ python skills/plan-step-tracker/scripts/step_tracker.py read_success my-feature
[X] plan-authoring
[X] plan-review
[X] 1. Setup environment
[X] 3. Add basic tests
```

**Output**: 4 lines (2 done workflow stages + 2 done implementation steps)
**Exit code**: 0

### Grep Fallback

```bash
$ grep '^\- \[X\]' plan/my-feature/my-feature.step.md
- [X] plan-authoring
- [X] plan-review
- [X] 1. Setup environment
- [X] 3. Add basic tests
```

---

## Operation 4: `check_all_succeeded` — Verify Completion & Block if Pending

Returns SUCCESS if all done; BLOCKED if any pending.

### Scenario A: All Steps Done

```bash
$ python skills/plan-step-tracker/scripts/step_tracker.py check_all_succeeded my-feature-complete
✅ SUCCESS: All 3 steps complete
```

**Exit code**: 0 (allows continuation)

### Scenario B: Pending Steps Exist (BLOCKING)

```bash
$ python skills/plan-step-tracker/scripts/step_tracker.py check_all_succeeded my-feature
❌ BLOCKED: 7 steps pending (exit code 1)
[ ] implementation
[ ] implementation-review
[ ] code-review
[ ] 2. Implement main logic
[ ] 4. Write documentation
[x] 5. Code review
[ ] 6. Integration tests
```

**Exit code**: 1 (blocks CI/workflow)

**Agent must halt**: When exit code is 1, Agent should **STOP** and report pending steps. Proceeding further violates the blocking contract.

### Grep Fallback (Manual Blocking)

```bash
# Count pending steps
PENDING=$(grep -c '^\- \[ \]' plan/my-feature/my-feature.step.md)
if [ $PENDING -eq 0 ]; then
  echo "SUCCESS: All steps complete"
  exit 0
else
  echo "BLOCKED: $PENDING steps pending"
  grep '^\- \[ \]' plan/my-feature/my-feature.step.md
  exit 1
fi
```

---

## Edge Case 1: Empty File

File contains only frontmatter, no checkbox lines.

```yaml
---
topic: empty-topic
phase: planning
created: 2025-01-15
---

# empty-topic — No Steps Yet
```

### Behavior

```bash
$ python skills/plan-step-tracker/scripts/step_tracker.py read_all empty-topic
# (empty output)

$ python skills/plan-step-tracker/scripts/step_tracker.py read_not_run empty-topic
# (empty output)

$ python skills/plan-step-tracker/scripts/step_tracker.py check_all_succeeded empty-topic
✅ SUCCESS: All 0 steps complete
```

**Exit code**: 0 (no pending = success)

---

## Edge Case 2: `.step.md` File Not Found

Topic directory exists but `.step.md` is missing.

```bash
$ python skills/plan-step-tracker/scripts/step_tracker.py read_all nonexistent-topic
Error: File not found: plan/nonexistent-topic/nonexistent-topic.step.md
```

**Exit code**: 1 (error signal)

**Agent behavior**: Should treat as blocking condition; report file missing and halt.

---

## Edge Case 3: No Checkbox Lines in File

File contains headings and text but no `- [ ]` or `- [X]` lines.

```markdown
---
topic: no-checkboxes
created: 2025-01-15
---

# Setup Guide

Follow these steps manually:
1. Install dependencies
2. Configure environment
3. Run tests
```

### Behavior

```bash
$ python skills/plan-step-tracker/scripts/step_tracker.py read_all no-checkboxes
# (empty output)

$ python skills/plan-step-tracker/scripts/step_tracker.py check_all_succeeded no-checkboxes
✅ SUCCESS: All 0 steps complete
```

**Exit code**: 0 (no items to track = not a failure)

---

## Integration Example: CI Blocking Workflow

```bash
#!/bin/bash
set -e

TOPIC="my-feature-release"

echo "Checking step completion before release..."

# Fetch pending steps
PENDING=$(python skills/plan-step-tracker/scripts/step_tracker.py read_not_run "$TOPIC")

if [ $? -ne 0 ]; then
  echo "FAIL: Unable to check steps"
  exit 1
fi

# Use check_all_succeeded for blocking gate
python skills/plan-step-tracker/scripts/step_tracker.py check_all_succeeded "$TOPIC"
CHECK_EXIT=$?

if [ $CHECK_EXIT -ne 0 ]; then
  echo "Release blocked: pending steps remain"
  exit 1
fi

echo "All steps complete; proceeding with release..."
# deploy, publish, etc.
```

---

## Common Pitfalls

| Pitfall | What goes wrong | How to avoid |
| --- | --- | --- |
| Lowercase `[x]` | Not recognized as done; treated as pending + warning issued | Always use uppercase `[X]` for done steps |
| Skipping blank lines in frontmatter | Parser may miss or double-count lines | Use grep pattern `^\- \[.\]` to filter strictly |
| Querying wrong path | Python CLI looks for `plan/<topic>/<topic>.step.md`; user provides wrong name | Always match directory name with topic name exactly |
| Ignoring exit codes | Agent proceeds despite exit 1 (blocking) | Always check `$?` or `exitCode` after CLI calls |
| Modifying `.step.md` manually | Breaks consistency with plan execution | Use this skill for **read-only** queries only; modify steps through plan execution |
