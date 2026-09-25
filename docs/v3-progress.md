# AgenticTeam v3 — progress

Authority: `docs/v3-upgrade-plan.md`. Integration branch: `v3` (from `main` @ `d0fb6cf`).

| Phase | Branch | Status | Commits | Acceptance evidence | Deviations |
|---|---|---|---|---|---|
| P0 Safety net | v3-p0-safety-net | done | 984ac07 | validate OK; 53 tests OK; real ~/.agentic-team untouched; 52 golden files | Phase branches named v3-pN-* (git forbids v3/ under branch v3) |
| P1 Runtime correctness | v3-p1-runtime | done | 8991bc1 | 83 tests OK (28 regression tests R-01..R-39 subset); install.sh all 7 harnesses; install.ps1 smoke; preflight OK | R-25 partial: max_concurrent_agents enforced; unused team.json defaults/fusion modes removed; context_target_tokens kept for P4 pack; tier handled in P5. R-17 (evidence) moves to P3 as planned. |
| P2 Authority, risk, audit | v3-p2-authority | done | 3f6173b | 101 tests OK (18 in test_authority: forgery fails closed, audit detects tampering, risk corpus, supervised!=autonomous, R-13, R-35, waiver, migrate) | Home material keyed by run_id.run_uid (found cross-project ledger collision during P2). Waiver of risk:<task> supersedes its pending risk checkpoint. |
| P3 Evidence, stage exits | v3-p3-evidence | done | 0d0fa07 | 115 tests OK (14 in test_evidence: R-10 empty run refused at 00, R-17 evidence, exec/checks, verifier independence, verdict/CONDITIONAL/FAIL, integration SHA with git) | adaptive profile needs no RELEASE.md (plan §5.5 lighter profile); final-report template replaced by delivery-report.md |
| P4 Events, budgets, ergonomics | v3-p4-ergonomics | done | 99624d9 | 127 tests OK (12 in test_orchestration: events outside state, chain tamper detection, next/board/pack 2K-8K/brief, metrics, budget warn/stop/waive, migrate) | Plan target 'state.json < 40 KiB at 200 tasks' was unrealistic (tasks live in state, ~690 B each = 138 KiB). Replaced by: state no longer grows with events (verified). Budget blocks only when exceeding the limit. |
| P5 Harness compilers | v3-p5-harness | done | b3675ca | 148 tests OK (21 in test_harness); install.sh + doctor (incl. hook self-test) clean for all 13 harnesses | Antigravity hooks and Gemini policy.toml not emitted (formats unverified, per plan A.5). Kiro prompt uses file://./prompts/<id>.md relative to the agent file; OpenCode command patterns come from new 'globs' lists on policy command rules. |
| P6 Roster | v3-p6-roster | done | 5f49a72 | 153 tests OK; validate runs roster lint (banned terms, skeleton, descriptions, role ids, single owner per artifact, 400-2500 tokens); compiled prompts 566-1389 tokens | Rewritten by 6 parallel subagents from one brief, then linted. untrusted-content, secrets-and-sensitive-data, supply-chain protocols written early (roles reference them). Descriptions adapted from B.4 drafts to fit 300 chars + exclusion clause. |
| P7 Protocols, skills, templates, knowledge | v3-p7-law | done | 1fd3cf7 | 160 tests OK (test_law: no retired vocabulary, gate lists match policy, templates used/present, protocol refs resolve, Agent Skills spec; learn/promote) | Found and fixed: Windows NUL stdin reports isatty() so the token prompt hung automated callers (now checks for a real console). Plan's fusion --file/sealed/ commit-reveal not implemented; privacy is guard-hook enforced on Claude Code, instruction elsewhere. |
| P8 Team evaluation | v3-p8-evals | done | c2b44c3 | 163 tests OK; evals/run_scenarios.py 6/6 scenarios pass (101 CLI steps against installed CLIs); CI step added | Live-agent smoke eval is documented (protocols/team-evaluation.md) but not automated: it needs model credentials and is opt-in by design. |
| P9 Docs, migration, release | v3-p9-release | pending | | | |

## Follow-ups

- (none yet)
