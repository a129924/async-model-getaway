# ONNX minimal executor invocation boundary steps

## Workflow Stages

- [X] fresh-plan-review
- [X] human-implementation-clearance
- [X] fresh-red-tests
- [X] implementation
- [X] focused-pytest
- [X] full-pytest
- [X] strict-pyright-witnesses
- [X] global-pyright
- [X] ruff
- [X] lock-check
- [X] diff-check
- [X] implementation-review
- [X] code-review
- [ ] commit-push-ready-pr-codex-review

## Implementation Steps

- [X] 1. Write fresh RED tests and strict type witness without production source edits.
- [X] 2. Add the internal ONNX session Protocol and private direct-await executor.
- [X] 3. Replace ONNX binding/composition erasure with the exact generic chain.
- [X] 4. Run the declared validation sequence and update fresh evidence.
