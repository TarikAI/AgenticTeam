# Definition of Done

"Done" is a claim with evidence. These are the minimum bars per work type; a task's
brief may add to them, never subtract silently.

## Feature (code)
- [ ] Implements the acceptance criteria in the task/story — all of them.
- [ ] Types, lint, and format clean; follows `coding-standards.md` and the project's ARCHITECTURE.md.
- [ ] Unit/integration tests written and passing locally; attach the observed result to task state.
- [ ] No secrets, no debug leftovers, no dead code introduced.
- [ ] Reviewed by the assigned lead/reviewer; the builder is not the sole verifier.
- [ ] Task completion records artifacts, deviations, discovered work, and evidence.

## Bug fix
- [ ] Root cause identified and stated (not just symptom patched).
- [ ] Regression test that fails before the fix, passes after.
- [ ] Related occurrences of the same pattern checked.

## Infrastructure / DevOps
- [ ] Reproducible: IaC or a scripted, documented procedure — no hand-configured snowflakes.
- [ ] Rollback path documented before applying.
- [ ] Secrets in a secret store; least-privilege access.
- [ ] Verified from a clean environment (the "works on my machine" test).

## Design
- [ ] Covers all states: empty, loading, error, success, long-content overflow.
- [ ] Accessibility annotations (contrast, focus order, labels).
- [ ] Implementable: references real components/tokens, no ambiguous hand-waving.

## Documentation
- [ ] Tested by execution: following the doc from scratch actually works.
- [ ] Audience-appropriate (non-dev docs contain no unexplained jargon).

## Marketing asset
- [ ] On-brand per the brand strategist's voice/positioning doc.
- [ ] Claims are true and substantiated; regulated-domain rules respected (no fake testimonials,
      disclosures where required, platform ad policies checked).
- [ ] Has a measurable goal (metric + target) noted in MARKETING.md.
- [ ] **Not published and no budget spent without human approval.**

## Research
- [ ] Sources cited with dates; current-year information verified, not assumed.
- [ ] Findings separated from recommendations; confidence levels stated.
