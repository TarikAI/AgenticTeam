# Learning ladder

`observation → candidate (learn) → playbook candidate → evaluation → human promote (proven) → PROPOSALS entry → human approval → CHANGELOG`

| Step | Where | Who |
|---|---|---|
| candidate | `<run>/07_learn/lesson-*.md` + `.agentic-team/knowledge/lessons.md` | any role, via `learn` |
| playbook candidate | `.agentic-team/knowledge/playbooks/<role>.md`, `status: candidate` | that role |
| evaluation | `<run>/07_learn/eval-<slug>.md` | retrospective owner |
| proven | same playbook line, `status: proven · promoted: <date> by <human>` | human, via `promote` |
| proposal | `.agentic-team/knowledge/evolution/PROPOSALS.md`, `status: proposed` | delivery-lead / cmo drafts |
| applied | `.agentic-team/knowledge/evolution/CHANGELOG.md` with version | human |

## Evaluation record

```markdown
# Evaluation — <lesson title>
- Candidate: <playbook line or lessons.md title> · source: <run>/<task>
- Disproof test: <observable result that would show the lesson is wrong>
- Baseline cases: <runs/tasks without the check, with outcome>
- Candidate cases: <runs/tasks with the check, with outcome>
- Regressions checked: correctness, security, privacy, accessibility, latency, cost, user intent
- Result: supports | refutes | inconclusive · confidence: low | medium | high
```

Promote only when evidence repeats across relevant cases, or a human accepts a one-case safety
correction. Guardrails may be tightened from strong evidence; weakening always needs explicit
human review and a compensating control.
