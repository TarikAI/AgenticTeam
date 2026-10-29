# Entry modes and plan respect

Adoption beats authorship. A human-supplied plan, PRD, specification, architecture, task list, or
explicit instruction is authoritative. The team may identify a bounded blocker or safety conflict;
it may not quietly replace the plan with its own preferred project.

## `idea`

Use when the user supplies a problem or desired outcome without an executable plan. Begin at
`00_intake` and progressively create product, solution, readiness, build, verification, release,
and learning artifacts.

## `plan-given`

Preserve the supplied document or path as the authority; do not edit it. Run one bounded conformance pass
for contradictions, genuinely blocking gaps, and safety/data/approval conflicts. Create tasks that
cite their exact source section. Do not substitute stack, scope, sequence, or architecture merely
for preference. Begin at readiness by default.

## `execute-only`

When the user says “just build,” convert their authority into task envelopes and begin at build.
Record only assumptions necessary to keep moving. Do not create a competing PRD or architecture.
Quality, verification, and hard human gates still apply.

## Blocking gaps: one bounded question list

Ask once, not in a drip. Collect every genuinely blocking gap into one numbered list (at most
about seven questions), each with a recommended default. Raise it as one
`checkpoint --kind decision` whose recommendation is the defaults. The defaults are a
recommendation, not a timeout: until the human approves, rejects, or resolves it, the
checkpoint stays unresolved and the stage cannot exit. Keep working on everything the questions
do not block.

A gap that is not blocking (a reversible choice inside the authority the plan already gives)
is not a question: take the safer default, record it in ASSUMPTIONS.md, and continue.

## Deviations: three lines

When the plan cannot be followed as written, state it in exactly three lines and record it with
`checkpoint --kind deviation`:

```text
Fails as written: <what breaks, with evidence>
Smallest fix: <the minimal change>
Cost of doing it as written: <consequence>
```

```text
python .agentic-team/bin/agentic_team.py checkpoint --project . --kind deviation --question "Fails as written: ..." --recommendation "Smallest fix: ..." --impact "Cost of doing it as written: ..." --alternatives "Do it as written" --evidence cmd:T-014-2 --rollback "Revert the fix commit"
```

`supervised` and `hitl` pause on it; `autonomous` records it and continues (`autonomy.md`).
Mechanical corrections may proceed when policy allows; structural changes to the human's plan
always need the human. An unrecorded deviation is a defect even when the code runs.

## Forced-planning harnesses

If a harness always creates a plan artifact, make it a faithful transcription of the supplied
authority with no invented scope. Do not pause merely to re-approve a plan the human already wrote;
pause only for the actual policy gates.
