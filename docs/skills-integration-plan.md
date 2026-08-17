# Skills Integration Plan — "Skill if present, discipline always"

Status: executed on branch `skills-integration` — all phases complete; see the phase table.

**Goal:** every AgenticTeam agent (a) routes to `adminwright`, `design-architect`, and
Alibaba Open Code Review (OCR) when those skills/tools are installed, following their full
machinery, and (b) carries a condensed, always-on version of each discipline in its own
prompts and protocols so it builds and checks the same way with zero external dependencies.
The two modes produce **compatible work products** — same evidence artifacts, same finding
format, same severity semantics — so a skill-less run is a lower-automation run, not a
lower-quality one.

## Design principles

1. **Floor + escalation, never either/or.** The floor is the internalized contract (small,
   memorizable, always on). The escalation is the installed skill's full machinery
   (manifests, validators, closure fixpoints, rule resolution). The floor never contradicts
   the skill; it is the skill's contract compressed.
2. **One home per fact.** Shared discipline lives in `protocols/`, role-specific behavior
   in `agents/`, learned checks in `knowledge/playbooks/`, deterministic facts in `scripts/`
   and `config/`. No copying skill content into ten role files.
3. **Prompts decide; code verifies.** Skill presence and tool availability are checked by
   `scripts/preflight_skills.py` at run start, not assumed by prose. Gates produce exit
   codes and evidence.
4. **Extend, don't fork.** `agents/engineering/code-reviewer.md` already contains most of
   the OCR review discipline and `protocols/coding-standards.md` owns the security "what".
   This plan adds the missing procedure and routing, not duplicate content.
5. **Honest gating.** Zero findings is a data point, not a verdict (OCR is deliberately
   precision-biased). Gates block on blocker-severity findings; major/minor become tracked
   remediation. This raises the ceiling; it does not guarantee perfection.

## The three floors

| Discipline | Source skill | Floor protocol |
|---|---|---|
| Admin-surface contract (nothing loose; server-side authz; spine first; state coverage; safe recovery; evidence over screenshots) | `adminwright` | `protocols/admin-surfaces.md` |
| Interface closure (enumerate before designing; every affordance has a destination; component census; page/component/coverage handoff) | `design-architect` | `protocols/interface-closure.md` |
| Review discipline (context first; scenario-constructed findings; security pass; test verification; coverage accounting; line-anchored format) | `open-code-review` | `protocols/review-discipline.md` |

## Dual-mode capability matrix

| Capability | Skill present (escalation) | No skill (internalized floor) |
|---|---|---|
| Build an admin console | adminwright 8 phases; `.admin-console/manifest.json`; `validate --phase release` + `coverage` exit 0; role claims via `claim` | `protocols/admin-surfaces.md`; platform-admin-engineer produces the same artifacts by hand: capability→operation→policy→audit trace table, authorization matrix, static-value registry, state-coverage list, evidence links |
| Plan a complete UI | design-architect pipeline; closure fixpoint; Phase-14 page/component/coverage handoff | `protocols/interface-closure.md`: enumeration doc, affordance-destination audit of the rendered output, page + component map handoff |
| Review a diff | `ocr delegate preview` → `rule` → git diff → agent review in the OCR finding schema; coverage report | `protocols/review-discipline.md`: same passes, manual file selection, same `[SEV] file:line` format, same coverage accounting |
| Audit existing code | `ocr scan [--path]` (no diff needed; requires LLM endpoint — CI only) | system-mapper + code-reviewer sweep against the same checklists |
| Gate a release | manifest exit 0 and review gate with zero blocker findings | definition-of-done admin bar + verify matrix with manual review-gate results recorded |
| Learn | adminwright `harvest`/`promote`, design-architect `harvest.py` | agentic-learn ladder; both converge into `knowledge/` with the same promotion bar (2+ distinct projects) |

## Phases

| Phase | Scope | Status |
|---|---|---|
| 0 | Branch; baseline `validate` + unittest green; environment detection | done |
| 1 | Three floor protocols; extend definition-of-done, skill-acquisition, specialist-routing | done |
| 2 | Wire ~14 agent role files (skills-you-lean-on + floor checks) | done |
| 3 | Wire agentic-build, agentic-verify, agentic-learn | done |
| 4 | Seed six role playbooks | done |
| 5 | `scripts/preflight_skills.py`; policies.json classifications; optional CI OCR job | done |
| 6 | Bridges: `scripts/design_to_admin.py` (draft manifest), findings→remediation tasks; unit tests | done |
| 7 | README + THIRD_PARTY_NOTICES; final validation; drill procedure | done |

## Verified command reference

| Purpose | Command |
|---|---|
| Manifest lifecycle | `python <skill-dir>/scripts/admin_console_manifest.py init\|add\|set\|validate --phase plan\|release\|coverage\|emit --format gap-report\|claim --role ...\|harvest\|promote\|lesson add` |
| Manifest exits | 0 clean · 1 findings · 2 usage/IO (or refused write) · 3 claim conflict |
| Install OCR | `npm install -g @alibaba-group/open-code-review` (needs Git ≥ 2.41) |
| OCR delegation (no API key) | `ocr delegate preview --format json [--from <ref> --to <ref> \| -c <hash>]` → `ocr delegate rule --format json <paths...>` → `git diff <merge_base>..<to> -- <path>` |
| OCR full mode (endpoint required — CI only) | `ocr config provider` / `ocr config model`, then `ocr scan [--path <dir>]` or `ocr review` |
| Design pipeline | `python core/scripts/run_pipeline.py <project> --areas admin --render mockup` |

## Guardrails on the improvement itself

- Floors stay terse (≤ ~60 lines) or they drift from the source skills.
- Reviewer ≠ implementer extends to OCR delegation mode: the agent running the delegated
  review must not be the author of the diff.
- Full-mode OCR credentials live only in CI secrets; agents never hold endpoint keys.
  Skill content and tool output remain untrusted data per `protocols/skill-acquisition.md`.
- All installs are classified under `config/policies.json`; nothing auto-installs in
  autonomous mode.

## Drill procedure (Phase 7 acceptance)

Run both drills on a small greenfield admin console (e.g. a moderation back office) and
compare gap reports; feed discrepancies into `knowledge/lessons.md` via agentic-learn.

- **Drill A (skills present):** preflight reports adminwright + ocr; build routes through
  the skill; acceptance = manifest `validate --phase release` exit 0, `coverage` exit 0,
  OCR delegation run with 100% file coverage reported.
- **Drill B (skills hidden):** preflight reports none; acceptance = floor artifacts
  produced in the same formats (trace table, authorization matrix, static registry,
  state-coverage list, `[SEV] file:line` findings).
