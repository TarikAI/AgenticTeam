#!/usr/bin/env python3
"""Bridge: normalize review-gate findings into a verdict and remediation task packets.

Accepts findings in either schema used by the team:
- the OCR comment schema: {"path", "content", "start_line"?, "end_line"?, "category"?,
  "severity"?} with severity critical|high|medium|low
- the team finding format: {"severity": blocker|major|minor|nit, "file", "line"?,
  "claim", "scenario"?, "fix"?}

Produces:
- a gate verdict per agentic-verify: PASS (zero blockers), CONDITIONAL (zero blockers,
  one or more majors), FAIL (any blocker)
- remediation task packets (JSON) plus suggested `add-task` command lines for the
  orchestrator to run. This script never writes run state itself — the runtime CLI is
  the single state writer.

Exit codes: 0 = PASS, 1 = CONDITIONAL or FAIL (findings exist), 2 = usage/IO error.
Zero findings is a data point, not a verdict: report what was checked separately.
"""

import argparse
import json
import sys
from pathlib import Path

SEVERITY_MAP = {
    "critical": "blocker",
    "high": "blocker",
    "blocker": "blocker",
    "major": "major",
    "medium": "major",
    "minor": "minor",
    "low": "minor",
    "nit": "nit",
}

# categories that route the remediation task to a specialist owner
SECURITY_CATEGORIES = {"security", "injection", "xss", "sqli", "authz", "idor", "secrets"}


def normalize(raw):
    """Normalize one finding record; raise ValueError on an unusable record."""
    if not isinstance(raw, dict):
        raise ValueError("finding is not an object")
    severity = SEVERITY_MAP.get(str(raw.get("severity", "")).lower())
    if severity is None:
        raise ValueError(f"unknown severity: {raw.get('severity')!r}")
    path = raw.get("path") or raw.get("file")
    if not path:
        raise ValueError("finding has no path/file")
    line = raw.get("start_line") or raw.get("line")
    claim = raw.get("content") or raw.get("claim")
    if not claim:
        raise ValueError(f"finding on {path} has no content/claim")
    category = str(raw.get("category", "")).lower()
    return {
        "severity": severity,
        "file": str(path),
        "line": int(line) if line is not None else None,
        "claim": str(claim),
        "scenario": raw.get("scenario"),
        "fix": raw.get("fix"),
        "category": category or None,
        "raw": raw,
    }


def verdict(findings):
    if any(f["severity"] == "blocker" for f in findings):
        return "FAIL"
    if any(f["severity"] == "major" for f in findings):
        return "CONDITIONAL"
    return "PASS"


def task_owner(finding):
    if finding["category"] in SECURITY_CATEGORIES:
        return "security-engineer"
    return "code-owner"  # orchestrator routes to the owning lead/engineer


def task_id(index):
    return f"remediate-{index:03d}"


def build_tasks(findings):
    """Group minor/nit findings into one batched task; one task per blocker/major."""
    tasks = []
    batched = []
    for index, finding in enumerate(findings, start=1):
        anchor = f"{finding['file']}:{finding['line']}" if finding["line"] else finding["file"]
        summary = f"[{finding['severity'].upper()}] {anchor} — {finding['claim']}"
        if finding["severity"] in ("minor", "nit"):
            batched.append(summary)
            continue
        tasks.append({
            "id": task_id(len(tasks) + 1),
            "owner": task_owner(finding),
            "risk": "R1",
            "summary": summary,
            "acceptance": [
                f"Fix: {finding['fix'] or finding['claim']}",
                "Regression test that fails before the fix and passes after",
                "Re-run the review gate on the touched files",
            ],
            "evidence": [f"finding: {json.dumps(finding['raw'], ensure_ascii=False)}"],
        })
    if batched:
        tasks.append({
            "id": task_id(len(tasks) + 1),
            "owner": "code-owner",
            "risk": "R1",
            "summary": f"Batched minor/nit review findings ({len(batched)})",
            "acceptance": ["Each finding fixed or explicitly waived with a reason"],
            "evidence": batched,
        })
    return tasks


def add_task_command(task):
    acceptance = " && ".join(task["acceptance"])
    evidence = " && ".join(task["evidence"])
    return (
        f'python .agentic-team/bin/agentic_team.py add-task --project . '
        f'--owner {task["owner"]} --risk {task["risk"]} '
        f'--summary "{task["summary"]}" --acceptance "{acceptance}" --evidence "{evidence}"'
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("findings", help="findings JSON file (array, either schema)")
    parser.add_argument("--output", help="write task packets JSON here (default: stdout only)")
    parser.add_argument("--commands", action="store_true",
                        help="print suggested add-task command lines")
    args = parser.parse_args(argv)

    try:
        raw = json.loads(Path(args.findings).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"cannot read findings: {exc}")

    try:
        findings = [normalize(item) for item in raw]
    except ValueError as exc:
        parser.error(str(exc))

    result = {
        "total_findings": len(findings),
        "by_severity": {
            level: sum(1 for f in findings if f["severity"] == level)
            for level in ("blocker", "major", "minor", "nit")
        },
        "verdict": verdict(findings),
        "tasks": build_tasks(findings),
    }
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Task packets written: {args.output}")
    else:
        print(text)
    if args.commands:
        print("\nSuggested add-task invocations (runtime CLI is the state writer):")
        for task in result["tasks"]:
            print("  " + add_task_command(task))
    print(f"Review gate verdict: {result['verdict']}", file=sys.stderr)
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
