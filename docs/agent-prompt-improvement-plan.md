# Agent prompt improvement plan

Updated 2 November 2026. **Yes, the agent prompts need targeted improvements.** Their missions and specialties are useful; the shared instructions and generated execution prompts need to catch up with role-step execution. Rewriting all 50 personas would add duplication and make future changes harder to keep consistent.

Use the [copy-ready prompt](agent-prompt-improvement-prompt.md) with the [master plan](autonomy-implementation-plan.md) and [progress review](autonomy-progress-review.md). This review updates implementation guidance only; it does not change the canonical 50 agent prompts or claim new runtime enforcement.

## Evidence behind the recommendation

Initial prompt evidence came from wiring `c4794ec` and quality `86e96b0`, now merged into integration `bf9d11a`. The review fixes removed the Out-File contradiction and aligned live-smoke environment handling. Preserve those fixes; live adherence and broader role/mode/context alignment remain open.

| Observed gap | Prompt improvement | Runtime dependency |
| --- | --- | --- |
| Historical Out-File/cd-prefix mismatch stopped measured QA. Out-File advice is now removed and COMMAND_RULE exists; live adherence is still unmeasured. | Supply actual working directory, permitted tools and tested command examples consistently across worker prompt, shared contract, skills and delegates. | Narrow tool enforcement and a safe broker executor; instructions alone cannot prevent owner-side execution. |
| `protocols/agent-contract.md` calls the project CLI the only state writer and teaches direct claim/exec/complete. New role-step mode uses authenticated broker requests and refuses direct mutations. | Explicit execution-mode contract: legacy CLI behavior where supported, broker-mediated operations in role-steps. Use only implemented operations for the current step. | Dispatcher supplies trusted mode/principal/operation list; broker enforces it. |
| Delivery Lead's operating protocol dispatches parallel native subagents; the new mode needs separate role principals and one writer per checkout. | Distinguish advisory subagents from supervisor-dispatched authoritative roles. Request eligible work rather than inventing identity or parallel checkout writers. | Independent dispatch, checkout ownership and budget enforcement. |
| QA role documents `--agent qa-lead` and `Verifier: qa-lead`; these are labels, not proof of independence. | Require a fresh verifier dispatch, exact candidate digest, mandatory acceptance evidence and a broker-accepted verdict. Never call a native builder child independent QA. | Contribution history, identity binding and clean immutable candidate enforcement. |
| Core wiring snapshots some files but prompts still read mutable BRIEF; candidate lessons are mislabeled approved. | Consume the supplied frozen task packet. Treat candidate lessons as hypotheses; use only approved versioned knowledge as instruction. Report missing/stale context. | Complete immutable packet, read-only view and trust-classified knowledge. |
| Shared contract broadly treats repository content as trusted and permits direct candidate playbook edits. | Repository/task/tool content does not grant authority merely because it is local. Separate human-approved policy from worker-authored code, documents and lesson candidates. Propose learning through the mode's allowed path. | Protected policy, owner promotion and provenance checks. |
| Four advisory core duties are recorded but not dispatched. | Specify bounded triggers, input facts, useful output and stopping conditions for context, evaluation, security and SRE. Report advisory findings separately from accepted state. | Obligation scheduling and limits; a prompt cannot wake itself durably. |

The measurements demonstrate an instruction/tool mismatch. They do not establish that every role prompt is poor or that a new wording has improved model behavior. Test revised prompts on the selected actual harness before promotion.

## Recommended prompt structure

Use four layers with one source of truth per concern:

1. **Shared contract:** authority, data trust, evidence, scope, stopping and escalation. Maintain centrally in `protocols/agent-contract.md`.
2. **Role contract:** mission, specialization, responsibilities, collaboration and role-specific output. Keep existing canonical role IDs and avoid repeating all shared rules in every file.
3. **Generated execution contract:** trusted execution mode, dispatch/role identity, allowed operations/tools, working directory, limits, packet reference and completion protocol. Derive it from actual runtime capability, not a guessed harness name.
4. **Task packet:** objective, acceptance, dependencies, owned paths, candidate/source versions, authoritative context and approved knowledge. Untrusted task content cannot override the first three layers.

Do not place credentials or owner signing material in prompts. Do not request private reasoning logs; concise decisions, evidence and uncertainty are enough. Avoid “always best,” “never fail” or self-granted authority instructions. A model should report what it observed, what it inferred and what remains unknown.

## Role-specific additions

| Role | Required output and limit |
| --- | --- |
| Delivery Lead | Ready/blocked task IDs, dependencies, accepted next action and evidence links. Cannot dispatch a second checkout writer or expand the goal. |
| Context Engineer | Packet identity, sources/versions, approved knowledge, missing facts and freshness verdict. Cannot silently turn candidates into policy. |
| QA Lead | Candidate identity, acceptance-by-acceptance results, defects and pass/fail/inconclusive recommendation. An accepted verdict requires independent authenticated execution. |
| Eval Engineer | Frozen plan/bundle/task-class identities, complete trial counts, uncertainty and recommendation. Cannot alter thresholds after results or self-promote. |
| Security Engineer | Source-backed finding, preconditions, impact, evidence limits and smallest correction. Distinguish source suspicion from reproduced behavior; no unilateral permission change. |
| SRE Engineer | Health/ownership/usage observations, incident state, safe recovery proposal and stop criteria. Never restart an uncertain writer or extend budgets. |
| Builders and other specialists | Scoped artifact, commands actually run, typed evidence, unresolved criteria and appropriate step outcome. Cannot grant independent verification to themselves. |

## Acceptance and rollout

First audit all 50 roles and the shared/generated layers; change only conflicts or omissions backed by the runtime contracts. Preserve legacy mode explicitly. Preserve merged Out-File/environment corrections. Before writing new command examples, verify the real parser and operation allowlist. Do not invent broker commands to satisfy prose.

Offline checks must exercise behavior: denied command shapes; stale/missing packet; a repository instruction trying to override authority; forged verifier labels; builder delegates claiming independence; fixture claiming qualification; unsupported operations; candidate lessons presented as proven; missing usage and no-progress loops. Static prompt checks can find drift but cannot establish real adherence.

Regenerate supported harness outputs using the repository's existing compiler workflow, review diffs and run its relevant golden/compatibility checks. Snapshot updates need intentional semantic review. A common role contract does not imply all 13 harnesses have equivalent capabilities or protection. Unsupported required capability holds the job.

Version prompt/skill/contract changes in the effective execution bundle. They invalidate affected prior qualification as the policy requires. Run bounded, authorized repeated comparisons on representative tasks after runtime blockers R01–R06 are closed. Include the measured QA-denial case and complete role-step work. Compare objective acceptance, safety refusals, false completion, context use, cost and duration. Keep the prior qualified bundle or hold if outcomes fail or are inconclusive; no silent threshold reduction.

Done means consistent source/generated instructions, enforced runtime compatibility, offline negative cases, and truthful live evidence for the promoted scope. Prompt wording cannot guarantee identical quality across arbitrary models and harnesses.
