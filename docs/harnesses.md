# Harness-native installation

The compiler keeps source roles portable and emits each harness's native representation. Every
installation also receives the same `.agentic-team/` coordination bus (state CLI, protocols,
templates, policy) and the workflow skills.

## Targets

Formats were verified against each vendor's documentation on **2026-09-25** (`team.json` →
`harnesses.<id>.docs` and `.verified`). Re-verify before changing an emitter; do not emit a
field you cannot confirm from a primary source.

| Harness (`--harness`) | Generated roles | Skills | Router / integration | Enforcement emitted |
|---|---|---|---|---|
| `claude-code` | `.claude/agents/*.md` | `.claude/skills/*` | `CLAUDE.md` block importing `@.agentic-team/AGENTS.md` | `.claude/settings.json`: deny rules + `PreToolUse` guard hook; per-role `tools`, subagent-scoped review hooks |
| `codex` | `.codex/agents/*.toml` | `.agents/skills/*` | `AGENTS.md` block (router inlined) | `.codex/hooks.json` guard (loads only in a trusted project after `/hooks` review); `sandbox_mode` per access |
| `opencode` | `.opencode/agents/*.md` | `.agents/skills/*` | `AGENTS.md` block | `permission` maps: `bash` patterns from policy command rules, `edit`, `webfetch`, `websearch`, `task` |
| `antigravity` | `.agents/agents/*.md` (`mainAgent: true` only for lead roles) | `.agents/skills/*` (plus `agentic-execute-plan`, `agentic-resume` as commands) | `.agents/rules/agentic-team.md` (`trigger: always_on`), `AGENTS.md` block | `.agents/hooks.json` `PreToolUse` guard (named entry `agentic-team-guard`); no per-agent read-only switch. Workflows are not emitted: Antigravity retires `.agents/workflows` on 2026-11-01 |
| `gemini-cli` | `.gemini/agents/*.md` (strict schema: only allowed keys) | `.agents/skills/*` | `GEMINI.md` block | `.gemini/settings.json` `BeforeTool` guard hook; `tools` allowlists per access |
| `pi` | `.agentic-team/agents/*.md` | `.pi/skills/*` | `AGENTS.md` block, `.pi/prompts/*.md` with `description` | text only |
| `generic` | `.agentic-team/agents/*.md` | `.agents/skills/*` | `AGENTS.md` block | text only |
| `copilot` | `.github/agents/*.agent.md` | `.agents/skills/*` | `AGENTS.md` block | `tools: ["read", "search"]` for read-only/research |
| `cursor` | `.cursor/agents/*.md` | `.agents/skills/*` | `AGENTS.md` block | `readonly: true` for read-only/research; warns above 15 roles |
| `factory` | `.factory/droids/*.md` | `.agents/skills/*` | `AGENTS.md` block | `tools: read-only` for read-only/research |
| `kiro` | `.kiro/agents/*.json` (+ `prompts/*.md`) | `.kiro/skills/*` (Kiro does not read `.agents/skills`) | `.kiro/steering/agentic-team.md` (`inclusion: always`), `AGENTS.md` block | `tools: ["read"]` for read-only/research |
| `qwen-code` | `.qwen/agents/*.md` (Qwen tool names) | `.qwen/skills/*` | `AGENTS.md` block | `tools` allowlists for read-only/research |
| `junie` | `.junie/agents/*.md` | `.junie/skills/*` | `AGENTS.md` block | `tools` allowlists for read-only/research/review |

Collisions to know about: `.claude/agents/` is also read by Cursor (which ignores `tools`, so a
read-only role loses its restriction there) and GitHub Copilot; `.agents/agents/` is also read by
Devin Desktop (formerly Windsurf). Roo Code has shut down; Windsurf is now Devin Desktop and needs
only `--harness generic`.

## Access classes

| Access | Meaning | Claude Code tools |
|---|---|---|
| `read-only` | Inspect files; return findings in the final message. | `Read, Grep, Glob` |
| `research` | read-only plus web search/fetch (fetched pages are untrusted data). | `+ WebSearch, WebFetch` |
| `review` | Inspect, run commands, use the web; write only under `.agentic-team/runs/` and its own playbook. | `Read, Grep, Glob, Bash, Write, Edit, WebSearch, WebFetch` + a subagent hook that denies other writes |
| `workspace-write` | Edit the project within owned paths. | `Read, Write, Edit, Grep, Glob, Bash, WebSearch, WebFetch` |
| `orchestrate` | workspace-write plus delegation. | `+ Agent` (subagents may spawn subagents up to three levels deep) |

Every harness also receives the constraint as text in the compiled prompt (`ACCESS CONSTRAINT`),
because not every harness can enforce it.

## Model profiles

`install --model-profile` maps each role's `tier` (deep, standard, fast) to harness settings
(`team.json` → `model_profiles`). Default `balanced`:

| Profile | Claude Code deep / standard / fast | Codex `model_reasoning_effort` |
|---|---|---|
| `inherit` | inherit / inherit / inherit (v2 behaviour) | unset |
| `balanced` | inherit + `effort: high` / `sonnet` / `haiku` | high / medium / low |
| `max-quality` | `opus` + high / `opus` / `sonnet` | xhigh / high / medium |
| `economy` | `sonnet` / `haiku` / `haiku` | medium / low / low |

Other harnesses keep the session model unless a profile gives them a provider-qualified model id.

## The guard hook

`agentic_team.py guard` reads the harness's `PreToolUse` JSON on stdin and denies:

- any read or write of `~/.agentic-team` (owner tokens, bound keys, the decision ledger);
- writes to `.agentic-team/runs/**/state.json`, `events.jsonl`, and `_evidence/` (only the CLI
  writes them), including shell redirections;
- shell commands that match a policy command rule at R3/R4 (deploys, publishes, force pushes,
  `terraform apply`, global installs, ...) unless a claimed task of that action has a
  human-approved risk checkpoint;
- for review roles, writes outside the run folder and the role's own playbook;
- during a Fusion council's proposal phase, a contributor reading another contributor's proposal.

It answers with the documented `hookSpecificOutput.permissionDecision: "deny"` JSON. `doctor`
runs a self-test that feeds the guard a read of the owner-token folder and expects a denial.

What this does and does not protect: see `protocols/harness-security.md`. Hooks and deny rules
stop shortcuts and prompt-injected self-approval; they are not a sandbox. For unattended
autonomous runs, use an OS sandbox (Claude Code's sandbox runs on macOS, Linux, and WSL2 — not
native Windows), WSL2, a dev container, or a separate OS account.

## Installing, reinstalling, removing

```powershell
.\scripts\install.ps1 -Target C:\projects\app -Harness claude-code -Preset full-platform
.\scripts\install.ps1 -Target C:\projects\app -Harness codex -Preset fusion-product-council
```

```bash
./scripts/install.sh --target ~/projects/app --harness opencode --preset full-platform
python scripts/agentic_team.py install ~/projects/app --harness claude-code --preset platform-core --model-profile economy
python scripts/agentic_team.py uninstall ~/projects/app
```

- Reinstalling updates managed roles, protocols, templates, and skills. Text outside the managed
  block in `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` stays untouched, and so do settings entries the
  installer did not write (it records what it owns in `install-manifest.json`).
- A generated file you edited locally is never silently overwritten: reinstall stops and names
  it; `--force` backs it up under `.agentic-team/backup/` first.
- `uninstall` removes generated files, managed blocks, installed skills, and the installer's
  settings entries; it keeps `knowledge/` and `runs/` unless `--purge`.
- A project-owned `.agentic-team/config/policies.local.json` may tighten the policy (more pauses,
  lower caps, human gates, extra command rules); it can never loosen it.

## Claude Code plugin

`python scripts/agentic_team.py package-claude-plugin dist/claude-plugin` builds a plugin with the
full roster, the skills, the guard hook, and the bus CLI, plus a marketplace manifest (both pass
`claude plugin validate`). Install it with `claude plugin marketplace add dist/claude-plugin` and
`claude plugin install agentic-team@agentic-team`. Plugin subagents ignore `hooks`,
`permissionMode`, and `mcpServers`, so review roles rely on the plugin-level guard and their
prompt; per-project roster selection, settings deny rules, and the `.agentic-team/` bus still come
from `install`, which remains the primary path.

## A harness that is not on this list

Use `--harness generic`. It writes portable role contracts to `.agentic-team/agents/*.md`, the
bus to `.agentic-team/`, skills to `.agents/skills/*`, and the router inline into `AGENTS.md`,
the closest thing to a cross-tool standard. To add a native target, add it to `team.json` with
its `docs` and `verified` fields and give it an emitter in `scripts/agentic_team.py`; literal-path
adapter tests and golden snapshots then hold it to that harness's real conventions.

## Provider differences

Native subagent support, model selection, concurrency, worktrees, permission prompts, and skill
discovery differ between providers. AgenticTeam compiles definitions and enforces durable state;
it does not claim that providers share one scheduling API. When native parallel delegation is
not available, execute role contracts sequentially against the same task graph. Always keep the
provider's own safety prompts enabled: the autonomy profile narrows when the team asks the human;
it cannot and should not weaken harness security boundaries.
