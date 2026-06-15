# Test quality criteria

## What makes a good unit test

- **Behavioral**: tests observable behavior (return value, state change, important side effect), not implementation wiring.
- **Self-contained**: each test can run independently; no dependency on global state from other tests.
- **Named clearly**: test name encodes the scenario and expected outcome (`test_<unit>_<scenario>_<expected>`).
- **One assertion focus**: the primary assertion is obvious; secondary assertions support the story.
- **No real I/O**: no real filesystem, network, database, or external service calls. Use mocks or fakes.
- **Parametrized appropriately**: `pytest.mark.parametrize` when only data varies and the behavior is the same.

## What makes a bad unit test

| Issue | Severity |
|---|---|
| No assertions at all | `blocking` |
| Assertion on an internal implementation detail instead of behavior | `warning` |
| Real I/O without explicit justification (should be integration test) | `warning` |
| `assert True` or `assert result is not None` with no behavioral meaning | `warning` |
| Every internal call is mocked (tests the wiring, not the behavior) | `warning` |
| No coverage of the core decision branches | `warning` |
| Test name does not indicate what is being verified | `info` |
| No parametrization when 3+ identical-structure cases differ only in data | `info` |

## Coverage signal

This skill does not enforce a hard coverage gate. Note obviously untested branches as
`info` or `warning`. For branch-coverage policy, defer to the project's CI configuration.
