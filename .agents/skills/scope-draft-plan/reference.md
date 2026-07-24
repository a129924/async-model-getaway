# Scope Draft Plan Reference

Use this file after `SKILL.md` has established that the task is scope
convergence rather than implementation planning or execution.

## Core terms

| Term | Meaning in this skill |
| --- | --- |
| BC Mission | One independently acceptable business capability owned by one primary BC. |
| Primary BC | The context accountable for the core business result and its main rules. |
| Technical task | Domain, persistence, delivery, data, observability, or verification work needed inside one Mission. |
| Follow-up Mission | A separately valuable capability intentionally excluded from the recommended Mission. |
| Dependent Mission | Work another BC must own before or alongside the Mission; it is not silently included. |
| Risk gate | A high-impact decision that needs explicit handling before implementation planning can proceed safely. |

## Output boundary

A Draft Plan is a conversational scope decision. It is not:

- a repo-visible topic plan;
- a frozen requirements or technical-spec artifact;
- a Python implementation plan; or
- permission to create files, dispatch work, or implement anything.

Use the output template for capability-level decisions. It may name a
technical-task map, but never file-by-file steps, classes, database columns, or
endpoint designs unless the human has already locked them as a relevant public
contract.

## Reference routing

- Read `references/scope-sizing.md` to judge whether a candidate is too small,
  too large, or complete enough.
- Read `references/output-template.md` to produce the Draft Plan in the proper
  language and structure.
- Read `references/handoff-routing.md` only after the Draft Plan is complete;
  its guidance is advisory and never performs routing.

## Language rule

Use the language requested by the human. When no language is requested, follow
repository governance; if it specifies no different language, use Traditional
Chinese. Local headings or examples may be translated without changing the
meaning or required decision fields.
