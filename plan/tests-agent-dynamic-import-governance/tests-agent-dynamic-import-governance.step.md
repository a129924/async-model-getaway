---
topic: tests-agent-dynamic-import-governance
phase: plan-authoring
created: 2026-06-26
---

# tests-agent-dynamic-import-governance — Step Tracking

> **Executor**: 完成後將每個步驟標記為 `[X]`。
> 在此 topic 離開 `implement-plan` 前，所有 Implementation Steps 都必須為
> `[X]`。
> 請在
> `plan/tests-agent-dynamic-import-governance/tests-agent-dynamic-import-governance.step.md`
> 更新此檔。

## Workflow Stages

- [X] plan-authoring
- [ ] plan-review
- [ ] implementation
- [ ] reviewer-follow-up

## Implementation Steps

- [ ] 1. Update `AGENTS.md` so the root repo policy explicitly forbids agents from using dynamic module loading in `tests/` to make tests fit implementation unless the current topic plan names a reviewer-verifiable necessity exception; state that root `AGENTS.md` plus the reviewer gate are the formal control plane and `tests/AGENTS.md` is not.
- [ ] 2. Update `.codex/agents/reviewer.toml` so reviewer instructions treat unauthorized dynamic module loading in `tests/` as a bounded governance violation, require the topic plan to name any allowed exception and why it is necessary, and record `tests/model_registry/model_payload/test_canonical_hash.py` only as a grandfathered known exception rather than a reusable precedent.
- [ ] 3. Run bounded validation over `AGENTS.md`, `.codex/agents/reviewer.toml`, and existing `tests/` dynamic-import call sites so the grandfathered exception remains the only recorded known case, then update `tests-agent-dynamic-import-governance.step.md` to reflect implementer-owned completion without pre-filling reviewer or human gates.
