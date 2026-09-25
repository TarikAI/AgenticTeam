---
name: agentic-execute-plan
description: "Build from a plan the user already wrote, without re-planning. Use when the user supplies an authoritative plan, spec, or task list."
---

# Agentic Execute Plan

Use entry mode `execute-only`. Preserve the supplied plan as the authority and derive bounded task packets from it with `.agentic-team/bin/agentic_team.py add-task`. Do not author a competing plan; raise gaps as a bounded question list with a recommended default each.
