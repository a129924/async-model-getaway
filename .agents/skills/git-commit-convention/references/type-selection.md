# Commit type selection

Use commit type to describe the dominant semantic effect of the staged change.

## Primary mapping

- `feat`: adds a user-visible capability or business flow
- `fix`: corrects broken behavior, wrong data, wrong output, or bad UX
- `refactor`: restructures implementation without intended behavior change
- `test`: adds or improves tests as the main purpose
- `docs`: changes documentation as the main purpose
- `chore`: maintenance work such as dependency or config upkeep
- `style`: formatting-only or presentation-only code changes with no logic change
- `perf`: measurable performance improvement as the main purpose
- `ci`: CI workflow or automation policy changes
- `build`: build-system or packaging changes
- `revert`: reverts an earlier commit

## Business-language rule

Choose the type from the business effect, then write the subject from that same effect.

- Better: `fix(查詢): 修正排序條件遺失造成結果錯亂`
- Worse: `fix: rename sort helper`

If the user-facing effect is "broken behavior now works," default to `fix` even if the implementation touched error classes, parsing helpers, or schema glue.

## Breaking changes

Use `!` when callers, operators, or downstream integrations must change.

- `feat!(api): ...`
- `fix!(cli): ...`

Breaking changes still need a body that explains migration impact.
