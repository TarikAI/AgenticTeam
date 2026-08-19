# Agent Evolution Changelog

Applied Level-3 changes (see `.agentic-team/protocols/evolution.md`). This is the audit trail of how the
team's constitution changed and why. Append-only.

## Format

```
## YYYY-MM-DD
- **<agent-name>** — <what changed> (proposal P-00X, approved by <human>)
  evidence: <short>
```

---

## 2026-08-19 - Audit remediation (v2.0.1)

Applied after a full repository audit. Every item below was reproduced before the fix and
re-verified after it.

**Safety**
- Checkpoint decisions now require the run's owner token, issued by `init-run` and stored
  outside the project at `~/.agentic-team/owner-tokens/<run-id>.token`. `--by` may not name an
  installed agent. Previously any agent could approve the R4 gate that was blocking it.
- Task risk is derived from what the task says it does; the declared `--risk` is a floor
  request, not a promise. A task titled "deploy to production" labelled R1 is raised to R3.
- A human rejection now actually blocks: claims and stage advances are refused while a run is
  `blocked`, and approving one checkpoint no longer clears an unrelated rejection.
- `advance` exits 2 at a human gate, so `advance && next-step` stops instead of walking through.

**Harness compilation**
- Antigravity: roles moved to `.agents/agents/<id>.md` with required frontmatter, rule gained
  `trigger: always_on`, workflows gained `description:`, and a root `AGENTS.md` is written.
  The previous `.agents/roles/` layout was never loaded by the tool.
- Protocol references in compiled prompts are rewritten to `.agentic-team/protocols/...`.
- Read-only roles carry an explicit ACCESS CONSTRAINT paragraph for harnesses without a
  pinned tool vocabulary (Antigravity, Gemini CLI, generic).
- `generic` writes a root `AGENTS.md`; switching harnesses removes the previous skill tree.

**Installer**
- `install.sh` probes for a Python that actually runs. On Windows `python3` resolves to the
  Microsoft Store stub, so every install failed with exit 49.

**Role definitions**
- All 50 roles moved to v2 vocabulary: state CLI instead of PLAN.md, task evidence records
  instead of STATUS.md, VERIFICATION.md instead of QA.md, stage names instead of "Phase N",
  DELIVERY-REPORT.md instead of FINAL-REPORT.md, with a single owner for the report.
- The per-role playbook loop now lives in `agent-contract.md`, which every compiled agent
  points at, so it survives compilation. It was previously stripped and reached no agent.
- The 18 specialists gained the standing-orders block the other 32 already had.

**Tests and CI**
- 42 -> 50 tests. Adapter expectations are literals rather than being read back out of
  `team.json`, plus new tests for native conventions, gate self-approval, risk derivation,
  blocked runs, protocol reference resolution, documented role counts, and gate coverage.
- CI runs on Windows and Ubuntu across two Python versions and performs real installs of all
  seven harnesses. It previously only syntax-checked the installer, which is why the Windows
  bug shipped.

**Documentation**
- Corrected the role count, split the CLI reference into compiler vs run invocations, fixed
  the generic router path and the local-LLM tier table, and documented that unlisted harnesses
  (zcode, Cursor, Windsurf, in-house runners) use `--harness generic`.

Not changed: `.opencode/agents/` is correct as-is. An audit pass claimed it should be
singular; the current OpenCode documentation specifies the plural form.

## 2026-08-14
- **system** — Baseline: 31 agents, 10 protocols, evolution + playbook system established.
  evidence: initial build of the AgenticTeam system.
