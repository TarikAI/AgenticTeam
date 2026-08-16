# Final Report Protocol

Every build ends with `.agentic-team/runs/<run-id>/DELIVERY-REPORT.md` — the single document the human actually
reads. It is written by the ceo (or fullstack-engineer in solo mode) from the
delivery-lead's ship report, in plain language, and it must be TRUE: every claim in it
traces to evidence in active run documents or executed checks.

The final chat message to the human is a compressed version of this report (the
summary + how to run it + decisions needed), never a wall of process narration.

## Template

```markdown
# Final Report — <project name>
date · build preset used · harness(es)

## 1. What you got (plain language, 3–6 sentences)
What was built, for whom, and what it does — written so a non-dev recognizes their
idea. State clearly what is DONE, what is PARTIAL, and what was CUT (with the
decision reference for each cut).

## 2. Try it now
Exact steps to see it working: commands to run locally, or the staging URL, plus a
2-minute "click this, then this" tour of the main flows. If it cannot be run right
now, say why and what's needed.

## 3. Evidence of quality
| Check | Result | Where |
|---|---|---|
| Test suite | e.g. 148/148 passing | QA.md, CI |
| Acceptance criteria | e.g. 21/23 pass, 2 waived | QA.md §verdict |
| Code review sign-off | approved / notes | STATUS.md |
| Security sign-off | approved / open risks | QA.md §security |
| Docs verified by execution | yes/no | tech-writer note |
Numbers are pasted from actual runs — never estimated.

## 4. Known limitations & risks
Honest list, ranked. What breaks, what's untested, what shortcuts were recorded, what
the top security or operational risks are. An empty section here is a red flag, not
an achievement.

## 5. What's next (recommendation)
The 3–5 highest-value next steps (from PRD "later" list + retro findings), each with
a one-line why. Plus any decisions currently waiting on the human.

## 6. Where everything lives
One-line map: code entry points, run/ documents, how to redeploy, who (which agent)
to summon for what kind of follow-up work.

## 7. Costs & approvals ledger
Anything that was spent or approved during the build (deploys, services, skills
installed), each with its approval reference.
```

## Rules
- Length target: the whole report fits on ~2 screens. Detail lives in the linked
  active run documents; the report is the map, not the territory.
- No process theater: the human doesn't need the story of the build, they need the
  state of the product. Phase-by-phase narration belongs in STATUS.md only.
- Marketing builds use the same template with MARKETING.md artifacts: section 3
  becomes campaign/asset checklist + metrics baseline, section 7 lists all approvals.
- If the build stopped early or failed, the report is still written — sections 1, 4
  and 5 become the honest account of where it stopped, why, and the cheapest path
  forward. Never skip the report because the news is bad.
