# Python library-architecture reference

Use this reference after `SKILL.md` narrows the task to reusable library/package architecture rather than package layout or application architecture.

## Architecture frame

- A theme is one coherent capability slice inside a single library or SDK-style package.
- Themes may expose different operations, but they should not depend on each other directly.
- This skill is about logical dependency direction inside one reusable package, not about physical repo layout or framework layers.

## Hard rules

### 1. Themes stay isolated

- Cross-theme imports are forbidden with zero exceptions.
- If `orders/` needs something from `catalog/`, the design is wrong even when the shared code looks small.
- Keep local duplication when the reused code is still theme-specific. Promote only truly shared contracts or semantic primitives.
- If a peer import appears during review, repair it by promoting a shared contract into `core` or by moving orchestration up into the facade/client.

### 2. `core` is the shared contract center

- `core/` is the recommended baseline name for multi-theme libraries.
- `kernel/` or `base/` can be acceptable when they clearly mean the same shared-contract role.
- `common/` and `utils/` are not acceptable substitutes for `core`; they encourage dump-zone behavior.
- `core` may contain shared contracts, semantic identifiers, shared base errors, pagination/result wrappers, and other pure support logic that multiple themes or entry points genuinely share.
- `core` must stay side-effect-free. It must not own transport clients, persistence adapters, environment loading, retry loops, auth refresh flows, or package bootstrap.

### 3. Promote shared contracts instead of sharing peer code

- If a contract crosses theme boundaries, promote it into `core`.
- If a contract crosses an external boundary and multiple themes depend on that shared meaning, promote that contract into `core` too.
- Promote the contract or semantic primitive, not the whole peer implementation.
- Convenience alone is not enough reason to move code into `core`; shallow helper extraction often creates a grab bag instead of a real shared contract center.

### 4. Keep dependency direction one-way

| Part | May depend on | Must not depend on |
| --- | --- | --- |
| `core` | local pure helpers only | themes, adapters, facade/client, transport code |
| theme | its own modules, `core` | other themes, facade/client |
| adapter | its owning theme, `core`, external libraries | unrelated themes, facade/client internals |
| facade/client | themes, adapters, `core` | caller application code, web/CLI handlers, peer facade/client internals |

- Do not push facade/client orchestration down into `core` to reduce imports or hide bootstrap complexity.
- Keep auth coordination, transport/retry setup, and multi-theme flow orchestration at the facade/client or in a dedicated adapter that owns that flow.

### 5. Facade/client is the composition root

- Prefer one primary facade/client entry point for the package's public composition root.
- A bounded secondary entry point can be acceptable when it remains orchestration-only and does not become a parallel architecture lane.
- Themes should not construct sibling themes directly.
- The facade/client may coordinate auth, transport, retries, or multi-theme flows, but `core` must not.

## Review checklist

A reusable library/package architecture is sound when:

- every theme depends inward on `core` rather than sideways on peer themes
- `core` contains shared contracts and pure support logic, not outward orchestration
- shared contracts that appear in multiple themes or shared external flows are promoted into `core`
- adapters stay attached to their owning theme instead of becoming a hidden shared layer
- the facade/client is the consumer-facing composition root
- package review does not rely on `common/` or `utils/` as a substitute for `core`

## Smells and rationalizations

Watch for these anti-patterns during review:

- a theme imports another theme "just for one model" or "just for one helper"
- `core` starts making HTTP calls, building sessions, reading environment variables, or coordinating retries
- a so-called shared module mostly contains unrelated helpers with no clear contract meaning
- secondary clients become parallel architecture stacks instead of bounded composition wrappers

Challenge these rationalizations directly:

- "It is only one import." → One exception becomes the rule; promote the shared contract or move composition up.
- "We already had a `common/` folder." → Rename alone is not enough; define a real `core` role and remove dump-zone leftovers.
- "Putting auth refresh in `core` makes it reusable." → Shared behavior is not the same as shared contract; orchestration still belongs outside `core`.
- "The tooling says imports are fine." → Tooling is supplementary; architecture rules and review judgment stay primary.

## Optional tooling stays supplementary

- Tools such as `import-linter` or Tach can help encode the no-cross-theme rule.
- They do not replace the portable architecture contract.
- Passing a tool check does not justify a bad `core`, and not using a tool does not weaken the zero-exception rule.
