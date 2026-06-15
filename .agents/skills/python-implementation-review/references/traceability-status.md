# Traceability Status Definitions and Test Plan Coverage Rules

## Traceability step status definitions

| Status | Definition |
| --- | --- |
| `done` | The full change described by the step is present in the implementation |
| `partial` | Only part of the described change is present; the step is not fully complete |
| `missing` | No relevant code change corresponding to this step can be found |

A step must be `done` to count toward `approved`. `partial` triggers `needs-rework`.

## Test Plan coverage rules

A test case type is `present` when:
- a test function containing logic that exercises that case type exists
- the test is in the file named in the plan (if the plan names a file)

A test case type is `missing` when:
- no test function covering that case type can be found
- the plan names a specific file and the case is not in that file

Do not infer test coverage from function names alone. Verify that the test body
exercises the case logic described in the Test Plan.
