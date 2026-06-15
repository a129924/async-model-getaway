# Stop-and-Ask Triggers

Stop and ask before drafting or continuing when any of the following conditions is true.

- The real topic outcome is unclear.
- Artifact paths cannot be stated exactly.
- Stable-library timing is unclear.
- Release intent is implied but not declared.
- The topic tries to mix multiple jobs that should be separate topics.
- Analysis artifacts exist but conflict with chat-time instructions and no explicit human `override` is present.
- A human `override` instruction is ambiguous about which specific analysis file it overrides.

Do not fill placeholder text (`TBD`, `later`, `follow normal process`) in place of explicit decisions. Stop and resolve the ambiguity first.
