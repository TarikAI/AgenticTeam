# Dependencies and supply chain

Adding a dependency is a decision with a risk class (`add-task --action add-dependency`, R2), not a
side effect of writing code.

## Before adding a package

1. Confirm it exists under exactly that name in the official registry and is not a typosquat or a
   model-hallucinated name: check publish age, weekly downloads, repository link, maintainers,
   and recent releases.
2. Prefer a maintained, widely used package over a new one; prefer the standard library or an
   existing dependency over adding any.
3. Check the license against the allowlist: MIT, Apache-2.0, BSD-2/3-Clause, ISC, MPL-2.0.
   Copyleft (GPL, AGPL, LGPL) or unknown licenses need an ADR and compliance-advisor's review.
4. Record the choice and the alternatives in the task evidence.

## Installing

- Commit lockfiles; install reproducibly (`npm ci`, `pnpm install --frozen-lockfile`,
  `uv sync --locked`, `pip install --require-hashes`).
- Disable install scripts by default (`--ignore-scripts`) unless the package needs them and the
  task says why.
- Never pipe a remote script into a shell (`curl … | sh`); global or system-wide installs are a
  hard human gate (R4, `system-change`).

## Verifying (05_verify and 06_release)

- Dependency vulnerability scan through `exec` (`npm audit --omit=dev`, `pip-audit`,
  `osv-scanner`), with the threshold stated in READINESS.md: no known critical or high
  vulnerability in shipped code without a human waiver.
- SBOM generated for the release (`syft` or a CycloneDX tool) and referenced in RELEASE.md,
  together with the license check result.
- devops-engineer wires these into CI; security-engineer owns the policy and reviews results.
