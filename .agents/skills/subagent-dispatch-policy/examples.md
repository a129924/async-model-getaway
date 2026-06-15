# subagent-dispatch-policy examples

## Positive: implementation dispatch

Input:

- one bounded task slice: update the accepted implementation artifact set
- real dispatch conditions: all present
- no registry or runtime dependency

Output:

```json
{
  "next_role": "Implementer",
  "reason": "The task slice requires concrete artifact edits inside the bounded write set.",
  "stop_condition": "none"
}
```

## Positive: planning clarification dispatch

Input:

- one bounded task slice
- frozen truth is ambiguous for the current slice
- real dispatch conditions: all present

Output:

```json
{
  "next_role": "Planner",
  "reason": "The current slice cannot proceed until frozen planning truth is clarified.",
  "stop_condition": "none"
}
```

## Negative: path-based target

Bad input:

- "dispatch this to `.github/agents/python-implementation-workflow.agent.md`"

Bad output:

```json
{
  "next_role": ".github/agents/python-implementation-workflow.agent.md",
  "reason": "That file is the implementation owner.",
  "stop_condition": "none"
}
```

Why it is invalid:

- targets must be role names only
- compatibility-surface paths are not canonical dispatch targets

## Negative: hidden role simulation

Bad input:

- no separated result payload exists
- the Observer plans to "pretend reviewer said PASS"

Required output:

```json
{
  "next_role": "stop",
  "reason": "Real dispatch is not established because the result payload would be simulated by the Observer.",
  "stop_condition": "missing explicit result payload"
}
```

## Negative: runtime-expansion request

Input:

- the request requires launcher wiring or runtime orchestration semantics

Output:

```json
{
  "next_role": "stop",
  "reason": "The task expands beyond the bounded Observer baseline.",
  "stop_condition": "runtime orchestration semantics required"
}
```
