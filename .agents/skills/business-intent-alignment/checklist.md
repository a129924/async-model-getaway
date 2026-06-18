# Business Intent Alignment Checklist

Use this checklist before treating `analysis/<topic>/requirements.md` as review-ready.

- [ ] The task is business-intent alignment, not technical design, implementation planning, or coding.
- [ ] The output path is explicit: `analysis/<topic>/requirements.md`.
- [ ] Every in-scope requirement names an actor, condition, observable result, and metric or decision rule.
- [ ] Soft adjectives such as `fast`, `simple`, `accurate`, or `better` were converted into measurable language.
- [ ] Contradictions were surfaced explicitly:
  - [ ] resolved with a clear decision, or
  - [ ] recorded as blockers instead of hidden in compromise wording.
- [ ] Extreme-boundary checks were applied for at least these cases:
  - [ ] no network or degraded dependency
  - [ ] wrong user role or missing approval
  - [ ] interrupted or partially completed flow
  - [ ] low-volume and peak-volume conditions
- [ ] Assumptions and non-goals are stated clearly enough that technical translation will not need to guess intent.
- [ ] The document does not contain architecture choices, task breakdowns, or implementation estimates.
- [ ] If blockers remain, the file says technical translation must roll back or wait; it does not pretend the baseline is fully frozen.
