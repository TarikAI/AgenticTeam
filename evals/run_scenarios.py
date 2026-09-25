#!/usr/bin/env python3
"""Deterministic team-evaluation scenarios for AgenticTeam.

Each scenario in evals/scenarios/*.json installs the team into a scratch project and drives the
INSTALLED CLI step by step, asserting exit codes, output, files, and state. They exercise the
gates, artifacts, and authority refusals the way an orchestrating agent would hit them.

Usage:
    python evals/run_scenarios.py                 # run all, print a scorecard
    python evals/run_scenarios.py greenfield      # run scenarios whose name contains "greenfield"

Step forms (JSON objects):
    {"cli": [...], "exit": 0, "contains": "text"}     run the installed CLI (--project added)
    {"human": [...], "exit": 0}                      same, with --token-file for the owner token
    {"write": "RUN/BRIEF.md", "text": "..."}         write a file (RUN = run dir, PROJECT = project)
    {"state": {"stage": "04_build", "status": "active"}}   assert top-level state fields
    {"task": {"id": "T1", "status": "completed"}}    assert one task's fields
    {"exec_py": "print(1)", "task": "T1", "agent": "backend-engineer", "exit": 0}
                                                     run python through `exec` for a claimed task
Exit codes: 0 all scenarios pass, 1 otherwise.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = Path(__file__).resolve().parent / "scenarios"


class ScenarioFailure(AssertionError):
    pass


def expand(value: str, context: dict[str, str]) -> str:
    for key, replacement in context.items():
        value = value.replace(key, replacement)
    return value


def run_scenario(spec: dict) -> list[str]:
    home = tempfile.mkdtemp(prefix="eval-home-")
    project = Path(tempfile.mkdtemp(prefix="eval-project-"))
    env = dict(os.environ, AGENTIC_TEAM_HOME=home)
    log: list[str] = []
    try:
        install = [sys.executable, str(ROOT / "scripts" / "agentic_team.py"), "install", str(project),
                   "--harness", spec.get("harness", "generic"), "--preset", spec.get("preset", "full-company")]
        subprocess.run(install, check=True, capture_output=True, env=env)
        cli = [sys.executable, str(project / ".agentic-team" / "bin" / "agentic_team.py")]
        context = {"PROJECT": str(project)}

        def state() -> dict:
            current = (project / ".agentic-team" / "CURRENT.md").read_text(encoding="utf-8")
            run_id = current.split("Run: `", 1)[1].split("`", 1)[0]
            return json.loads((project / ".agentic-team" / "runs" / run_id / "state.json").read_text(encoding="utf-8"))

        def token_file() -> str:
            current = state()
            key = f"{current['run_id']}.{current['run_uid']}"
            return str(Path(home) / "owner-tokens" / f"{key}.token")

        for number, step in enumerate(spec["steps"], start=1):
            label = step.get("note") or next(iter(step))
            if "write" in step:
                target = Path(expand(step["write"], context))
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(step["text"], encoding="utf-8")
                log.append(f"{number:>2}. write {step['write']}")
                continue
            if "state" in step:
                current = state()
                for key, expected in step["state"].items():
                    if current.get(key) != expected:
                        raise ScenarioFailure(f"step {number} ({label}): state.{key} is {current.get(key)!r}, expected {expected!r}")
                log.append(f"{number:>2}. state {step['state']}")
                continue
            if "task" in step and "exec_py" not in step:
                current = state()["tasks"][step["task"]["id"]]
                for key, expected in step["task"].items():
                    if current.get(key) != expected:
                        raise ScenarioFailure(f"step {number} ({label}): task.{key} is {current.get(key)!r}, expected {expected!r}")
                log.append(f"{number:>2}. task {step['task']}")
                continue
            if "exec_py" in step:
                args = ["exec", "--task", step["task"], "--agent", step["agent"], "--", sys.executable, "-c", step["exec_py"]]
            else:
                args = [expand(part, context) for part in step.get("cli") or step.get("human")]
            args = args + ["--project", str(project)] if args[0] not in {"exec"} else args[:1] + ["--project", str(project)] + args[1:]
            if "human" in step:
                args += ["--token-file", token_file()]
            result = subprocess.run(cli + args, capture_output=True, text=True, env=env, stdin=subprocess.DEVNULL, timeout=60)
            expected = step.get("exit", 0)
            if result.returncode != expected:
                raise ScenarioFailure(
                    f"step {number} ({label}): `{' '.join(args[:3])}` exited {result.returncode}, expected {expected}\n"
                    f"stdout: {result.stdout.strip()[:400]}\nstderr: {result.stderr.strip()[:400]}"
                )
            if step.get("contains") and step["contains"] not in result.stdout + result.stderr:
                raise ScenarioFailure(f"step {number} ({label}): output lacks {step['contains']!r}: {result.stdout[:300]} {result.stderr[:300]}")
            if args[0] == "init-run":
                context["RUN"] = result.stdout.strip().splitlines()[-1]
            log.append(f"{number:>2}. {' '.join(args[:2])} -> {result.returncode}")
        return log
    finally:
        shutil.rmtree(project, ignore_errors=True)
        shutil.rmtree(home, ignore_errors=True)


def load_scenarios(selector: str | None = None) -> list[dict]:
    specs = []
    for path in sorted(SCENARIOS.glob("*.json")):
        spec = json.loads(path.read_text(encoding="utf-8"))
        spec.setdefault("name", path.stem)
        if not selector or selector in spec["name"]:
            specs.append(spec)
    return specs


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    specs = load_scenarios(argv[0] if argv else None)
    failures = 0
    for spec in specs:
        try:
            steps = run_scenario(spec)
            print(f"PASS {spec['name']} ({len(steps)} steps)")
        except (ScenarioFailure, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            failures += 1
            print(f"FAIL {spec['name']}: {exc}")
    print(f"\n{len(specs) - failures}/{len(specs)} scenarios passed")
    return 0 if failures == 0 and specs else 1


if __name__ == "__main__":
    raise SystemExit(main())
