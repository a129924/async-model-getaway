# Business-to-Technical Translation Checklist

Use this checklist before treating `analysis/<topic>/technical-spec.md` as review-ready.

- [ ] The task is technical translation of a business baseline, not business discovery or direct implementation.
- [ ] The output path is explicit: `analysis/<topic>/technical-spec.md`.
- [ ] `analysis/<topic>/requirements.md` exists and is strong enough to translate:
  - [ ] actors and measurable outcomes are explicit
  - [ ] contradictions are resolved or clearly marked as blockers
  - [ ] the baseline is not still using soft business adjectives as requirements
- [ ] Every business requirement maps to one of these outcomes:
  - [ ] concrete technical realization
  - [ ] explicit blocker
  - [ ] rollback-to-alignment trigger
- [ ] Major workstreams include cost-of-realization commentary covering build effort, sequencing, integration burden, or operational load.
- [ ] An architecture-compliance self-check names whether each major area fits, fits with prerequisites, needs waiver, or conflicts.
- [ ] Material conflicts are explicit and include rollback instructions instead of optimistic workaround language.
- [ ] The document does not silently narrow or rewrite the business promise to make implementation easier.
- [ ] The document does not contain runtime coding, scaffolding, or execution steps.
