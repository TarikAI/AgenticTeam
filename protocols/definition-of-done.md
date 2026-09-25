# Definition of done

"Done" is a claim with evidence. These are the minimum bars per work type; a task envelope may
add to them, never silently subtract.

## One verdict vocabulary

- **Findings** are `blocker`, `major`, `minor`, or `nit` (format: `review-discipline.md`).
- **Verdicts** are `PASS` (zero open blockers), `CONDITIONAL` (zero blockers; each open major
  has an owner and an approved checkpoint; the 05_verify exit also needs the human's waiver
  `stage-exit:05_verify:conditional`), or `FAIL` (any open blocker).
- The release verdict lives in the first lines of `VERIFICATION.md` (`workflow.md`).

## Typed evidence

Every completion carries typed evidence: `file:<path>`, `cmd:<exec-id>`, `commit:<sha>`,
`url:`, `note:`. Work that changes the workspace needs at least one `file:`, `cmd:`, or
`commit:`; a note alone is refused. Checks declared with `add-task --check` must pass through
`exec` (`complete --run-checks`). "I ran the tests" is not evidence; the `cmd:` record is.

## Feature (code)
- [ ] Implements every acceptance criterion (`AC-` id) in the task.
- [ ] Types, lint, and format clean; follows `coding-standards.md` and `ARCHITECTURE.md`.
- [ ] Tests written and passing, recorded as `cmd:` evidence.
- [ ] No secrets, debug leftovers, or dead code introduced.
- [ ] Independent review run (OCR delegation when `ocr` is present, else the
      `review-discipline.md` floor) with zero open blockers; the builder is not the sole verifier.
- [ ] Completion records artifacts, deviations, and discovered work (as new tasks).

## Bug fix
- [ ] Root cause stated, not just the symptom patched.
- [ ] A regression test that fails before the fix and passes after (`cmd:` both runs).
- [ ] Other occurrences of the same pattern checked.

## Infrastructure / DevOps
- [ ] Reproducible: IaC or a scripted procedure, no hand-configured snowflakes.
- [ ] Rollback path written before applying.
- [ ] Secrets in a secret store; least-privilege access.
- [ ] Verified from a clean environment.

## Admin / control surface
- [ ] Every screen traces to a server operation, server-side policy, authoritative data
      source, audit event where required, and a test (`admin-surfaces.md`); with
      `adminwright`, manifest `validate --phase release` and `coverage` both exit 0.
- [ ] Authorization matrix produced; denial paths tested server-side, including per-row
      scope in bulk operations.
- [ ] No mock, placeholder, or hard-coded value in the release path; static-by-design values
      registered with reason and approver.
- [ ] States per screen: loading, empty, filtered-empty, validation, conflict, error,
      forbidden, success.
- [ ] Interface closure audited in the rendered output (`interface-closure.md`).

## Design
- [ ] Covers empty, loading, error, success, and long-content overflow states.
- [ ] Meets WCAG 2.2 AA: contrast, focus order and visibility, labels, target size.
- [ ] Implementable: references real components and tokens.

## Documentation
- [ ] Tested by execution: following it from scratch works.
- [ ] Audience-appropriate (non-developer docs carry no unexplained jargon).

## Marketing asset
- [ ] On-brand per the brand strategist's voice and positioning.
- [ ] Claims true and substantiated; regulated-domain and platform ad rules respected.
- [ ] Has a measurable goal (metric and target) in `_marketing/MARKETING.md`.
- [ ] Not published and no budget spent without the human (`guardrails.md` hard gates).

## Research
- [ ] Sources cited with dates; current facts verified, not assumed.
- [ ] Findings separated from recommendations; confidence stated.
