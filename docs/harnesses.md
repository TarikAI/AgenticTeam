# Harness-native installation

The compiler keeps source roles portable and emits each harness's native representation. Every
installation also receives the same `.agentic-team/` coordination bus and workflow skills.

| Harness | Generated roles | Skills | Router/integration |
|---|---|---|---|
| Claude Code | `.claude/agents/*.md` | `.claude/skills/*` | managed block in `CLAUDE.md` |
| Codex | `.codex/agents/*.toml` | `.agents/skills/*` | compact managed block in `AGENTS.md` |
| OpenCode | `.opencode/agents/*.md` | `.agents/skills/*` | permissions/mode frontmatter + `AGENTS.md` |
| Antigravity | `.agents/roles/*.md` | `.agents/skills/*` | `.agents/rules` and `.agents/workflows` |
| Gemini CLI | `.gemini/agents/*.md` | `.agents/skills/*` | managed block in `GEMINI.md` |
| Pi | `.agentic-team/agents/*.md` | `.pi/skills/*` | root `AGENTS.md` + `.pi/prompts` |
| Generic | `.agentic-team/agents/*.md` | `.agents/skills/*` | portable role contracts |

The compiler marks read-only roles appropriately where the harness supports native permission or
sandbox fields. It strips duplicated legacy standing orders and points every role to the compact
shared contract.

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
