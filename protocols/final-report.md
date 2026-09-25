# Final report

Every run ends with `runs/<id>/DELIVERY-REPORT.md`, the one document the human actually reads.
The ceo writes it in 07_learn (fullstack-engineer when no ceo is installed), with sections from
the delivery-lead and, for marketing work, the cmo. It must be true: every claim traces to run
artifacts, typed evidence, or ledger decisions.

## Two files, two authors

- `report` generates `DELIVERY-EVIDENCE.md` from state: completed tasks and their evidence,
  unfinished work, and every checkpoint decision. Run it first and link it.
- `DELIVERY-REPORT.md` is the ceo's narrative. `report` never overwrites it. Create it with
  `scaffold --artifact DELIVERY-REPORT.md`; the 07_learn exit contract refuses it while any
  `{{...}}` marker or `TODO` remains.

## Structure (the `delivery-report.md` template, in this order)

1. **Outcome:** the verified user outcome in one plain paragraph a non-developer recognizes;
   say what is done, partial, and cut (with the decision reference for each cut).
2. **Scope delivered:** what shipped, by `AC-` id, and how to try it (commands or URL, a
   two-minute tour of the main flow). If it cannot be run now, say why.
3. **Verification:** the `VERIFICATION.md` verdict line, verifier, verified SHA, and the key
   evidence (`cmd:` records, counts pasted from real runs, never estimated).
4. **Decisions and deviations:** ADRs in `_decisions/`, checkpoints, and waivers, each with
   its reference.
5. **Open risks and unfinished work:** ranked, each with an owner and a next step. An empty
   section is a red flag, not an achievement.
6. **Release and rollback:** the `RELEASE.md` summary, or why the release gate is still open.
7. **Cost and learning:** budget used (tasks, councils, reported tokens/USD from `metrics`),
   anything spent or approved, and the lessons recorded with `learn`.

## Rules

- Fit on about two screens. Detail lives in the linked artifacts; the report is the map.
- No process narration: the human needs the state of the product, not the story of the run.
  Stage history is in `log`.
- Marketing runs use the same seven sections with `_marketing/MARKETING.md` as the source:
  section 3 becomes the asset checklist and metrics baseline, section 7 lists every approval.
- A run that stopped early or failed still gets the report: sections 1, 5, and 6 become the
  honest account of where it stopped, why, and the cheapest path forward.
- The final chat message to the human is a compressed version: outcome, how to try it, and the
  decisions waiting on them.
