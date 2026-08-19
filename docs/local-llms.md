# Running the team on local LLMs (LM Studio, Ollama, Unsloth)

AgenticTeam roles are prompt contracts and the state manager makes no model API calls
(`docs/architecture.md`). Any harness or client that can (a) read the installed agent
files and (b) call an OpenAI-compatible chat endpoint can execute the team. Local LLM
servers fit that contract directly.

## Local endpoints

| Server | Start | OpenAI-compatible endpoint |
|---|---|---|
| LM Studio | `lms server start` (or Developer tab → Start Server) | `http://localhost:1234/v1` |
| Ollama | `ollama serve` (the desktop app starts it) | `http://localhost:11434/v1` |

Verify before a run: `python scripts/local_llm_check.py` reports reachable servers and
loaded models. Treat the report like preflight: absent servers mean sequential or
cloud-backed execution, not a blocked run.

## Point a harness at the local endpoint

**Codex** — `~/.codex/config.toml`:

```toml
model = "team-standard"          # any model id your server lists
model_provider = "lmstudio"

[model_providers.lmstudio]
name = "LM Studio"
base_url = "http://localhost:1234/v1"
wire_api = "chat"

[model_providers.ollama]
name = "Ollama"
base_url = "http://localhost:11434/v1"
wire_api = "chat"
```

**OpenCode** — `opencode.json` in the project:

```json
{
  "provider": {
    "lmstudio": {
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "http://localhost:1234/v1" },
      "models": { "team-standard": {} }
    },
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "options": { "baseURL": "http://localhost:11434/v1" },
      "models": { "llama3.1:8b": {} }
    }
  }
}
```

Then install the team as usual (`--harness codex` or `--harness opencode`). For custom or
in-house runners, use `--harness generic`: role contracts land in
`.agentic-team/agents/*.md`, skills in `.agents/skills/*`, and the router in both `AGENTS.md`
(project root) and `.agentic-team/AGENTS.md` —
read those files, send each role's contract as the system prompt, and drive
`.agentic-team/bin/agentic_team.py` for claims and gates. Claude Code and Gemini CLI are
built around their own clouds; for local execution prefer Codex, OpenCode, or generic.

## Model selection by role tier

`team.json` encodes depth per role; map it to model size instead of paying one price for
everything. The exact membership below is generated from `team.json` - check it there rather
than trusting a hand-written summary:

| Tier | Roles (examples) | Local model class |
|---|---|---|
| `fast` (6 roles) | content-marketer, email-marketing-specialist, skill-scout, social-media-manager, tech-writer, ugc-creative | ~7–9B instruct |
| `standard` (26 roles) | ai-ml-engineer, analytics-engineer, backend-engineer, backend-lead, brand-strategist, customer-success-strategist ... | ~14–32B instruct, tool-calling capable |
| `deep` (18 roles) | accessibility-specialist, build-integrator, ceo, cmo, code-reviewer, compliance-advisor ... | largest you can serve (70B-class or better) |

Requirements that matter more than raw size: function/tool calling (the orchestrator
drives the state CLI through tool calls), instruction following over long prompts (each
role contract plus standing orders plus task brief and a protocol slice — plan for a
32K+ effective context), and reliable structured output. Use instruct or tool-chat
variants, not base models.

## Throughput and concurrency

Local serving serializes what a cloud API would parallelize. The default
`max_concurrent_agents` is 6 (8 in autonomous policy). On a single local box, lower it —
or select a smaller roster (`platform-core`, or an exact agent list) — so queued roles
wait on the task graph instead of competing for tokens.

## Unsloth Studio: train the floors into the model

Unsloth Studio is the training side of this stack: fine-tune (LoRA) on the team's own
corpus, then serve the result locally.

1. Build instruction pairs from the repo: role contracts (`agents/**/*.md`), protocols
   (`protocols/*.md`), and — most valuable — accumulated `knowledge/lessons.md` and
   playbooks. Format: task brief in, disciplined output out, including gate refusals
   (examples where the correct behavior is to stop and record a gap, not to claim done).
2. Export the fine-tune to GGUF and either load it in LM Studio or register it in Ollama:
   `ollama create team-standard -f Modelfile` with `FROM ./model.gguf`.
3. Treat the fine-tune like the floor protocols: compression of the discipline, never a
   replacement. The files stay authoritative; the gates stay in code.

## Safety posture on local models

The autonomy policy, risk levels, and human gates are enforced by the deterministic
runtime, not by model good behavior — a weaker local model cannot approve an R3 action
the state manager will not perform. The reverse also holds: local does not mean
unregulated, so keep the harness's own safety prompts on and the skill-acquisition rule
that tool output is untrusted data.
