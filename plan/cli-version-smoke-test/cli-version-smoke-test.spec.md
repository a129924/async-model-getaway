# cli-version-smoke-test Specification

## Acceptance Criteria

1. The existing `async-model-gateway` entrypoint can print a stable version
   string when invoked through explicit version flags on the current CLI
   surface.
2. `--version` and `-V` produce the same version output, with a trailing
   newline and no stderr noise on success.
3. The default no-argument entrypoint behavior continues to print
   `async-model-gateway foundation scaffold`.
4. Unsupported arguments do not silently reuse the version path and fail
   through a non-zero CLI exit path.
5. The version surface uses one package-local Python source of truth and does
   not depend on runtime parsing of `pyproject.toml`.

## Behavioral Scenarios

### Scenario 1: Explicit version request
- **Given**: the package entrypoint is imported from `async_model_gateway`
- **When**: `main(["--version"])` or `main(["-V"])` is invoked
- **Then**: the CLI prints the same stable version string
- **Then**: the output ends with a newline
- **Then**: stderr remains empty

### Scenario 2: Default scaffold path stays stable
- **Given**: the package entrypoint is invoked with no arguments
- **When**: `main()` or `main([])` runs
- **Then**: the CLI prints `async-model-gateway foundation scaffold`
- **Then**: the version string is not printed implicitly

### Scenario 3: Unsupported argument fails cleanly
- **Given**: the package entrypoint receives an unsupported argument
- **When**: `main([...])` runs with that unsupported input
- **Then**: the CLI does not print the version string
- **Then**: the call fails through a non-zero CLI exit path

## Error / Edge Cases

- Short and long version flags must remain behaviorally identical.
- Empty argv input must remain backward-compatible with the current scaffold
  path.
- Unsupported arguments must not expand the scope into a general-purpose CLI
  parser.
- Any implementation that needs new files, new dependencies, or runtime
  `pyproject.toml` parsing is outside this smoke-test contract and must return
  to planning.
