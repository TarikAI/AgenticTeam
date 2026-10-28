#!/usr/bin/env python3
"""A scripted worker for the supervisor tests. It is never shipped and never used in production.

It drives the INSTALLED CLI exactly as an agent would (add-task with a check, claim, commit,
complete, advance, an independent verdict, the release packet and rollback rehearsal, the
delivery report), reading only what an agent may read. It never writes runtime state, except in
the deliberate `forge` mode a tamper test uses. It prints one harness-style `result` line so the
supervisor has something to meter, and one `fake-env` line saying what it could see.

The mode comes from `<project>/.fake-worker-mode` (one word, then optional key=value options):
success, crash-once, missing-usage, malformed, hang, slow, claim-and-hang, repeated-failure, r2, r3,
stop-after-build, verdict-fail, commit-after-verify, dirty-after-verify, no-rollback, no-report,
forge, forge-complete, self-approve. Options: cost=<usd> (default 0.01), sleep=<seconds> (slow mode).
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

PASS = f'"{sys.executable}" -c "pass"'
FAIL = f'"{sys.executable}" -c "import sys; sys.exit(3)"'


def emit(item: dict) -> None:
    print(json.dumps(item), flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--run", required=True)
    args = parser.parse_args(argv)
    project = Path(args.project)
    run = args.run
    run_dir = project / ".agentic-team" / "runs" / run
    cli = [sys.executable, str(project / ".agentic-team" / "bin" / "agentic_team.py")]
    words = (project / ".fake-worker-mode").read_text(encoding="utf-8").split() if (project / ".fake-worker-mode").is_file() else ["success"]
    mode = words[0]
    options = dict(word.split("=", 1) for word in words[1:] if "=" in word)
    cost = float(options.get("cost", "0.01"))
    flags = run_dir / "_context"
    flags.mkdir(parents=True, exist_ok=True)
    home = os.environ.get("AGENTIC_TEAM_HOME", "")
    emit({"type": "system", "subtype": "fake-env", "home": home, "view": os.environ.get("AGENTIC_TEAM_VIEW"),
          "home_has_tokens": bool(home) and any(Path(home).rglob("*.token")), "worker": os.environ.get("AGENTIC_TEAM_WORKER"),
          "gh_token_visible": "GH_TOKEN" in os.environ})
    module = run.replace("-", "_")

    def finish(code: int = 0) -> int:
        if mode == "missing-usage":
            emit({"type": "assistant", "message": {"content": "no result line follows"}})
        elif mode == "malformed":
            print('{"type": "result", "total_cost_usd": ', flush=True)
        else:
            emit({"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": cost,
                  "usage": {"input_tokens": 100, "output_tokens": 20}, "modelUsage": {"fake-model": {"inputTokens": 1000, "outputTokens": 200, "costUSD": cost}}})
        return code

    def call(*parts: str) -> subprocess.CompletedProcess:
        result = subprocess.run([*cli, *parts, "--project", str(project), "--run", run], capture_output=True, text=True, stdin=subprocess.DEVNULL)
        emit({"type": "fake-cli", "args": list(parts[:3]), "exit": result.returncode, "out": (result.stdout + result.stderr)[-300:]})
        return result

    def git(*parts: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-c", "user.email=worker@example.com", "-c", "user.name=Worker", *parts], cwd=project, capture_output=True, text=True)

    def head() -> str:
        result = git("rev-parse", "HEAD")
        return result.stdout.strip() if result.returncode == 0 else "none"

    def state() -> dict:
        return json.loads((run_dir / "state.json").read_text(encoding="utf-8"))

    if mode == "forge-complete":
        forged = state()
        forged.update(status="complete", stage="07_learn")
        (run_dir / "state.json").write_text(json.dumps(forged, indent=2), encoding="utf-8")  # no work, no verdict, no report
        return finish(0)
    if mode == "hang":
        emit({"type": "assistant", "message": {"content": "thinking forever"}})
        time.sleep(600)
    if mode == "slow":
        time.sleep(float(options.get("sleep", "30")))

    for _ in range(80):
        current = state()
        if current["status"] == "complete" or current["status"] == "waiting-human" or str(current["status"]).startswith("blocked"):
            break
        tasks = current["tasks"]
        stage = current["stage"]
        if stage == "04_build":
            if "T1" not in tasks:
                (project / "src").mkdir(exist_ok=True)
                (project / "tests").mkdir(exist_ok=True)
                (project / "src" / f"feature_{module}.py").write_text("def feature():\n    return 42\n", encoding="utf-8")
                (project / "tests" / f"test_feature_{module}.py").write_text(
                    "import sys\nimport unittest\nsys.path.insert(0, 'src')\n"
                    f"from feature_{module} import feature\n\n\nclass FeatureTests(unittest.TestCase):\n"
                    "    def test_feature(self):\n        self.assertEqual(feature(), 42)\n", encoding="utf-8")
                check = FAIL if mode == "repeated-failure" else f'"{sys.executable}" -m unittest discover -s tests -p "test_feature_{module}.py"'
                call("add-task", "--id", "T1", "--title", "Implement the feature", "--owner", "backend-engineer", "--path", "src", "--path", "tests",
                     "--check", check)
                continue
            task = tasks["T1"]
            if task["status"] == "ready":
                call("claim", "--task", "T1", "--agent", "backend-engineer")
                if mode == "claim-and-hang":
                    emit({"type": "assistant", "message": {"content": "holding T1"}})
                    time.sleep(600)
                if mode == "crash-once" and not (flags / "fake-crashed.flag").exists():
                    (flags / "fake-crashed.flag").write_text("crashed\n", encoding="utf-8")
                    return finish(3)
                continue
            if task["status"] == "claimed":
                if git("status", "--porcelain", "src", "tests").stdout.strip():
                    git("add", "src", "tests")
                    git("commit", "-q", "-m", f"Feature for {run}")
                result = call("complete", "--task", "T1", "--agent", "backend-engineer", "--evidence", f"file:src/feature_{module}.py")
                if result.returncode != 0:
                    call("fail", "--task", "T1", "--agent", "backend-engineer", "--reason", "acceptance check failed with exit 3")
                continue
            if task["status"] == "failed":
                return finish(1)
            if mode == "r2" and "MIG" not in tasks:
                call("add-task", "--id", "MIG", "--title", "Migrate the local database", "--owner", "database-engineer", "--action", "migrate",
                     "--target", "local", "--path", "db", "--check", PASS)
                continue
            if "MIG" in tasks and tasks["MIG"]["status"] == "ready":
                call("claim", "--task", "MIG", "--agent", "database-engineer")
                continue
            if "MIG" in tasks and tasks["MIG"]["status"] == "claimed":
                call("complete", "--task", "MIG", "--agent", "database-engineer", "--evidence", "note:migrated a local copy")
                continue
            if mode == "r3" and "SHIP" not in tasks:
                call("add-task", "--id", "SHIP", "--title", "Deploy to production", "--owner", "devops-engineer", "--action", "deploy",
                     "--target", "production", "--path", "deploy", "--check", PASS)
                call("claim", "--task", "SHIP", "--agent", "devops-engineer")  # refused: R3 waits for the human
                return finish(0)
            if mode == "stop-after-build":
                return finish(0)
            result = call("advance")
            if result.returncode != 0 or "waiting-human" in result.stdout:
                return finish(0)
        elif stage == "05_verify":
            verdict = "FAIL" if mode == "verdict-fail" else "PASS"
            (run_dir / "VERIFICATION.md").write_text(
                f"Verdict: {verdict}\nVerifier: qa-lead\nVerified-SHA: {head()}\n\n# Verification\n\n| AC-1 | feature returns 42 | {verdict.lower()} | unittest |\n",
                encoding="utf-8")
            result = call("advance")
            if result.returncode != 0:
                return finish(0)
        elif stage == "06_release":
            if mode == "commit-after-verify" and not (flags / "fake-late.flag").exists():
                (flags / "fake-late.flag").write_text("late\n", encoding="utf-8")
                (project / "src" / f"late_{module}.py").write_text("LATE = True\n", encoding="utf-8")
                git("add", "src")
                git("commit", "-q", "-m", "A change after verification")
            (run_dir / "RELEASE.md").write_text(
                "# Release\n\nArtifact: HEAD as verified. Rollout: local only. Data changes: none.\n"
                "Monitoring and rollback: rehearsed by task RB. Supply chain: no new dependencies.\n", encoding="utf-8")
            if mode != "no-rollback" and "RB" not in tasks:
                call("add-task", "--id", "RB", "--title", "Rehearse the rollback", "--owner", "release-manager", "--action", "rollback-test",
                     "--check", PASS)
                continue
            if "RB" in tasks and tasks["RB"]["status"] == "ready":
                call("claim", "--task", "RB", "--agent", "release-manager")
                continue
            if "RB" in tasks and tasks["RB"]["status"] == "claimed":
                call("complete", "--task", "RB", "--agent", "release-manager", "--evidence", "note:rolled back and forward on a local copy")
                continue
            result = call("advance")
            if "waiting-human" in result.stdout:
                pending = [item for item in state()["checkpoints"] if item["status"] == "pending"]
                if mode == "self-approve" and pending:
                    call("approve", "--checkpoint", pending[0]["id"], "--by", "Owner", "--decision", "approving my own release")
                if mode == "forge" and pending:
                    forged = state()
                    for item in forged["checkpoints"]:
                        if item["id"] == pending[0]["id"]:
                            item.update(status="approved", approved_by="Owner")
                    forged["status"] = "active"
                    (run_dir / "state.json").write_text(json.dumps(forged, indent=2), encoding="utf-8")
                    call("advance")  # still refused: the gate reads the ledger through the view
                return finish(0)
            if result.returncode != 0:
                return finish(0)
        elif stage == "07_learn":
            if mode != "no-report":
                (run_dir / "DELIVERY-REPORT.md").write_text("# Delivery report\n\nOutcome: the feature returns 42; verified and released locally.\n",
                                                            encoding="utf-8")
            result = call("advance")
            if result.returncode != 0:
                return finish(0)
        else:
            call("advance")
    if mode == "dirty-after-verify":
        (project / "src" / f"stray_{module}.txt").write_text("not committed\n", encoding="utf-8")
    return finish(0)


if __name__ == "__main__":
    raise SystemExit(main())
