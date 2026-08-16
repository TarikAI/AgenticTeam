---
name: agentic-verify
description: Independently verify an AgenticTeam-built product against requirements, architecture, security, quality, and operational evidence before release. Use for final review, audit mode, release readiness, acceptance checks, or whenever a builder's completion claim needs an independent verdict.
---

# Agentic Verify

The verifier must not be the sole builder of the artifact under review. Read
`references/verification-matrix.md`, the authoritative requirements, current architecture,
task evidence, and integrated result.

## Verify

1. Build a traceability matrix before inspecting green checkmarks.
2. Reproduce critical checks in the integrated environment; distinguish observed, reported,
   and inferred evidence.
3. Review changed behavior and boundaries, not just changed lines. Include failure, denial,
   rollback, migration, and recovery paths where applicable.
4. Activate security, privacy, accessibility, performance, compliance, or SRE review according
   to scope and risk.
5. Classify findings by user/business impact, evidence, reproduction, and blocking status.
6. Issue `PASS`, `CONDITIONAL`, or `FAIL`. Never weaken acceptance criteria to obtain PASS.

Return matrix, executed checks, findings, residual risk, missing evidence, and precise remediation
tasks. A conditional verdict identifies the owner and required release gate.
