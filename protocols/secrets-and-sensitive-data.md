# Secrets and sensitive data

Agents handle code, not credentials. Everything here is instruction the team follows; the harness
rules in `harness-security.md` and the hard human gates back it where they can.

## Secrets

- The human provisions development secrets through a gitignored `.env` (or the platform's secret
  store). Agents never read `.env` values into prompts, evidence, logs, or reports; they keep
  `.env.example` current with names and placeholder values only.
- Production and payment credentials never enter an agent's environment. Handling real
  credentials or payment methods is a hard human gate (R4).
- Code reads secrets from the environment or a secret manager; no secret literal in code,
  tests, fixtures, docs, or commit messages.
- A secret scan runs in 05_verify through `exec` (for example `gitleaks detect --no-banner`) and
  must report zero findings; its exec id is evidence in VERIFICATION.md.
- The owner token, the bound owner key, and the decision ledger live in `~/.agentic-team`; agents
  never read that folder (the guard hook denies it). Tokens of closed runs can be deleted.

## If a secret leaks

1. Stop the affected work and do not "clean it up" by rewriting history yourself.
2. Raise `checkpoint --kind decision` (R4) naming where it leaked and since when.
3. The human rotates the credential. History rewriting or force-pushing happens only under an
   approved R4 task.
4. Record the lesson with `learn` without repeating the secret.

## Sensitive data and fixtures

- Test data is synthetic by default, produced by seeded generators.
- Production-derived data is used only after an approved R3 checkpoint and documented
  anonymisation; never real PII in prompts, evidence, lessons, playbooks, screenshots, or
  reports.
- Data classification drives routing: personal, health, financial, or children's data activates
  privacy-engineer (and compliance-advisor for regulated regimes).
- Run artifacts are project files: redact evidence strings, events, and reports; keep
  `runs/**/_evidence/` out of version control unless reviewed.
