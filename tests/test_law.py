"""P7: shared law stays consistent with policy and the runtime (drift tests), plus the learning loop."""

from __future__ import annotations

import re
import unittest

from helpers import ROOT, fresh_project, team

BANNED = ("task board", "task evidence record", "hardening", "status.md", "qa.md", "plan.md", "decisions.md", "wcag 2.1", "phase gate", "level 2", "level 3")
GATE_KEYWORDS = ("production deployment", "publishing", "spending", "credential", "irreversible", "broad system access", "legal")


def law_files():
    for folder in ("protocols", "skills", "knowledge", "runtime/templates"):
        for path in sorted((ROOT / folder).rglob("*.md")):
            if path.name != "CHANGELOG.md":  # append-only history keeps the words it used then
                yield path


class DriftTests(unittest.TestCase):
    def test_no_retired_vocabulary_in_shared_law(self) -> None:
        problems = []
        for path in law_files():
            text = path.read_text(encoding="utf-8").lower()
            for term in BANNED:
                if term == "decisions.md" and path.name == "decisions.md":
                    text = text.replace("knowledge/decisions.md", "").replace("`decisions.md`", "")
                if term in text:
                    problems.append(f"{path.relative_to(ROOT).as_posix()}: '{term}'")
        self.assertEqual(problems, [], "\n".join(problems))

    def test_hard_gate_lists_match_policy(self) -> None:
        policy = team.load_json(ROOT / "config" / "policies.json")
        self.assertEqual(len(policy["absolute_human_gates"]), 7)
        for relative in ("protocols/guardrails.md", "protocols/agent-contract.md", "runtime/templates/router.md"):
            text = (ROOT / relative).read_text(encoding="utf-8").lower()
            for keyword in GATE_KEYWORDS:
                self.assertIn(keyword, text, f"{relative} omits the '{keyword}' gate")

    def test_every_template_is_used_and_every_used_template_exists(self) -> None:
        code = (ROOT / "scripts" / "agentic_team.py").read_text(encoding="utf-8")
        corpus = code + "".join(path.read_text(encoding="utf-8") for path in law_files() if "templates" not in path.parts)
        for template in (ROOT / "runtime" / "templates").glob("*.md"):
            self.assertIn(template.name, corpus, f"template {template.name} is never referenced")
        for name in set(re.findall(r'templates" / "([a-z-]+\.md)"', code)) | set(team.ARTIFACT_TEMPLATES.values()):
            self.assertTrue((ROOT / "runtime" / "templates" / name).is_file(), name)

    def test_protocol_references_resolve(self) -> None:
        problems = []
        for path in list(law_files()) + sorted((ROOT / "docs").glob("*.md")):
            if path.name.startswith("v3-"):
                continue
            for name in re.findall(r"protocols/([a-z0-9-]+\.md)", path.read_text(encoding="utf-8")):
                if not (ROOT / "protocols" / name).is_file():
                    problems.append(f"{path.relative_to(ROOT).as_posix()} -> protocols/{name}")
        self.assertEqual(problems, [], "\n".join(problems))

    def test_skills_follow_the_agent_skills_spec(self) -> None:
        for skill in sorted((ROOT / "skills").iterdir()):
            fields, body = team.parse_frontmatter((skill / "SKILL.md").read_text(encoding="utf-8"))
            self.assertEqual(fields.get("name"), skill.name)
            self.assertRegex(fields["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
            self.assertLessEqual(len(fields.get("description", "")), 1024)
            self.assertTrue(fields.get("compatibility"), f"{skill.name} needs compatibility:")
            self.assertLessEqual(len(fields["compatibility"]), 500)
            self.assertIn(".agentic-team/bin/agentic_team.py", body, f"{skill.name} must be a runbook with exact commands")


class LearningLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = fresh_project()
        self.run = team.init_run(self.project, "Learn", "learn", "autonomous", "execute-only", "adaptive")

    def token(self) -> str:
        return team.owner_token_file(team.load_state(self.run)).read_text(encoding="utf-8").strip()

    def test_learn_writes_a_filterable_candidate(self) -> None:
        team.learn(self.project, self.run, "Freeze API schema first", "contract drift broke T3", "Publish the schema before parallel work",
                   "parallel API work", "single-file prototype", ["backend-lead", "frontend-lead"], "two teams share an API", "high")
        index = (self.project / ".agentic-team" / "knowledge" / "lessons.md").read_text(encoding="utf-8")
        self.assertIn("[roles: backend-lead, frontend-lead] Freeze API schema first", index)
        self.assertIn("- status: candidate · confidence: high · source: learn", index)
        with self.assertRaises(team.TeamError):
            team.learn(self.project, self.run, "x", "y", "z", "s", "c", ["not-a-role"])

    def test_only_the_human_promotes_a_playbook_check(self) -> None:
        playbook = self.project / ".agentic-team" / "knowledge" / "playbooks" / "backend-engineer.md"
        playbook.write_text("# Playbook\n\n- [ ] Log the SQL of list endpoints  <!-- status: candidate · learned: 2026-09-25 -->\n", encoding="utf-8")
        with self.assertRaises(team.TeamError):
            team.promote_check(self.project, self.run, "backend-engineer", "Log the SQL", "backend-engineer", self.token())
        team.promote_check(self.project, self.run, "backend-engineer", "Log the SQL", "Owner", self.token())
        self.assertIn("status: proven", playbook.read_text(encoding="utf-8"))
        self.assertEqual(team.audit_verify(self.project, self.run, self.token()), [])


if __name__ == "__main__":
    unittest.main()
