"""P6: roster lint — every role file obeys the v3 rules (plan Appendix B)."""

from __future__ import annotations

import re
import unittest

from helpers import ROOT, team


class RosterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = team.load_json(ROOT / "team.json")

    def test_roster_lint_is_clean(self) -> None:
        self.assertEqual(team.roster_problems(ROOT, self.manifest), [])

    def test_lint_catches_what_it_claims_to(self) -> None:
        """The lint must not be vacuous: feed it a bad role and expect each rule to fire."""
        import tempfile
        from pathlib import Path
        import shutil

        scratch = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(ROOT / "agents", scratch / "agents")
            shutil.copytree(ROOT / "protocols", scratch / "protocols")
            shutil.copytree(ROOT / "runtime", scratch / "runtime")
            bad = scratch / "agents" / "specialists" / "sre-engineer.md"
            bad.write_text(
                "---\nname: sre-engineer\ndescription: Does reliability.\n---\n\n# SRE\n\n"
                "Write lessons.md during hardening. Ask `imaginary-engineer`.\n\n**Owns:** PRD.md\n\n## Standing orders\n\nx\n",
                encoding="utf-8",
            )
            problems = "\n".join(team.roster_problems(scratch, self.manifest))
            for expected in ("trigger clause", "exclusion clause", "lessons.md", "hardening", "standing orders",
                             "specialist sections", "unknown role id `imaginary-engineer`", "PRD.md must have exactly one owner"):
                self.assertIn(expected, problems)
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    def test_every_lifecycle_artifact_has_exactly_one_owner(self) -> None:
        owners: dict[str, list[str]] = {}
        for agent in self.manifest["agents"]:
            body = (ROOT / agent["file"]).read_text(encoding="utf-8")
            for line in re.findall(r"\*\*Owns:\*\*([^\n]+)", body):
                for name in re.findall(r"(?<!_marketing/)\b[A-Z][A-Z-]+\.md", line):
                    owners.setdefault(name, []).append(agent["id"])
        expected = {
            "BRIEF.md": ["ceo"], "ASSUMPTIONS.md": ["ceo"], "DELIVERY-REPORT.md": ["ceo"], "PRD.md": ["product-manager"],
            "ARCHITECTURE.md": ["cto-architect"], "DESIGN.md": ["ux-ui-designer"], "READINESS.md": ["delivery-lead"],
            "RETROSPECTIVE.md": ["delivery-lead"], "VERIFICATION.md": ["qa-lead"], "RELEASE.md": ["release-manager"],
            "MARKETING.md": ["cmo"],
        }
        for name, roles in expected.items():
            self.assertEqual(owners.get(name), roles, name)

    def test_access_wording_matches_access_class(self) -> None:
        for agent in self.manifest["agents"]:
            body = (ROOT / agent["file"]).read_text(encoding="utf-8")
            if agent["access"] in {"read-only", "research"}:
                self.assertNotRegex(body, r"\*\*Owns:\*\*", f"{agent['id']} cannot own files it may not write")

    def test_orchestrators_say_so(self) -> None:
        ceo = team.parse_frontmatter((ROOT / "agents" / "leadership" / "ceo.md").read_text(encoding="utf-8"))[0]
        self.assertIn("Main-session orchestrator", ceo["description"])


if __name__ == "__main__":
    unittest.main()
