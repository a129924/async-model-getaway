# Semantic Boundaries with Adjacent Skills

Three skills work together in sequence on any Python implementation task:

```
python-plan-review  →  python-implementation-review  →  python-code-review
       ↑                         ↑                              ↑
 "Can the plan be          "Does the code                "Is the code
  executed without          satisfy the                   good Python?"
  guessing?"                approved plan?"
```

## python-plan-review

- **Question it answers:** Can this plan be executed without guessing?
- **Input:** the plan document
- **Output:** plan verdict (`approved` / `needs-rework`)
- **Does not do:** review code

## python-implementation-review (this skill)

- **Question it answers:** Does the implementation satisfy the approved plan?
- **Input:** an approved plan AND the implementation diff or file set
- **Output:** implementation verdict (`approved` / `needs-rework`) with traceability matrix
- **Does not do:** review code style, typing, linting, or architecture quality

## python-code-review

- **Question it answers:** Is this good Python code?
- **Input:** the implementation (code diff or file set)
- **Output:** code review with findings
- **Does not do:** check plan completeness or scope

## Why the sequence matters

`python-code-review` optimizes code quality. Running it before
`python-implementation-review` risks spending review effort on code that is
structurally incomplete or has scope-crept beyond the plan boundary. The correct
gate order is:

1. Plan approved → implementation built → `python-implementation-review` passes
2. Only then: `python-code-review`
