# Review discipline

The floor procedure for reviewing any diff or existing code — with or without the
`open-code-review` (OCR) tooling installed. `coding-standards.md` owns what to
check; this protocol owns how to review and how findings are reported.

## Procedure

1. **Context first.** Read the task brief and the relevant ARCHITECTURE.md contract before
   the diff. Contract compliance is check #1 — a diff can be locally clean and globally
   wrong. Review the diff and its blast radius: callers and contract consumers, not just
   changed lines.
2. **Correctness pass.** Trace execution paths: edge inputs, error paths, off-by-ones,
   race conditions and thread-safety, null/undefined flow, resource leaks, broken
   invariants. For each suspected bug, construct the failing scenario — concrete input →
   wrong outcome. If you cannot construct one, downgrade to a question, not a finding.
3. **Security pass.** Injection surfaces (parameterized queries only), unsafe rendering
   (XSS/output encoding), authorization on every resource access (IDOR), input validation
   gaps, secrets, SSRF/path traversal on anything touching files or URLs.
4. **Verify the tests.** Do they assert the acceptance criteria? Would they fail if the
   feature broke?

## Findings

- Format: `[SEV] file:line — claim`, with scenario and fix; SEV: blocker · major · minor ·
  nit. Findings produced by a tool keep their schema (path, start/end line, category,
  severity) and are normalized to this format when recorded in task state.
- Coverage accounting: every reviewable file ends `reviewed` or `skipped` with a concrete
  reason. Do not stop at the first high-severity finding. Discard likely false positives
  silently — precision over noise.
- Severity honesty both ways: no blocker inflation for style, no courtesy downgrades.
- Zero findings is a data point, not a verdict. Report what was checked, how, and with
  what coverage.

## With OCR installed

Use delegation mode (no API key, no endpoint): `ocr delegate preview --format json` for
the reviewable file list and diff mode, `ocr delegate rule --format json <paths...>` for
per-file rule checklists, then the diffs via git per the reported mode (untracked files
are read whole). The reviewing agent must not be the author of the diff. Full-mode
`ocr review` / `ocr scan` requires a configured LLM endpoint and runs in CI only — never
with agent-held credentials.
