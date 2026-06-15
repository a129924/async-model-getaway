---
name: python-library-architecture
description: Design or review reusable Python library/package architecture with theme isolation, a side-effect-free `core`, and facade/client composition for multi-theme libraries and SDK-style packages.
complexity: medium
risk_profile: [ambiguity_sensitive]
inputs:
  - the reusable library or SDK's consumer-facing capabilities
  - the proposed themes or capability slices inside one package
  - the contracts shared across themes or external boundaries
  - the adapters or integrations that touch transport, storage, or vendor APIs
  - the intended public facade/client entry points
  - any current dependency smells, such as peer imports or a growing `common/`
outputs:
  - a review-ready library-architecture rule set or design recommendation
  - an explicit dependency-direction model for themes, `core`, adapters, and facade/client entry points
  - refactor guidance for cross-theme coupling, `core` misuse, and composition-root cleanup
use_when:
  - designing or reviewing the internal architecture of a reusable Python library or SDK-style package
  - deciding where themes, shared contracts, adapters, and the public facade/client should live
  - refactoring a coupled package that has cross-theme imports, a bloated `common/`, or orchestration in the wrong layer
do_not_use_when:
  - the main task is package/distribution layout, `src/`, or `pyproject.toml`
  - the main task is module export policy, `__all__`, or deep-import rules
  - the main task is type-hint syntax, model-construct choice, serialization translation, or error policy
  - the main task is service/application architecture, framework layering, or plugin design
---

# Purpose
Choose clean internal architecture for reusable Python libraries and SDK-style packages so themes stay isolated, shared contracts live in `core`, and consumers enter through a clear facade/client.

# Trigger / When to use
Use this skill when:
- designing or reviewing the internal architecture of a reusable Python library or SDK-style package
- deciding where themes, shared contracts, adapters, and the public facade/client should live
- refactoring a coupled package that has cross-theme imports, a bloated `common/`, or orchestration in the wrong layer

Do not use this skill when:
- the main task is package/distribution layout, `src/`, or `pyproject.toml`
- the main task is module export policy, `__all__`, or deep-import rules
- the main task is type-hint syntax, model-construct choice, serialization translation, or error policy
- the main task is service/application architecture, framework layering, or plugin design

# Inputs
- the reusable library or SDK's consumer-facing capabilities
- the proposed themes or capability slices inside one package
- the contracts shared across themes or external boundaries
- the adapters or integrations that touch transport, storage, or vendor APIs
- the intended public facade/client entry points
- any current dependency smells, such as peer imports or a growing `common/`

# Process
1. Confirm the task is library/package architecture only. If it is mainly about package layout, module gateways, typing syntax, model choice, serialization rules, error policy, or app/service architecture, hand off instead of widening scope.
2. Slice the library into themes that own one capability family each. Keep collaboration inside a theme by default.
3. Use `core/` as the recommended shared contract center for multi-theme libraries. Allow a semantically explicit alternative such as `kernel/` or `base/` only if it plays the same role; do not use vague substitutes such as `common/` or `utils/`.
4. Enforce a zero-exception cross-theme import ban. If two themes need the same contract, semantic primitive, or boundary-crossing abstraction, promote it into `core` instead of importing peer-to-peer.
5. Keep `core` side-effect-free and non-orchestrating. Put shared contracts, semantic value types, shared base errors, and pure support logic there; keep I/O, retries, auth refresh flows, client bootstrap, and other outward orchestration out of `core`.
6. Make the public facade/client the recommended composition root. Prefer one primary consumer-facing entry point; allow bounded secondary entry points only when they remain orchestration-only and do not become alternate architecture lanes.
7. Keep dependency direction explicit: facade/client and entry points may compose themes and adapters; adapters may depend on their owning theme and `core`; themes may depend on `core`; `core` must not depend outward.
8. Use the rules and checklist in `reference.md` as the portable baseline. Treat tools such as `import-linter` or Tach as optional verification aids, not as the architecture policy itself.
9. Use `examples.md` for pure-library, SDK-style, anti-pattern, and migration cases before recommending a refactor.

# Examples
- Positive: Put shared pagination and credential contracts in `core`, keep `storage/` and `queues/` isolated from each other, and expose one `Client` that composes them without either theme importing the other.
- Negative: Let `billing/` import `users/models.py`, move HTTP bootstrap into `core/`, or use `common/` as a cross-theme dump zone.

# Outputs
- a review-ready library-architecture rule set or design recommendation
- an explicit dependency-direction model for themes, `core`, adapters, and facade/client entry points
- refactor guidance for cross-theme coupling, `core` misuse, and composition-root cleanup

# Validation
Before proceeding, confirm:
- confirm no theme imports another theme, with zero exceptions
- confirm `core` is the shared contract center and stays side-effect-free
- confirm shared contracts that cross themes or external boundaries are promoted into `core`
- confirm facade/client entry points compose themes and adapters instead of pushing orchestration down into `core`

**SOFT FAIL** — ask and wait before continuing:
- Theme boundaries are unclear (what counts as one capability family vs two) → ask before recommending a slice boundary
- Whether a shared artifact belongs in `core` or a specific theme is ambiguous → ask before recommending promotion

**BLOCKED** — stop and redirect:
- The main task is package/distribution layout, `src/`, or `pyproject.toml` → redirect to `python-package-layout`
- The main task is service/application architecture, framework layering, or plugin design → out of scope for this skill

# Boundaries
- Do not define physical package/distribution layout; use `python-package-layout`.
- Do not define package gateways, `__all__`, deep-import policy, or internal-module contracts; use `python-module-boundaries`.
- Do not define type-hint syntax or strict-typing escape hatches; use `python-type-hints-strict`.
- Do not choose between `Enum`, dataclass, `ABC`, or `Protocol`; use `python-model-selection`.
- Do not define payload translation rules at API, database, or message boundaries; use `python-serialization-boundaries`.
- Do not define exception hierarchy or translation policy beyond allowing shared base errors in `core`; use `python-error-handling`.
- Do not widen into service/application architecture, framework-specific layering, or plugin systems.

# Failure Handling
- **Missing Context**: if theme boundaries, `core` scope, or facade/client intent are unknown, ask once before applying architectural rules.
- **Ambiguous Requirement**: if the stated goal conflicts with library-architecture boundaries (e.g., the task is really about module gateways or packaging), name the conflict and redirect.
- **Execution Limitation**: if the task involves service/application architecture or framework-specific plugin systems, stop and redirect to the appropriate skill.

# Local references
- `reference.md`: hard rules, dependency-direction checklist, smell list, and optional-tooling notes for reusable library/package architecture
- `examples.md`: pure-library, SDK-style, anti-pattern, and migration examples for theme isolation, `core`, and facade/client composition
