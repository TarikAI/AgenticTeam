# Release — {{project}}

Owner: release-manager (devops-engineer when not installed). Stage: 06_release.

## Artifact identity

{{commit SHA, build digest, version}}

## Rollout

{{steps, flags, canary percentage, abort thresholds, observation window}}

## Data changes

{{migrations: forward tested / backward tested / irreversible?}}

## Monitoring and rollback

{{dashboards and alerts to watch; tested rollback procedure and its evidence}}

## Supply chain

{{SBOM location, vulnerability scan result, license check}}

## Approval

{{human release gate (every profile except unattended with no task above R1): the id of the release decision checkpoint the human approves; unattended run with no task above R1: "Executable release" and the rollback rehearsal task id, with no release checkpoint raised}}
