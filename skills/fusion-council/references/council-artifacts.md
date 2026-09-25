# Council artifacts

All files live in `<run>/_fusion/<id>/`; `fusion-init` creates them from `.agentic-team/templates/`.

| File | Writer | Phase | Contents |
|---|---|---|---|
| `brief.md` | moderator | before proposals (then frozen) | question, facts, unknowns, constraints, rubric, sponsor; critique assignments added at `critiques` |
| `proposals/<agent>.md` | that contributor only | proposals | thesis, design, assumptions, evidence, risks, costs, validation |
| `critiques/<agent>.md` | that contributor only | critiques | target proposal, claim challenged, strongest objection, failure mode, evidence required |
| `synthesis.md` | moderator | synthesis | chosen spine, integrated and rejected elements, interfaces, confidence, experiments |
| `dissent.md` | moderator | synthesis | one row per material unadopted argument, columns from `fusion-dissent.md` |
| `decision.md` | sponsor (via `fusion-close`) | decision | outcome, rationale, owner, next tasks, reopening triggers |

The moderator may ask for missing evidence but never rewrites a contributor's file. A revision
edits the contributor's own proposal and is submitted once with `--kind revision`.
