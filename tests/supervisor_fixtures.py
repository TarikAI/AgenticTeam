"""Shared fixtures for the supervisor tests: an installed git project, a fast configuration, the fake worker."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

from helpers import ROOT, fresh_project, team

_SPEC = importlib.util.spec_from_file_location("agentic_supervisor", ROOT / "scripts" / "agentic_supervisor.py")
assert _SPEC and _SPEC.loader
sup = importlib.util.module_from_spec(_SPEC)
sys.modules["agentic_supervisor"] = sup
_SPEC.loader.exec_module(sup)

FAKE_WORKER = ROOT / "tests" / "fake_worker.py"
GITIGNORE = ".agentic-team/runs/\n.agentic-team/CURRENT.md\n.agentic-team/supervisor/\n.fake-worker-mode\n__pycache__/\n"


def git(project: Path, *args: str) -> str:
    result = subprocess.run(["git", "-c", "user.email=owner@example.com", "-c", "user.name=Owner", *args], cwd=project,
                            capture_output=True, text=True, check=True)
    return result.stdout.strip()


def git_project(preset: str = "full-company") -> Path:
    project = fresh_project(preset)
    (project / ".gitignore").write_text(GITIGNORE, encoding="utf-8")
    git(project, "init", "-q")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "Install AgenticTeam")
    return project


def fast_config(**overrides) -> dict:
    config = dict(
        adapter="command", command=[sys.executable, str(FAKE_WORKER), "--project", "{project}", "--run", "{run}"],
        run_budget={"usd": 5.0, "tokens": None}, attempt_usd=1.0, heartbeat_seconds=0.2, start_grace_seconds=4.0,
        backoff_seconds=0.05, backoff_max_seconds=0.2, poll_seconds=0.1, timeout_seconds=90.0, owner_name="Owner",
    )
    config.update(overrides)
    return config


class SupervisorBase(unittest.TestCase):
    autonomy = "unattended"

    def setUp(self) -> None:
        self.project = git_project()
        self.sup = sup.Supervisor(self.project)
        self.sup.configure(**fast_config(autonomy=self.autonomy))
        self.sup.add_allowance(20.0, "tests")
        self.addCleanup(self.stop_workers)

    def mode(self, text: str) -> None:
        (self.project / ".fake-worker-mode").write_text(text + "\n", encoding="utf-8")

    def enqueue(self, event_id: str = "fix-1", **fields) -> str:
        event = {"id": event_id, "kind": "manual", "title": f"Fix {event_id}", "brief": "Make feature() return 42.",
                 "acceptance": ["AC-1: feature() returns 42"]}
        event.update(fields)
        return self.sup.enqueue(event)[1]

    def until_idle(self, seconds: float = 120.0) -> int:
        return self.sup.serve("until-idle", max_seconds=seconds)

    def job(self, job_id: str = "fix-1") -> dict:
        return self.sup.store.job(job_id)

    def run_state(self, job_id: str = "fix-1") -> dict:
        return team.load_state(self.project / ".agentic-team" / "runs" / self.job(job_id)["run_id"])

    def token(self, job_id: str = "fix-1") -> str:
        return team.owner_token_file(self.run_state(job_id)).read_text(encoding="utf-8").strip()

    def run_dir(self, job_id: str = "fix-1") -> Path:
        return self.project / ".agentic-team" / "runs" / self.job(job_id)["run_id"]

    def attempt_dir(self, job_id: str = "fix-1", index: int = -1) -> Path:
        job = self.job(job_id)
        return self.sup.store.attempt_dir(job_id, job["attempts"][index]["id"])

    def transcript_lines(self, job_id: str = "fix-1", index: int = -1) -> list[dict]:
        lines = []
        for line in (self.attempt_dir(job_id, index) / "stdout.jsonl").read_text(encoding="utf-8").splitlines():
            try:
                lines.append(json.loads(line))
            except ValueError:
                continue
        return lines

    def reap(self) -> None:
        """Collect wrappers this process started, so an exited one is not a zombie that still looks alive (POSIX)."""
        for process in list(self.sup._spawned.values()):
            process.poll()

    def gone(self, pid: int) -> bool:
        self.reap()
        return not sup.process_alive(pid)

    def wait_for(self, predicate, seconds: float = 30.0, step: float = 0.1) -> bool:
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            try:
                if predicate():
                    return True
            except (PermissionError, team.TeamError) as exc:
                # Windows refuses a read while the worker's CLI replaces the file; poll again.
                if not isinstance(exc, PermissionError) and not isinstance(exc.__cause__, PermissionError):
                    raise
            time.sleep(step)
        return False

    def stop_workers(self) -> None:
        """Ask every wrapper still running to end its worker, and wait for the receipts."""
        root = self.sup.store.attempts
        if not root.is_dir():
            return
        pending = [folder for folder in root.glob("*/*") if (folder / "claim").exists() and not (folder / "exit.json").exists()]
        for folder in pending:
            with open(folder / "cancel", "a", encoding="utf-8"):
                pass
        deadline = time.monotonic() + 20
        while pending and time.monotonic() < deadline:
            pending = [folder for folder in pending if not (folder / "exit.json").exists() and (folder / "start.json").exists()]
            time.sleep(0.1)


def scratch(prefix: str) -> Path:
    path = Path(tempfile.mkdtemp(prefix=prefix))
    import atexit

    atexit.register(shutil.rmtree, str(path), True)
    return path


def environment_without(*names: str) -> dict:
    return {key: value for key, value in os.environ.items() if key not in names}
