# Verification matrix

The matrix in `VERIFICATION.md` has one row per `AC-` id; add one row per material risk that is
in scope. Every Evidence cell names an exec id (`V-1-3`), a project file, or a commit. "File
exists" and "builder says complete" are not evidence.

## Dimensions to cover when in scope

| Dimension | Typical check | Usual reviewer |
|---|---|---|
| Functional journeys | end-to-end test per journey | qa-lead |
| Data integrity, migrations | migration up/down on production-shaped fixtures | database-engineer review |
| Authentication, authorization | denial paths (403/404), per-object scope, bulk per-row authz | security-engineer |
| Abuse and security boundaries | injection, XSS render paths, SSRF, secrets in diff | security-engineer |
| Privacy lifecycle | collection, retention, export, deletion | privacy-engineer |
| Accessibility | WCAG 2.2 AA: keyboard walk, labels, contrast | accessibility-specialist |
| Performance | p95 under the stated load | performance-engineer |
| Observability, backup/restore | alerts fire, restore drill | sre-engineer |
| Deployment and rollback | rollback rehearsed on staging | release-manager |
| Admin and support operations | adminwright `validate --phase release` and `coverage`, or the hand-made equivalents | platform-admin-engineer review |

## Finding severity

`blocker` (release-stopping), `major` (must have an owner), `minor`, `nit`. Evidence labels in
findings: observed (you ran it), reported (someone else's record), inferred (reasoning only).
