Verdict: {{PASS|CONDITIONAL|FAIL}}
Verifier: {{installed role id that built none of the verified work}}
Verified-SHA: {{the current HEAD this verdict covers, or "none" when the project has no git history}}

# Verification — {{project}}

Owner: qa-lead. Stage: 05_verify. Exactly one verdict applies. PASS = no open blocker or major,
and every required criterion passed with evidence. CONDITIONAL = no open blocker, every required
criterion passed, and each open major has an owner and the human's waiver
(`stage-exit:05_verify:conditional`). FAIL = any open blocker or failed required criterion. A
check that was not run is unknown, never passed: an unknown required criterion is FAIL until run.

## Traceability matrix

| Requirement | Check (command or procedure) | Result | Evidence |
|---|---|---|---|
| AC-1 | {{check}} | {{pass/fail/unknown (not run)}} | {{exec id, file, or commit}} |

## Findings

| Severity | Location | Finding | Owner | Status |
|---|---|---|---|---|
| {{blocker/major/minor/nit}} | {{file:line}} | {{claim and failing scenario}} | {{role}} | {{open/fixed/waived}} |

## Review coverage

{{files reviewed / skipped with reasons; specialist reviews and their results}}
