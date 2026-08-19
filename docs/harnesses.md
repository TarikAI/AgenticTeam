# Harness-native installation

The compiler keeps source roles portable and emits each harness's native representation. Every
installation also receives the same `.agentic-team/` coordination bus and workflow skills.

| Harness | Generated roles | Skills | Router/integration |
|---|---|---|---|
| Claude Code | `.claude/agents/*.md` | `.claude/skills/*` | managed block in `CLAUDE.md` |
| Codex | `.codex/agents/*.toml` | `.agents/skills/*` | compact managed block in `AGENTS.md` |
| OpenCode | `.opencode/agents/*.md` | `.agents/skills/*` | permissions/mode frontmatter + `AGENTS.md` |
| Antigravity | `.agents/agents/*.md` | `.agents/skills/*` | `trigger: always_on` rule in `.agents/rules`, commands in `.agents/workflows`, managed block in `AGENTS.md` |
| Gemini CLI | `.gemini/agents/*.md` | `.agents/skills/*` | managed block in `GEMINI.md` |
| Pi | `.agentic-team/agents/*.md` | `.pi/skills/*` | root `AGENTS.md` + `.pi/prompts` |
| Generic | `.agentic-team/agents/*.md` | `.agents/skills/*` | portable role contracts + managed block in `AGENTS.md` |

The compiler marks read-only roles using each harness's own mechanism where one exists:
a `tools` allowlist for Claude Code, `sandbox_mode = "read-only"` for Codex, and
`permission.edit: deny` for OpenCode. Antigravity and Gemini CLI do not have a tool vocabulary
this project pins, so read-only roles additionally carry an explicit `ACCESS CONSTRAINT`
paragraph in the compiled prompt, which every harness understands. Protocol references are
rewritten to their installed `.agentic-team/protocols/...` paths at compile time.

The compiler replaces the per-role standing-orders block with a pointer to
`.agentic-team/protocols/agent-contract.md`, which carries the task envelope, evidence rules,
hard human gates, and the per-role playbook loop.

## A harness that is not on this list

`team.json` defines exactly seven targets. Anything else - zcode, Cursor, Windsurf, an
in-house runner, or a harness released after this version - is **not** a recognised
`--harness` value and the installer will reject it.

Use `--harness generic` for those. It writes portable role contracts to
`.agentic-team/agents/*.md`, the coordination bus to `.agentic-team/`, skills to
`.agents/skills/*`, and a managed router block into the project's root `AGENTS.md`, which is
the closest thing to a cross-tool standard. Point the harness at `AGENTS.md`, load the role
contract you want as a system prompt, and drive `.agentic-team/bin/agentic_team.py` for
claims, evidence, and gates.

If a harness has its own native agent format worth compiling to, add it to `team.json` and
give it an emitter in `scripts/agentic_team.py`; the adapter tests will then hold it to that
harness's real conventions.

## Install examples

```powershell
.\scripts\install.ps1 -Target C:\projects\app -Harness claude-code -Preset full-platform
.\scripts\install.ps1 -Target C:\projects\app -Harness codex -Preset fusion-product-council
.\scripts\install.ps1 -Target C:\projects\app -Harness antigravity -Preset regulated-platform
```

```bash
./scripts/install.sh --target ~/projects/app --harness opencode --preset full-platform
./scripts/install.sh --target ~/projects/app --harness gemini-cli --preset audit
```

Reinstalling updates managed roles, protocols, templates, and skills. Existing root instructions
outside the marked block remain untouched. Project `knowledge/` remains project-owned and is not
overwritten.

## Provider differences

Native subagent support, model selection, concurrency, worktrees, permission prompts, and skill
discovery differ between providers. AgenticTeam compiles definitions and enforces durable state;
it does not claim that providers share one scheduling API. When native parallel delegation is not
available, execute role contracts sequentially against the same task graph.

Always keep the provider's own safety prompts enabled. AgenticTeam's autonomy profile narrows when
the team asks the human; it cannot and should not weaken harness security boundaries.
