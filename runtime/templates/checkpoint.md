# Checkpoint request

Raise with `agentic_team.py checkpoint --kind decision|deviation|injection|budget` and all of:

- `--question`: the decision the human must make, in one sentence
- `--recommendation`: what you recommend and why
- `--alternatives`: the other options and their trade-offs
- `--impact`: what happens if the human waits or says no
- `--evidence`: files, exec ids, or commits that support the recommendation
- `--rollback`: how the choice is undone if it proves wrong
