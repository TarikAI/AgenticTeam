"""Shared test scaffolding.

Importing this module isolates every test from the developer's real home directory: owner
tokens, ledgers, and other owner-held material go to a throwaway AGENTIC_TEAM_HOME, and the
same variable is inherited by every CLI subprocess the tests start.
"""

from __future__ import annotations

import atexit
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest import mock

_HOME = tempfile.mkdtemp(prefix="agentic-home-")
os.environ["AGENTIC_TEAM_HOME"] = _HOME
atexit.register(shutil.rmtree, _HOME, True)

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = Path(__file__).resolve().parent / "golden"

_SPEC = importlib.util.spec_from_file_location("agentic_team", ROOT / "scripts" / "agentic_team.py")
assert _SPEC and _SPEC.loader
team = importlib.util.module_from_spec(_SPEC)
sys.modules["agentic_team"] = team
_SPEC.loader.exec_module(team)

TEST_HOME = Path(_HOME)


LOCAL_POLICY = {"budgets": {"usd": 50}}


def fresh_project(preset: str = "full-company", harness: str = "generic", only: list[str] | None = None) -> Path:
    """Install AgenticTeam into a new temporary directory and return the project root.

    The project sets a spend ceiling the way a real one would (policies.local.json), because
    autonomous and supervised runs refuse to start without one.
    """
    target = Path(tempfile.mkdtemp(prefix="agentic-project-"))
    atexit.register(shutil.rmtree, str(target), True)
    team.install_team(ROOT, target, harness, preset, [], only or [])
    (target / ".agentic-team" / "config" / "policies.local.json").write_text(json.dumps(LOCAL_POLICY), encoding="utf-8")
    return target


def run_cli(project: Path, *args: str, stdin: str | None = None) -> tuple[int, str, str]:
    """Run the INSTALLED CLI of a project as a subprocess; return (exit code, stdout, stderr)."""
    cli = project / ".agentic-team" / "bin" / "agentic_team.py"
    completed = subprocess.run(
        [sys.executable, str(cli), *args],
        capture_output=True,
        text=True,
        input=stdin,
        env=dict(os.environ),
    )
    return completed.returncode, completed.stdout, completed.stderr


GOLDEN_ROSTER = ["ceo", "fullstack-engineer", "qa-lead", "research-agent", "sre-engineer"]


def compile_snapshot(harness: str) -> dict[str, str]:
    """Compile the fixed golden roster for one harness; return {relative path: content}."""
    target = Path(tempfile.mkdtemp(prefix="agentic-golden-"))
    try:
        # hook_python() probes the host (python on Windows, python3 on POSIX); pin it so the golden is portable.
        with mock.patch.object(team, "hook_python", return_value="python"):
            record = team.install_team(ROOT, target, harness, "full-company", [], GOLDEN_ROSTER)
        snapshot: dict[str, str] = {}
        for relative in record["generated_files"]:
            path = target / relative
            if path.is_file():
                snapshot[relative.replace("\\", "/")] = path.read_text(encoding="utf-8")
        return snapshot
    finally:
        shutil.rmtree(target, ignore_errors=True)
