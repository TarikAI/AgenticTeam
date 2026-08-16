# Learning ladder

`observation -> scoped lesson -> playbook candidate -> evaluation -> proposal -> human approval -> versioned promotion`

Each record includes source run/task, evidence, confidence, scope, counterexample, owner, review
date, and rollback. Promote only when evidence repeats across relevant cases or a human explicitly
accepts a one-case safety correction. Guardrails may be tightened from strong evidence; weakening
always requires explicit human review and a compensating control.
