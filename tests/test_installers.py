"""The installers run end to end.

A syntax check never caught the Windows interpreter bug in install.sh, and nothing executed install.ps1
at all. These tests run each installer for real into a temporary project and check the result.
"""

import helpers  # noqa: F401  (isolates AGENTIC_TEAM_HOME before anything touches the CLI)
import subprocess
import tempfile
import unittest
from pathlib import Path

from helpers import ROOT
from test_repairs_packets import shells  # Git Bash on Windows (never the WSL launcher), and PowerShell

SHELLS = shells()


class InstallerTests(unittest.TestCase):
    def assert_installed(self, target: Path, result: subprocess.CompletedProcess) -> None:
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((target / ".agentic-team" / "team.json").is_file(), "no coordination bus")
        self.assertTrue((target / ".agentic-team" / "bin" / "agentic_team.py").is_file(), "no installed CLI")
        self.assertTrue((target / "AGENTS.md").is_file(), "no root router")

    @unittest.skipUnless("bash" in SHELLS, "no usable bash here (on Windows that means Git Bash)")
    def test_install_sh_installs_a_project(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "my project"
            result = subprocess.run(
                [SHELLS["bash"], "scripts/install.sh", "--target", str(target),
                 "--harness", "generic", "--preset", "platform-core"],
                cwd=ROOT, capture_output=True, text=True, timeout=300,
            )
            self.assert_installed(target, result)

    @unittest.skipUnless("bash" in SHELLS, "no usable bash here (on Windows that means Git Bash)")
    def test_install_sh_installs_every_harness(self) -> None:
        # Mirrors CI's install loop; the harness list comes from the manifest, never a hard-coded count.
        harnesses = sorted(helpers.team.load_json(ROOT / "team.json")["harnesses"])
        for harness in harnesses:
            with self.subTest(harness=harness), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary) / "proj"
                result = subprocess.run(
                    [SHELLS["bash"], "scripts/install.sh", "--target", str(target),
                     "--harness", harness, "--preset", "platform-core"],
                    cwd=ROOT, capture_output=True, text=True, timeout=300,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue((target / ".agentic-team" / "team.json").is_file(), f"no bus for {harness}")

    def test_install_sh_has_lf_line_endings(self) -> None:
        # bash, including the Windows WSL launcher, rejects a CRLF script outright.
        self.assertNotIn(b"\r\n", (ROOT / "scripts" / "install.sh").read_bytes())

    @unittest.skipUnless("powershell" in SHELLS, "no PowerShell here")
    def test_install_ps1_installs_a_project(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "my project"
            result = subprocess.run(
                [SHELLS["powershell"], "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/install.ps1",
                 "-Target", str(target), "-Harness", "generic", "-Preset", "platform-core"],
                cwd=ROOT, capture_output=True, text=True, timeout=300,
            )
            self.assert_installed(target, result)


if __name__ == "__main__":
    unittest.main()
