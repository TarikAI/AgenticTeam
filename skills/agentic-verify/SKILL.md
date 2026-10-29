---
name: agentic-verify
description: Independently verify an AgenticTeam build in stage 05_verify - trace every AC- acceptance id to an executed check, review the integrated diff (OCR delegation when installed), run the project's tests through the CLI, write VERIFICATION.md with its Verdict/Verifier/Verified-SHA header, and turn findings into remediation tasks. Use for final review, audit mode, release readiness, or whenever a builder's completion claim needs an independent verdict. Not for the builder's own self-review.
compatibility: Needs an AgenticTeam installation in the project (the bus at .agentic-team/, CLI at .agentic-team/bin/agentic_team.py), Python 3.10+, and git for the diff and Verified-SHA. The ocr CLI is optional (delegation mode, no endpoint).
---

# Agentic Verify

Runbook for the verifier (qa-lead; fallback code-reviewer) and the orchestrator who sets it up.
Rules: `.agentic-team/protocols/workflow.md` (the 05_verify exit), `.agentic-team/protocols/review-discipline.md`
(review floor and OCR delegation), `.agentic-team/protocols/admin-surfaces.md` (admin release
checks). Matrix dimensions: `references/verification-matrix.md`.

Exit codes: 0 ok; 1 error; 2 human gate → stop and present the checkpoint; 3 blocked → stop and
show what the human must run; 64 usage. `findings-to-tasks` differs: 0 PASS, 1 findings exist,
2 usage or I/O error.

## 1. Inputs

```text
python .agentic-team/bin/agentic_team.py status --project . --json
```

Collect: `stage` (must be `05_verify`), `integration_sha` (HEAD recorded when 04_build exited),
the current HEAD (`git rev-parse HEAD`; the verdict names this, and it must still be HEAD when
you write it), the 04_build tasks and who held them, and the base commit (`base_sha`, which
`init-run` recorded; ask the human only when it is null). Read the `AC-` ids in `<run>/PRD.md` (or `BRIEF.md`) and the contracts in
`<run>/ARCHITECTURE.md`.

**Independence check:** if the intended verifier appears as `claimed_by` or in `failures` of any
04_build task, stop and choose another installed role; the exit contract refuses a verifier who
built.

## 2. Verification task (orchestrator)

```text
python .agentic-team/bin/agentic_team.py add-task --project . --id V-1 --title "Independent verification" --owner qa-lead --action test --target local --verifies T-API-1 --verifies T-UI-1 --input .agentic-team/runs/<run-id>/PRD.md
python .agentic-team/bin/agentic_team.py brief --project . --task V-1
```

Hand the printed brief to a fresh qa-lead subagent. Activated specialists (security, privacy,
accessibility, performance) get their own review tasks in this stage.

## 3. Checks (verifier)

```text
python .agentic-team/bin/agentic_team.py claim --project . --task V-1 --agent qa-lead
python .agentic-team/bin/agentic_team.py exec --project . --task V-1 --agent qa-lead -- <command>
```

Run each of these as `<command>`, one `exec` per command (put `--shell` before `--` when the
command needs pipes or shell quoting):

1. `git diff --stat <base>..HEAD`, the scope of review (remediation after `integration_sha`
   is part of it);
2. the project's test command (from ARCHITECTURE.md or the build tasks' `--check` commands);
3. if `_context/capabilities.json` lists the `ocr` CLI, the delegation sequence from
   `.agentic-team/protocols/review-discipline.md`: `ocr delegate preview --format json`, then
   `ocr delegate rule --format json <paths...>`.

Without OCR, apply the review floor by hand with full file coverage. With `adminwright`, its
`validate --phase release` and `coverage` must exit 0 (run them through `exec`). Each check's exec
id (`V-1-N`) is the evidence cited in the matrix.

## 4. VERIFICATION.md

```text
python .agentic-team/bin/agentic_team.py scaffold --project . --artifact VERIFICATION.md
```

The first three lines must read exactly:

```text
Verdict: PASS|CONDITIONAL|FAIL
Verifier: qa-lead
Verified-SHA: <the current HEAD you verified, or none without git>
```

The exit contract compares that line with HEAD at `advance` time, and again when the release
stage exits. If anyone commits after you write it (a remediation, a version bump), verify again
at the new HEAD and update the line; a stale verdict is refused, not stretched.

Fill the traceability matrix (one row per `AC-` id, each with an exec id, file, or commit),
findings (`blocker|major|minor|nit`, `file:line`, failing scenario, owner), and review coverage.
Remove every `{{...}}` marker. Exactly one verdict applies. PASS = no open blocker or major, and
every required criterion passed with evidence. CONDITIONAL = no open blocker, every required
criterion passed, open majors each with an owner (the exit also needs the human's waiver).
FAIL = any open blocker or failed required criterion. A check that was not run is unknown, never
passed: mark the row `unknown`, and an unknown required criterion is FAIL until it runs. Never
weaken an acceptance criterion to reach PASS.

## 5. Remediation

Write findings as a JSON array (OCR comment schema or `{severity, file, line, claim, scenario,
fix}`) to `<run>/05_verify/findings.json`, then:

```text
python .agentic-team/bin/agentic_team.py findings-to-tasks .agentic-team/runs/<run-id>/05_verify/findings.json --project . --check "<project test command>" --apply
```

Tasks land in the current stage, owned by installed writing roles; the verifier re-verifies after
they complete and updates the header lines.

## 6. Finish

```text
python .agentic-team/bin/agentic_team.py complete --project . --task V-1 --agent qa-lead --evidence file:.agentic-team/runs/<run-id>/VERIFICATION.md --evidence cmd:V-1-2
python .agentic-team/bin/agentic_team.py advance --project .
```

`advance` exit 1 lists what the verdict check still needs. CONDITIONAL needs the human's waiver
`stage-exit:05_verify:conditional`, run by them with their token; present it and stop.

## Stop conditions

- the verifier held any 04_build task;
- the same check fails twice with the same error after remediation;
- exit 2 or 3; a budget exhausted;
- a check would need any hard-gate action listed in `.agentic-team/protocols/guardrails.md`
  outside a task whose risk checkpoint the human approved.
