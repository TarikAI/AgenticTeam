# Evidence-controlled evolution

The team may learn from runs; it may not silently rewrite its constitution. Evolution follows:

`observation -> scoped lesson -> playbook candidate -> evaluation -> proposal -> human approval -> versioned promotion`

## 1. Observation

Capture an observed outcome, failure, recovery, review finding, or explicit human feedback with
run/task source. Separate evidence from interpretation; invented feedback is prohibited.

## 2. Scoped lesson

State trigger, affected roles/tasks, impact, imperative behavior, confidence, and a counterexample
or condition where it should not apply. A lesson that cannot alter a future action is only a note.

## 3. Reversible playbook candidate

Put role-specific candidates in the project's playbook with status `candidate`. Keep each playbook
short enough to scan. The candidate must not change permissions, autonomy, hard gates, or another
role's ownership.

## 4. Evaluation

Define a test that could disprove the lesson. Compare relevant baseline and candidate cases; check
for regressions in correctness, security, privacy, accessibility, latency, cost, and user intent.
One lucky result is insufficient unless a human accepts an urgent one-case safety correction.

## 5. Team proposal

Repeated positive evidence may become a proposal in `knowledge/evolution/PROPOSALS.md`. Include
exact change, affected files/roles, evidence, evaluation result, version/migration, risks, and
rollback. One proposal contains one coherent change.

## 6. Human-controlled promotion

Only the human owner may promote changes to source agent definitions, protocols, autonomy policy,
permissions, release rules, or hard gates. Log approved application and version in CHANGELOG.
Guardrails may be tightened from strong evidence; weakening requires explicit human review and a
compensating control.

## Knowledge sync

Reinstallation never overwrites project knowledge. Promoted lessons move project → reviewed source
repository → future installations. Never copy raw run history wholesale into every agent context;
route only relevant, fresh, scoped knowledge.

At retrospective answer: which prior lesson was used, which defect repeated despite a lesson, which
candidate was evaluated, and which proposal the human accepted/rejected. Without those answers the
system is journaling, not learning.
