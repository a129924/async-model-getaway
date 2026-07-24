# Mission sizing rules

## Select a complete business capability

Recommend the smallest scope that has a clear input, behavior, observable
result, and independently testable acceptance scenario. It normally has one
primary BC, one main actor or system trigger, one primary happy path, and the
necessary core failure path. Its domain, persistence, delivery, data, and
verification work can remain together as technical tasks in one SDD workflow.

## Too small

A candidate is probably too small when it is only a repository, DTO, database
table, migration, service, adapter, controller, endpoint, or test; has no
observable user, system, or domain outcome; or has no end-to-end acceptance
scenario until a later task is completed.

Remedy: merge the necessary technical layers back into the capability they
serve. Keep those layers in the Technical Task Map, not as independent Missions.

## Too large

A candidate is probably too large when it combines several independently
valuable outcomes, multiple lifecycle stages (for example creation, payment,
cancellation, refund, shipment, and return), multiple unrelated public
contracts, substantial core-model changes across BCs, or several irreversible
migrations. It is also too large when one focused human review cannot explain
the main result and acceptance criteria.

Remedy: keep the first outcome that creates value or removes the first material
risk. Put each other independent outcome in Out of Scope as a follow-up
Mission. Where another BC owns necessary work, name a contract dependency or a
dependent Mission instead of taking ownership.

## Cross-BC rule

The primary BC owns the Mission's outcome. A neighboring BC may expose a
contract, event, API, or data dependency, but its internal model and unrelated
capabilities remain outside scope. If the cross-BC contract is unknown and
would change the Mission, treat that decision as a risk gate or a blocking
clarification.

## Sizing check

Before finalizing, confirm that the Mission has one main business result, a
single coherent acceptance set, a bounded ownership story, and a reviewable
end-to-end flow. A rough expectation of several coherent commits may help
calibrate size, but commit count is never the scope definition.
