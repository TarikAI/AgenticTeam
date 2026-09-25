# AgenticTeam v3 — progress

Authority: `docs/v3-upgrade-plan.md`. Integration branch: `v3` (from `main` @ `d0fb6cf`).

| Phase | Branch | Status | Commits | Acceptance evidence | Deviations |
|---|---|---|---|---|---|
| P0 Safety net | v3-p0-safety-net | done | 984ac07 | validate OK; 53 tests OK; real ~/.agentic-team untouched; 52 golden files | Phase branches named v3-pN-* (git forbids v3/ under branch v3) |
| P1 Runtime correctness | v3-p1-runtime | done | 8991bc1 | 83 tests OK (28 regression tests R-01..R-39 subset); install.sh all 7 harnesses; install.ps1 smoke; preflight OK | R-25 partial: max_concurrent_agents enforced; unused team.json defaults/fusion modes removed; context_target_tokens kept for P4 pack; tier handled in P5. R-17 (evidence) moves to P3 as planned. |
| P2 Authority, risk, audit | v3-p2-authority | done | 3f6173b | 101 tests OK (18 in test_authority: forgery fails closed, audit detects tampering, risk corpus, supervised!=autonomous, R-13, R-35, waiver, migrate) | Home material keyed by run_id.run_uid (found cross-project ledger collision during P2). Waiver of risk:<task> supersedes its pending risk checkpoint. |
| P3 Evidence, stage exits | v3-p3-evidence | pending | | | |
| P4 Events, budgets, ergonomics | v3-p4-ergonomics | pending | | | |
| P5 Harness compilers | v3-p5-harness | pending | | | |
| P6 Roster | v3-p6-roster | pending | | | |
| P7 Protocols, skills, templates, knowledge | v3-p7-law | pending | | | |
| P8 Team evaluation | v3-p8-evals | pending | | | |
| P9 Docs, migration, release | v3-p9-release | pending | | | |

## Follow-ups

- (none yet)
