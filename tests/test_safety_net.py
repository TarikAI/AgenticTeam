"""P0 safety net: home isolation, golden compile snapshots, doc <-> CLI consistency."""

from __future__ import annotations

import os
from pathlib import Path
import re
import unittest

from helpers import GOLDEN, ROOT, TEST_HOME, compile_snapshot, team

HARNESSES = ["claude-code", "codex", "opencode", "antigravity", "gemini-cli", "pi", "generic"]


class HomeIsolationTests(unittest.TestCase):
    def test_owner_material_never_touches_the_real_home(self) -> None:
        token_path = team.owner_token_path("any-run.abc")
        self.assertEqual(os.environ["AGENTIC_TEAM_HOME"], str(TEST_HOME))
        self.assertTrue(str(token_path).startswith(str(TEST_HOME)), token_path)
        self.assertNotEqual(TEST_HOME.resolve(), (Path.home() / ".agentic-team").resolve())


class GoldenSnapshotTests(unittest.TestCase):
    """Byte-for-byte snapshots of what each emitter writes for a fixed five-role roster.

    Regenerate after an intended change with UPDATE_GOLDEN=1 and review the diff.
    """

    def test_compiled_output_matches_golden(self) -> None:
        update = os.environ.get("UPDATE_GOLDEN") == "1"
        for harness in HARNESSES:
            with self.subTest(harness=harness):
                snapshot = compile_snapshot(harness)
                root = GOLDEN / harness
                if update:
                    if root.exists():
                        for stale in sorted(root.rglob("*"), reverse=True):
                            stale.unlink() if stale.is_file() else stale.rmdir()
                    for relative, content in snapshot.items():
                        path = root / relative
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(content, encoding="utf-8", newline="\n")
                    continue
                expected = {
                    path.relative_to(root).as_posix(): path.read_text(encoding="utf-8")
                    for path in root.rglob("*")
                    if path.is_file()
                }
                self.assertEqual(sorted(snapshot), sorted(expected), f"{harness}: file set changed")
                for relative, content in snapshot.items():
                    self.assertEqual(content, expected[relative], f"{harness}: {relative} changed")


COMMAND = re.compile(r"agentic_team\.py(?: --source \S+)? ([a-z][a-z-]*)(?: ([a-z][a-z-]*))?([^\n`]*)")
FLAG = re.compile(r"(?<![\w-])(--[a-z][a-z-]*)")


def parser_surface() -> tuple[dict[str, set[str]], set[str]]:
    parser = team.build_parser()
    global_flags = {option for action in parser._actions for option in action.option_strings}
    commands: dict[str, set[str]] = {}
    for action in parser._actions:
        if getattr(action, "choices", None) and isinstance(action.choices, dict):
            for name, sub in action.choices.items():
                flags = {option for sub_action in sub._actions for option in sub_action.option_strings}
                for sub_sub in sub._actions:
                    if getattr(sub_sub, "choices", None) and isinstance(sub_sub.choices, dict):
                        for nested_name, nested in sub_sub.choices.items():
                            commands[f"{name} {nested_name}"] = {
                                option for nested_action in nested._actions for option in nested_action.option_strings
                            }
                commands[name] = flags
    return commands, global_flags


def documented_invocations() -> list[tuple[str, int, str, str]]:
    sources = [ROOT / "README.md"]
    for folder in ("docs", "skills", "protocols", "agents", "runtime/templates"):
        sources.extend(sorted((ROOT / folder).rglob("*.md")))
    found = []
    for source in sources:
        if source.name.startswith("v3-"):
            continue  # the upgrade plan describes future commands on purpose
        for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
            for match in COMMAND.finditer(line):
                found.append((source.relative_to(ROOT).as_posix(), number, match.group(1), line))
    return found


class DocCliConsistencyTests(unittest.TestCase):
    """Every documented `agentic_team.py <command> --flag` must exist in build_parser()."""

    def test_documented_commands_and_flags_exist(self) -> None:
        commands, global_flags = parser_surface()
        problems = []
        for source, number, command, line in documented_invocations():
            tail = line.split("agentic_team.py", 1)[1].split(" -- ", 1)[0]  # flags after -- belong to the wrapped command
            words = tail.split()
            name = command
            if len(words) > 1 and f"{words[0]} {words[1]}" in commands:
                name = f"{words[0]} {words[1]}"
            if name in team.HELPER_COMMANDS:
                continue  # helper commands own and validate their flags
            if name not in commands:
                problems.append(f"{source}:{number}: unknown command '{command}'")
                continue
            allowed = commands[name] | global_flags
            for flag in FLAG.findall(tail):
                if flag not in allowed:
                    problems.append(f"{source}:{number}: '{name}' has no flag {flag}")
        self.assertEqual(problems, [], "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
