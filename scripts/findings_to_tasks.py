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
- remediation task packets (JSON), runnable `add-task` command lines (--commands), or
  the tasks added directly through the runtime (--apply). Owners are always installed
  roles that may write; a read-only reviewer is named as re-verifier, never as owner.

Exit codes: 0 = PASS, 1 = CONDITIONAL or FAIL (findings exist), 2 = usage/IO error.
Zero findings is a data point, not a verdict: report what was checked separately.
"""

import argparse
import json
import re
import shlex
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


FRONTEND_SUFFIXES = (".tsx", ".jsx", ".ts", ".js", ".vue", ".svelte", ".css", ".scss", ".html")
BACKEND_SUFFIXES = (".py", ".go", ".java", ".kt", ".rb", ".rs", ".cs", ".php", ".sql")
WRITE_ACCESS = {"workspace-write", "orchestrate"}
FALLBACK_OWNERS = ("fullstack-engineer", "backend-engineer", "frontend-engineer", "delivery-lead")
UNASSIGNED = "UNASSIGNED"


def _normalized(path):
    return str(path).replace("\\", "/").strip("/").lower()


def _covers(owned, file):
    owned, file = _normalized(owned), _normalized(file)
    return bool(owned) and (file == owned or file.startswith(owned + "/"))


def resolve_owner(finding, context=None):
    """Pick an installed role that may WRITE the fix; never a read-only reviewer.

    Order: the owner of the task whose owned paths cover the file, then a role by file
    type, then generalists. Returns UNASSIGNED when no writable role is installed.
    """
    context = context or {}
    installed = context.get("installed")  # {id: access}; None = assume the default roster

    def writable(agent_id):
        if installed is None:
            return True
        return installed.get(agent_id) in WRITE_ACCESS

    for task in (context.get("tasks") or {}).values():
        if any(_covers(owned, finding["file"]) for owned in task.get("owned_paths", [])) and writable(task["owner"]):
            return task["owner"]
    suffix = Path(finding["file"]).suffix.lower()
    preferred = []
    if suffix in FRONTEND_SUFFIXES:
        preferred.append("frontend-engineer")
    elif suffix in BACKEND_SUFFIXES:
        preferred.append("backend-engineer")
    for agent_id in preferred + list(FALLBACK_OWNERS):
        if writable(agent_id) and (installed is None or agent_id in installed):
            return agent_id
    return UNASSIGNED


def _next_ids(count, taken):
    ids, number = [], 1
    while len(ids) < count:
        candidate = f"remediate-{number:03d}"
        if candidate not in taken:
            ids.append(candidate)
        number += 1
    return ids


def build_tasks(findings, context=None, stage=None, checks=None):
    """One task per blocker/major; minor and nit findings are batched into one task.

    `checks` are the acceptance commands every remediation task must pass (typically the
    project's test command): the runtime refuses a build task by a writing role without one.
    """
    context = context or {}
    checks = list(checks or [])
    individual = [f for f in findings if f["severity"] in ("blocker", "major")]
    batched = [f for f in findings if f["severity"] in ("minor", "nit")]
    ids = _next_ids(len(individual) + (1 if batched else 0), set((context.get("tasks") or {}).keys()))
    tasks = []

    def summary(finding):
        anchor = f"{finding['file']}:{finding['line']}" if finding["line"] else finding["file"]
        return f"[{finding['severity'].upper()}] {anchor} - {finding['claim']}"

    for finding in individual:
        inputs = [f"finding: {json.dumps(finding['raw'], ensure_ascii=False)}"]
        if finding["category"] in SECURITY_CATEGORIES:
            inputs.append("re-verify: security-engineer reviews the fix (security finding)")
        tasks.append({
            "id": ids[len(tasks)],
            "title": summary(finding),
            "owner": resolve_owner(finding, context),
            "stage": stage,
            "risk": "R1",
            "paths": [finding["file"]],
            "inputs": inputs,
            "acceptance": [
                f"Fix: {finding['fix'] or finding['claim']}",
                "Regression test that fails before the fix and passes after",
                "Re-run the review gate on the touched files",
            ],
            "evidence_contract": ["test output showing the regression test passing", "review gate re-run result"],
            "checks": checks,
        })
    if batched:
        files = sorted({finding["file"] for finding in batched})
        tasks.append({
            "id": ids[len(tasks)],
            "title": f"Batched minor/nit review findings ({len(batched)})",
            "owner": resolve_owner(batched[0], context),
            "stage": stage,
            "risk": "R1",
            "paths": files,
            "inputs": [summary(finding) for finding in batched],
            "acceptance": ["Each finding fixed or explicitly waived with a reason"],
            "evidence_contract": ["list of findings with fix or waiver"],
            "checks": checks,
        })
    return tasks


def add_task_argv(task, project=".", run=None):
    """argv (after the CLI path) for one task; every flag exists in `add-task`.

    With a run, the command is pinned to it: running it later, after CURRENT moved, still adds the
    task to the run the findings were resolved against.
    """
    argv = ["add-task", "--project", project]
    if run:
        argv += ["--run", run]
    argv += ["--id", task["id"], "--title", task["title"], "--owner", task["owner"], "--risk", task["risk"]]
    if task.get("stage"):
        argv += ["--stage", task["stage"]]
    for path in task.get("paths", []):
        argv += ["--path", path]
    for value in task.get("inputs", []):
        argv += ["--input", value]
    for value in task.get("acceptance", []):
        argv += ["--acceptance", value]
    for value in task.get("evidence_contract", []):
        argv += ["--evidence-contract", value]
    for value in task.get("checks", []):
        argv += ["--check", value]
    return argv


# Windows PowerShell 5.1 (and 7.0-7.2) drop embedded double quotes when calling a native program unless
# they are backslash-escaped; 7.3+ passes them as written. Q escapes only where the running shell needs it.
POWERSHELL_PRELUDE = (
    "function Q([string]$s) { if ($null -eq $PSNativeCommandArgumentPassing -or $PSNativeCommandArgumentPassing -eq 'Legacy') "
    "{ $s -replace '(\\\\*)\"', '$1$1\\\"' } else { $s } }"
)


def quote(value, shell):
    if shell == "powershell":
        literal = "'" + value.replace("'", "''") + "'"
        return f"(Q {literal})" if '"' in value else literal
    return shlex.quote(value)


def add_task_command(task, shell="bash", project=".", run=None):
    cli = ".agentic-team/bin/agentic_team.py"
    return " ".join(["python", cli] + [quote(part, shell) for part in add_task_argv(task, project, run)])


def load_context(project, run=None):
    """Installed roles, current stage, and existing tasks of an installed project."""
    bus = Path(project) / ".agentic-team"
    manifest = json.loads((bus / "team.json").read_text(encoding="utf-8"))
    wanted = set(manifest.get("installation", {}).get("installed_agents", []))
    installed = {a["id"]: a.get("access") for a in manifest.get("agents", []) if not wanted or a["id"] in wanted}
    run_id = run
    if not run_id:
        current = (bus / "CURRENT.md").read_text(encoding="utf-8") if (bus / "CURRENT.md").exists() else ""
        match = re.search(r"Run: `([^`]+)`", current)
        run_id = match.group(1) if match else None
    state = {}
    if run_id and (bus / "runs" / run_id / "state.json").is_file():
        state = json.loads((bus / "runs" / run_id / "state.json").read_text(encoding="utf-8"))
    return {"installed": installed, "tasks": state.get("tasks", {}), "stage": state.get("stage"), "run": run_id}


def apply_tasks(tasks, project, run=None):
    """Add the tasks through the runtime itself (the single state writer)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import agentic_team  # noqa: E402

    project_path = Path(project)
    run_dir = agentic_team.find_run(project_path, run)
    for task in tasks:
        args = argparse.Namespace(
            id=task["id"], title=task["title"], objective=None, owner=task["owner"], stage=task.get("stage"),
            risk=task["risk"], depends_on=[], path=task.get("paths", []), exclusive=False,
            input=task.get("inputs", []), acceptance=task.get("acceptance", []),
            evidence_contract=task.get("evidence_contract", []), check=task.get("checks", []),
        )
        agentic_team.add_task(project_path, run_dir, args)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="findings-to-tasks", description=__doc__.splitlines()[0])
    parser.add_argument("findings", help="findings JSON file (array, either schema)")
    parser.add_argument("--output", help="write task packets JSON here (default: stdout only)")
    parser.add_argument("--commands", action="store_true", help="print runnable add-task command lines")
    parser.add_argument("--shell", choices=["bash", "powershell"], default="bash", help="quoting for --commands")
    parser.add_argument("--project", help="installed project: resolve owners and stage from its roster and run")
    parser.add_argument("--run", help="run id (default: CURRENT.md)")
    parser.add_argument("--stage", help="stage for remediation tasks (default: the run's current stage)")
    parser.add_argument("--check", action="append", default=[],
                        help="acceptance command every remediation task must pass, e.g. the project's test command "
                             "(repeatable; the runtime refuses build tasks without one)")
    parser.add_argument("--apply", action="store_true", help="add the tasks to the run (requires --project)")
    args = parser.parse_args(argv)

    try:
        raw = json.loads(Path(args.findings).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"cannot read findings: {exc}")

    try:
        findings = [normalize(item) for item in raw]
    except ValueError as exc:
        parser.error(str(exc))

    context = load_context(args.project, args.run) if args.project else {}
    stage = args.stage or context.get("stage")
    tasks = build_tasks(findings, context, stage, args.check)
    if tasks and not args.check:
        print("No --check given: the runtime refuses remediation tasks without an acceptance command "
              "(pass the project's test command).", file=sys.stderr)
        if args.apply:
            return 2
    result = {
        "total_findings": len(findings),
        "by_severity": {
            level: sum(1 for f in findings if f["severity"] == level)
            for level in ("blocker", "major", "minor", "nit")
        },
        "verdict": verdict(findings),
        "tasks": tasks,
    }
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Task packets written: {args.output}")
    else:
        print(text)
    unassigned = [task["id"] for task in tasks if task["owner"] == UNASSIGNED]
    if unassigned:
        print(f"No installed writable role for: {', '.join(unassigned)}; assign an owner before adding.", file=sys.stderr)
    if args.commands:
        print("\nRunnable add-task invocations (the runtime CLI is the state writer):")
        if args.shell == "powershell" and any('"' in part for task in tasks for part in add_task_argv(task)):
            print("  " + POWERSHELL_PRELUDE)
        for task in tasks:
            print("  " + add_task_command(task, args.shell, args.project or ".", context.get("run") or args.run))
    if args.apply:
        if not args.project:
            parser.error("--apply requires --project")
        if unassigned:
            print("Refusing to apply: unassigned tasks exist.", file=sys.stderr)
            return 2
        apply_tasks(tasks, args.project, context.get("run") or args.run)
        print(f"Added {len(tasks)} remediation task(s) to stage {stage}.")
    print(f"Review gate verdict: {result['verdict']}", file=sys.stderr)
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
