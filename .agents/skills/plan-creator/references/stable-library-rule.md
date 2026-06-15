# Stable-Library Rule

Rules for deciding when and how to declare stable-library intent in a topic plan.

- If the topic does **not** affect stable-library surfaces, say so explicitly.
- If the topic affects `README.md`, `VERSION`, release notes, or deferred release timing, the topic plan must include a `## Stable library metadata` section.
- `## Stable library metadata` must declare the workflow fields needed to execute the promotion, including at minimum:
  - `README row`: whether `README.md` changes and what row or entry is expected
  - `VERSION bump`: whether `VERSION` changes and the intended bump, or an explicit no-bump decision
  - `timing`: whether promotion happens at `publish-in-progress`, is deferred, or is tied to `release`
- If release notes or deferred release timing are part of the topic, declare them inside `## Stable library metadata`, not only as narrative notes elsewhere.
- Do not treat `Locked Decisions` as a substitute for stable-library metadata; executable metadata must still appear in its own section.
- If `timing=release`, the topic plan must also declare the release action under `Post-merge / release actions` as required by the workflow.
- If no release action exists, `Post-merge / release actions` should say that explicitly rather than leaving release handling implied.
- Do not mix review-ready-only work with undeclared stable-library promotion.
