# Coding Standards

Baseline standards for all code this team produces, in any stack. `ARCHITECTURE.md`
may tighten these per project; it may not loosen them without a recorded decision.

## Staying current (mandatory)
- Before pinning any framework/library version, verify the current stable version and its
  breaking changes via official docs or the registry (npm, PyPI, crates.io, ...). Do not
  trust training-data memory for versions or APIs.
- Prefer boring, mainstream, actively-maintained dependencies. Every new dependency must
  earn its place — record non-obvious choices in `DECISIONS.md`.

## Languages & typing
- Use typed languages/modes: TypeScript over JS (strict mode on), Python with type hints
  (checked by mypy/pyright), etc.
- Lint + format from day one: configure the stack's standard toolchain (eslint/prettier or
  biome, ruff, gofmt, clippy...) in the scaffold task, enforced in CI.

## Architecture & style
- Small modules, single responsibility, dependency direction inward (domain logic does not
  import framework glue).
- 12-factor for services: config via environment, stateless processes, logs to stdout.
- APIs: consistent naming, versioned routes, meaningful status codes, validated input at
  the boundary (schema validation — zod/pydantic/etc.), pagination on all list endpoints.
- Errors: no swallowed exceptions; user-safe messages out, detailed context logged.
  Fail loudly in dev, degrade gracefully in prod.
- Comments only for what code cannot say (invariants, why-not-the-obvious-way). No narration.

## Data
- Migrations for every schema change (never hand-edited databases), reversible where possible.
- Indexes justified by real query patterns; no premature denormalization.
- PII identified and minimized; encryption at rest for secrets; soft-delete where recovery matters.

## Security (see also guardrails §2)
- Parameterized queries only. Output encoding against XSS. CSRF protection on state-changing
  browser routes. Rate limiting on auth and expensive endpoints.
- Modern password hashing (argon2/bcrypt), short-lived tokens, least-privilege service accounts.
- Dependencies scanned (npm audit / pip-audit / osv) during hardening.

## Testing
- Test pyramid: many fast unit tests, focused integration tests on real seams (db, API),
  a few end-to-end happy paths. Coverage follows risk, not a vanity number.
- Every bug fixed gets a regression test. Every task's DoD includes its tests passing.
- Tests must run headless with one command from a clean checkout (`npm test`, `pytest`, ...).

## Frontend
- Accessibility is not optional: semantic HTML, keyboard navigable, WCAG 2.1 AA contrast,
  labels on all inputs.
- Responsive by default; performance budgets (bundle size, LCP) noted in ARCHITECTURE.md.
- Design tokens/theme in one place; no scattered magic colors or spacing.

## Git & delivery
- Conventional commits (`feat:`, `fix:`, `chore:`...), small and coherent.
- Never commit secrets, .env files, or build artifacts. Maintain .gitignore in the scaffold.
- CI runs lint + typecheck + tests on every push; a red main branch is the team's top priority.

## Documentation
- README that takes a newcomer from clean checkout to running app.
- Every service/module has a header note: what it is, what depends on it.
- Public API surface documented (OpenAPI where applicable).
