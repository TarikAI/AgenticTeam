# Harness security

What AgenticTeam's protections stop, what they do not, and how to close the gap. Three layers:
prompts decide, the CLI checks state transitions, the harness checks tool calls. None of them is
an OS boundary.

## Threat model

Protects against:

- cooperative agents taking shortcuts (skipping a gate, claiming unrun tests, editing state);
- prompt-injected attempts to self-approve (reading the owner token, forging a decision);
- accidental edits to run state, events, evidence, or the owner's material.

Does not protect against deliberately malicious code running unsandboxed as the same OS user.
Such code can read `~/.agentic-team`, bypass hooks, or edit files directly. Signed decisions and
the event hash chain make that tampering evident (`audit verify`), not impossible. Only OS
isolation makes it impossible.

## Per-harness enforcement

| Harness | Enforced by the harness | Instruction only |
|---|---|---|
| `claude-code` | `.claude/settings.json` deny rules (read/edit of `~/.agentic-team`, edits of run `state.json`, `events.jsonl`, `_evidence/`); `PreToolUse` guard hook; per-role `tools` allowlists; subagent-scoped guard hooks for review roles | anything done through a tool the hook does not see |
| `codex` | `.codex/hooks.json` guard, loaded only in a trusted project after the human reviews it with `/hooks`; `sandbox_mode` per access (`read-only` for read-only/research roles) | per-agent tool limits (none exist); review-role source protection |
| `opencode` | `permission` maps: `edit`, `webfetch`, `websearch`, `task`, and `bash` patterns from policy command rules (R4 deny, R3 ask) | `edit: deny` does not stop writes through `bash`; no guard hook, so owner-home and run-state protection |
| `gemini-cli` | `BeforeTool` guard hook in `.gemini/settings.json` (owner home, run state, command rules); `tools` allowlists for read-only, research, and review roles | review-role source protection |
| `antigravity` | `PreToolUse` guard hook in `.agents/hooks.json` (owner home, run state, command rules) | per-agent read-only limits (no reliable switch) |
| `copilot`, `factory`, `kiro` | read-only tool lists for read-only/research roles | everything else |
| `cursor` | `readonly: true` for read-only/research roles | everything else |
| `qwen-code`, `junie` | `tools` allowlists (junie also for review roles) | everything else |
| `antigravity`, `pi`, `generic` | nothing | all rules (text in the compiled prompt) |

Every harness also gets the rules as text (`ACCESS CONSTRAINT`). The CLI checks
(human-only commands, stage exits, risk checkpoints, `exec` command rules, the event chain)
apply on every harness, because they run inside `agentic_team.py`. Details per target:
`docs/harnesses.md`.

## What the guard denies

The guard (`agentic_team.py guard`, wired as a `PreToolUse` hook on Claude Code and Codex) denies:

- any read or write of `~/.agentic-team` (owner tokens, bound keys, the decision ledger);
- writes to `.agentic-team/runs/**/state.json`, `events.jsonl`, and `_evidence/`, including
  shell redirections, copies, moves, and deletes;
- shell commands matching an R3/R4 command rule unless a claimed task of that action has a
  human-approved risk checkpoint;
- for review roles, writes outside `.agentic-team/runs/` and the role's own playbook;
- during a Fusion council's proposal phase, a contributor reading another's proposal
  (Claude Code only; it passes the subagent type to the hook).

A denied call is a decision, not an obstacle: do not retry it or route around it
(`guardrails.md`).

## Sandbox and isolation

- For unattended or `autonomous` runs, run the harness inside OS isolation.
- Claude Code's sandbox runs on macOS, Linux, and WSL2, not on native Windows. Enable it there.
- On native Windows use WSL2, a dev container, or a separate OS account that cannot read the
  owner's home folder.
- A supervised worker runs with its own empty `AGENTIC_TEAM_HOME` and reads decisions through
  the exported `AGENTIC_TEAM_VIEW`. Removing the owner's variable does not isolate files from the
  same OS user: the view is trustworthy only where the worker cannot write it, and the owner side
  re-checks with `audit verify` after every attempt.
- Never grant agents access to `~/.agentic-team` (or `AGENTIC_TEAM_HOME`): no allow rule, no
  mount into a container, no additional directory. Keep the owner token file outside every
  folder an agent can read.
- Keep production credentials out of agent environments entirely: no production keys in
  `.env`, shell profiles, CI variables an agent job can read, or mounted cloud config
  (`secrets-and-sensitive-data.md`).
- Keep the harness's own permission prompts on; an autonomy profile never weakens them.

## Verify

- `agentic_team.py doctor` (Claude Code and Codex installs): feeds the guard a read of the
  owner-token folder and expects a denial, and checks the hook is registered in
  `.claude/settings.json` or `.codex/hooks.json`. On Codex, also confirm the project is trusted
  and the hook was approved in `/hooks`.
- `agentic_team.py audit verify --by <name> --token-file <path>` (human): recomputes ledger
  signatures and the event hash chain; any finding means stop and investigate.
- Other harnesses: inspect the generated agent files for the allowlists in the table above.
