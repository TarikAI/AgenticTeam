#!/usr/bin/env python3
"""AgenticTeam v2: portable installer, compiler, and deterministic run-state manager."""

from __future__ import annotations

import argparse
import contextlib
import copy
import datetime as dt
import hashlib
import json
import os
import secrets
from pathlib import Path
import re
import shutil
import sys
import time
from typing import Any, Iterator


VERSION = "2.0.0"
MANAGED_START = "<!-- AGENTIC-TEAM:BEGIN -->"
MANAGED_END = "<!-- AGENTIC-TEAM:END -->"
STAGES = [
    ("00_intake", "Intake", "Normalize intent, constraints, authority, entry mode, and unknowns."),
    ("01_product", "Product definition", "Define user outcomes, journeys, scope, and measurable acceptance."),
    ("02_solution", "Solution design", "Define architecture, experience, contracts, and specialist controls."),
    ("03_readiness", "Implementation readiness", "Prove traceability, sequencing, ownership, and risk disposition."),
    ("04_build", "Build", "Execute bounded task packets and integrate working product increments."),
    ("05_verify", "Independent verification", "Verify the integrated product against requirements and risks."),
    ("06_release", "Release readiness", "Prepare approval, rollout, monitoring, rollback, and operational handoff."),
    ("07_learn", "Learning", "Capture evidence-backed lessons and evaluated improvement proposals."),
]
STAGE_NAMES = [item[0] for item in STAGES]
RISK_ORDER = {"R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4}


class TeamError(RuntimeError):
    """A user-correctable AgenticTeam error."""


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return result[:60] or "run"


def source_root(explicit: str | None = None) -> Path:
    if explicit:
        root = Path(explicit).expanduser().resolve()
    else:
        here = Path(__file__).resolve()
        candidates = [here.parent.parent, here.parent.parent.parent]
        root = next((candidate for candidate in candidates if (candidate / "team.json").is_file()), candidates[0])
    if not (root / "team.json").is_file():
        raise TeamError(f"AgenticTeam source not found at {root}")
    return root


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TeamError(f"Cannot read valid JSON from {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


@contextlib.contextmanager
def state_lock(run_dir: Path, timeout: float = 10.0) -> Iterator[None]:
    lock_path = run_dir / ".state.lock"
    deadline = time.monotonic() + timeout
    while True:
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(descriptor, f"pid={os.getpid()} time={utcnow()}\n".encode())
            os.close(descriptor)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                age = ""
                with contextlib.suppress(OSError):
                    held = time.time() - lock_path.stat().st_mtime
                    age = f" (held for {int(held)}s)"
                raise TeamError(
                    f"Run state is busy: {lock_path}{age}. If no other command is running, the "
                    "holder died; clear it with: agentic_team.py unlock --project <project>"
                )
            time.sleep(0.05)
    try:
        yield
    finally:
        with contextlib.suppress(FileNotFoundError):
            lock_path.unlink()


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"\'')
    return fields, text[end + 5 :].strip()


def compact_agent_body(text: str) -> tuple[dict[str, str], str]:
    fields, body = parse_frontmatter(text)
    body = body.split("\n## Standing orders", 1)[0].rstrip()
    body += (
        "\n\n## Shared operating contract\n"
        "Follow the installed project router and `.agentic-team/protocols/agent-contract.md`. "
        "Use the state CLI for claims and completion; obey the selected autonomy policy and hard human gates.\n"
    )
    return fields, body


def resolve_preset(manifest: dict[str, Any], preset: str) -> list[dict[str, Any]]:
    presets = manifest.get("presets", {})
    if preset not in presets:
        raise TeamError(f"Unknown preset '{preset}'. Choose: {', '.join(sorted(presets))}")
    spec = presets[preset]
    agents = manifest.get("agents", [])
    if spec.get("agents") == "all":
        return agents
    wanted = set(spec.get("agents", []))
    departments = set(spec.get("departments", []))
    selected = [agent for agent in agents if agent["id"] in wanted or agent["department"] in departments]
    missing = wanted - {agent["id"] for agent in selected}
    if missing:
        raise TeamError(f"Preset '{preset}' references missing agents: {', '.join(sorted(missing))}")
    return selected


def is_installed_bus(root: Path) -> bool:
    """True when we are running from a project's .agentic-team copy rather than the source repo."""
    return (root / "install-manifest.json").is_file() and not (root / "agents").is_dir()


def validate_source(root: Path) -> list[str]:
    errors: list[str] = []
    manifest = load_json(root / "team.json")
    if manifest.get("version") != VERSION:
        errors.append(f"team.json version must be {VERSION}")
    agents = manifest.get("agents")
    if not isinstance(agents, list) or not agents:
        errors.append("team.json must contain agents")
        agents = []
    seen: set[str] = set()
    known = {agent.get("id") for agent in agents}
    for agent in agents:
        agent_id = agent.get("id", "")
        if not agent_id or agent_id in seen:
            errors.append(f"duplicate or missing agent id: {agent_id!r}")
        seen.add(agent_id)
        for required in ("file", "department", "tier", "access", "reports_to", "capabilities"):
            if required not in agent:
                errors.append(f"{agent_id}: missing {required}")
        file_path = root / agent.get("file", "")
        if not file_path.is_file():
            errors.append(f"{agent_id}: missing file {file_path}")
        else:
            fields, _ = parse_frontmatter(file_path.read_text(encoding="utf-8"))
            if fields.get("name") != agent_id:
                errors.append(f"{agent_id}: frontmatter name is {fields.get('name')!r}")
            if not fields.get("description"):
                errors.append(f"{agent_id}: missing frontmatter description")
        manager = agent.get("reports_to")
        if manager not in known and manager != "human-owner":
            errors.append(f"{agent_id}: unknown reports_to {manager!r}")
    for preset in manifest.get("presets", {}):
        try:
            resolve_preset(manifest, preset)
        except TeamError as exc:
            errors.append(str(exc))
    for harness, spec in manifest.get("harnesses", {}).items():
        if not any(key in spec for key in ("agent_dir", "context_file")):
            errors.append(f"{harness}: no native destination")
    for workflow in manifest.get("workflows", {}).values():
        skill = root / workflow.get("skill", "") / "SKILL.md"
        if not skill.is_file():
            errors.append(f"missing workflow skill: {skill}")
        else:
            fields, body = parse_frontmatter(skill.read_text(encoding="utf-8"))
            if not fields.get("name") or not fields.get("description") or "TODO" in body:
                errors.append(f"invalid or unfinished skill: {skill}")
    required = [
        "config/policies.json",
        "protocols/agent-contract.md",
        "protocols/autonomy.md",
        "protocols/fusion.md",
        "protocols/progressive-context.md",
        "protocols/runtime.md",
        "runtime/templates/router.md",
        "schemas/team.schema.json",
        "schemas/run-state.schema.json",
    ]
    for relative in required:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")
    return errors


def yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


PROTOCOL_REF = re.compile(r"(?<![\w./-])protocols/([a-z0-9-]+\.md)")


def resolve_protocol_refs(text: str) -> str:
    """Rewrite bare `protocols/x.md` to the path it actually has in an installed project.

    Source files use the repo-relative form; installed projects keep protocols under
    `.agentic-team/`. Without this, every compiled agent points at a file that is not there.
    """
    return PROTOCOL_REF.sub(r".agentic-team/protocols/\1", text)


def agent_prompt(agent: dict[str, Any], root: Path) -> tuple[str, str]:
    fields, body = compact_agent_body((root / agent["file"]).read_text(encoding="utf-8"))
    description = fields.get("description", agent["id"])
    header = (
        f"Role ID: {agent['id']}\nDepartment: {agent['department']}\n"
        f"Reports to: {agent['reports_to']}\nAccess: {agent['access']}\n"
        f"Capabilities: {', '.join(agent['capabilities'])}\n\n"
    )
    if agent["access"] == "read-only":
        # Not every harness can express a tool allowlist, so the constraint also travels
        # in the prompt where it is understood everywhere.
        header += (
            "ACCESS CONSTRAINT: you are a read-only role. Do not create, edit, or delete "
            "project files, and do not run commands that mutate state. Report findings and "
            "hand changes to the owning role.\n\n"
        )
    return description, resolve_protocol_refs(header + body)


def managed_router() -> str:
    return (
        f"{MANAGED_START}\n"
        "# AgenticTeam\n\n"
        "Read `.agentic-team/AGENTS.md`, then `.agentic-team/CURRENT.md` and the active stage "
        "`CONTEXT.md`. Use `.agentic-team/bin/agentic_team.py` for durable task state. "
        "Role contracts live in this project (see `.agentic-team/install-manifest.json` for the "
        "compiled location); adopt the relevant role before acting. Installed skills describe the "
        "operating procedures. Do not bypass hard human gates or replace a human-supplied plan.\n"
        f"{MANAGED_END}"
    )


def upsert_managed_block(path: Path, block: str) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    pattern = re.compile(re.escape(MANAGED_START) + r".*?" + re.escape(MANAGED_END), re.DOTALL)
    if pattern.search(current):
        updated = pattern.sub(block, current)
    else:
        updated = current.rstrip() + ("\n\n" if current.strip() else "") + block
    write_text(path, updated)


def remove_managed_block(path: Path) -> None:
    if not path.is_file():
        return
    current = path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(MANAGED_START) + r".*?" + re.escape(MANAGED_END), re.DOTALL)
    updated = pattern.sub("", current).strip()
    if updated:
        write_text(path, updated)
    else:
        path.unlink()


def copy_managed_tree(source: Path, destination: Path) -> None:
    if source.exists():
        shutil.copytree(source, destination, dirs_exist_ok=True)


def emit_claude(target: Path, selected: list[dict[str, Any]], root: Path) -> list[str]:
    written: list[str] = []
    out = target / ".claude" / "agents"
    for agent in selected:
        description, prompt = agent_prompt(agent, root)
        tools = "Read, Grep, Glob" if agent["access"] == "read-only" else "Read, Write, Edit, Grep, Glob, Bash"
        content = (
            "---\n"
            f"name: {agent['id']}\n"
            f"description: {yaml_scalar(description)}\n"
            f"tools: {tools}\n"
            "model: inherit\n"
            "---\n\n" + prompt
        )
        path = out / f"{agent['id']}.md"
        write_text(path, content)
        written.append(str(path.relative_to(target)))
    upsert_managed_block(target / "CLAUDE.md", managed_router())
    return written + ["CLAUDE.md"]


def toml_literal(value: str) -> str:
    safe = value.replace('"""', '\\"\\"\\"')
    return f'"""{safe}"""'


def emit_codex(target: Path, selected: list[dict[str, Any]], root: Path) -> list[str]:
    written: list[str] = []
    out = target / ".codex" / "agents"
    for agent in selected:
        description, prompt = agent_prompt(agent, root)
        lines = [
            f"name = {json.dumps(agent['id'])}",
            f"description = {json.dumps(description)}",
            f"developer_instructions = {toml_literal(prompt)}",
        ]
        if agent["access"] == "read-only":
            lines.append('sandbox_mode = "read-only"')
        path = out / f"{agent['id']}.toml"
        write_text(path, "\n".join(lines))
        written.append(str(path.relative_to(target)))
    upsert_managed_block(target / "AGENTS.md", managed_router())
    return written + ["AGENTS.md"]


def emit_opencode(target: Path, selected: list[dict[str, Any]], root: Path) -> list[str]:
    written: list[str] = []
    out = target / ".opencode" / "agents"
    for agent in selected:
        description, prompt = agent_prompt(agent, root)
        edit_permission = "deny" if agent["access"] == "read-only" else "allow"
        mode = "primary" if agent["id"] in {"ceo", "cmo"} else "subagent"
        content = (
            "---\n"
            f"description: {yaml_scalar(description)}\n"
            f"mode: {mode}\n"
            "permission:\n"
            f"  edit: {edit_permission}\n"
            "  bash: ask\n"
            "---\n\n" + prompt
        )
        path = out / f"{agent['id']}.md"
        write_text(path, content)
        written.append(str(path.relative_to(target)))
    upsert_managed_block(target / "AGENTS.md", managed_router())
    return written + ["AGENTS.md"]


def emit_gemini(target: Path, selected: list[dict[str, Any]], root: Path) -> list[str]:
    written: list[str] = []
    out = target / ".gemini" / "agents"
    for agent in selected:
        description, prompt = agent_prompt(agent, root)
        content = f"---\nname: {agent['id']}\ndescription: {yaml_scalar(description)}\n---\n\n{prompt}"
        path = out / f"{agent['id']}.md"
        write_text(path, content)
        written.append(str(path.relative_to(target)))
    upsert_managed_block(target / "GEMINI.md", managed_router())
    return written + ["GEMINI.md"]


def emit_antigravity(target: Path, selected: list[dict[str, Any]], root: Path) -> list[str]:
    written: list[str] = []
    # Antigravity loads named agents from .agents/agents/<name>.md. The older .agents/roles/
    # layout is not a directory it scans, so contracts placed there were never loaded.
    agents_dir = target / ".agents" / "agents"
    for agent in selected:
        description, prompt = agent_prompt(agent, root)
        content = (
            "---\n"
            f"name: {agent['id']}\n"
            f"description: {yaml_scalar(description)}\n"
            "subagent: true\n"
            "mainAgent: true\n"
            "model: inherit\n"
            "---\n\n" + prompt
        )
        path = agents_dir / f"{agent['id']}.md"
        write_text(path, content)
        written.append(str(path.relative_to(target)))
    rule = (
        "---\n"
        "trigger: always_on\n"
        "---\n\n"
        "# AgenticTeam coordination\n\n"
        "Read `.agentic-team/AGENTS.md`, then `.agentic-team/CURRENT.md` and the active stage\n"
        "`CONTEXT.md`. Role contracts are installed as named agents in `.agents/agents/`; dispatch\n"
        "bounded work to them instead of performing every role yourself. Durable state changes go\n"
        "through `.agentic-team/bin/agentic_team.py`.\n\n"
        "A human-supplied plan is authoritative. When this harness generates an implementation\n"
        "plan artifact, that artifact must be a faithful transcription of the supplied plan - same\n"
        "scope, same sequence, nothing invented - and execution starts immediately. Do not pause to\n"
        "re-approve a plan the human already wrote; pause only at the hard human gates.\n"
    )
    rule_path = target / ".agents" / "rules" / "agentic-team.md"
    write_text(rule_path, rule)
    written.append(str(rule_path.relative_to(target)))
    workflows = {
        "start-platform.md": (
            "Start or resume a complete platform build",
            "Use the installed `agentic-build` skill. Initialize or resume a run, route specialists, "
            "execute, integrate, verify, and report.",
        ),
        "execute-given-plan.md": (
            "Build from a plan the user already wrote, without re-planning",
            "Use entry mode `execute-only`. Preserve the supplied plan as the authority and derive "
            "bounded task packets from it. Do not author a competing plan.",
        ),
        "fusion.md": (
            "Run an independent Fusion council on a high-stakes decision",
            "Use the installed `fusion-council` skill and the CLI fusion workspace. Keep proposals "
            "independent before reveal.",
        ),
        "progressive-context.md": (
            "Load only the current stage contract and its named inputs",
            "Use `bmad-progressive`; load only the router, current stage contract, and named inputs.",
        ),
        "verify.md": (
            "Independently verify the integrated result",
            "Use `agentic-verify` with a verifier independent from the builder.",
        ),
        "resume.md": (
            "Recover and resume an interrupted run",
            "Read `.agentic-team/CURRENT.md`, inspect CLI status, reconcile leases, and resume the "
            "active stage.",
        ),
    }
    for filename, (description, body) in workflows.items():
        title = filename.removesuffix(".md").replace("-", " ").title()
        path = target / ".agents" / "workflows" / filename
        write_text(path, f"---\ndescription: {description}\n---\n\n# {title}\n\n{body}")
        written.append(str(path.relative_to(target)))
    # Antigravity also reads a workspace-root AGENTS.md, as every other harness here does.
    upsert_managed_block(target / "AGENTS.md", managed_router())
    return written + ["AGENTS.md"]


def emit_pi(target: Path, selected: list[dict[str, Any]], root: Path) -> list[str]:
    upsert_managed_block(target / "AGENTS.md", managed_router())
    prompt_dir = target / ".pi" / "prompts"
    prompts = {
        "agentic-build.md": "Run or resume AgenticTeam using the agentic-build skill and durable state.",
        "fusion-council.md": "Run a Fusion council with independent proposals and preserved dissent.",
        "agentic-verify.md": "Independently verify the integrated result and issue an evidence-backed verdict.",
    }
    written = ["AGENTS.md"]
    for filename, content in prompts.items():
        path = prompt_dir / filename
        write_text(path, content)
        written.append(str(path.relative_to(target)))
    # Pi has no native subagent definition surface; keep selected roles in the durable bus.
    role_dir = target / ".agentic-team" / "agents"
    for agent in selected:
        _, prompt = agent_prompt(agent, root)
        path = role_dir / f"{agent['id']}.md"
        write_text(path, prompt)
        written.append(str(path.relative_to(target)))
    return written


def emit_generic(target: Path, selected: list[dict[str, Any]], root: Path) -> list[str]:
    written: list[str] = []
    out = target / ".agentic-team" / "agents"
    for agent in selected:
        _, prompt = agent_prompt(agent, root)
        path = out / f"{agent['id']}.md"
        write_text(path, prompt)
        written.append(str(path.relative_to(target)))
    upsert_managed_block(target / "AGENTS.md", managed_router())
    return written + ["AGENTS.md"]


def install_team(
    root: Path,
    target: Path,
    harness: str,
    preset: str,
    extra_agents: list[str],
    only_agents: list[str],
) -> dict[str, Any]:
    manifest = load_json(root / "team.json")
    if harness not in manifest.get("harnesses", {}):
        raise TeamError(f"Unknown harness '{harness}'")
    by_id = {agent["id"]: agent for agent in manifest["agents"]}
    if only_agents:
        unknown = [agent_id for agent_id in only_agents if agent_id not in by_id]
        if unknown:
            raise TeamError(f"Unknown agent(s): {', '.join(unknown)}")
        selected = [by_id[agent_id] for agent_id in dict.fromkeys(only_agents)]
        preset = "custom"
    else:
        selected = resolve_preset(manifest, preset)
    for agent_id in extra_agents:
        if agent_id not in by_id:
            raise TeamError(f"Unknown agent '{agent_id}'")
        if agent_id not in {agent["id"] for agent in selected}:
            selected.append(by_id[agent_id])
    target.mkdir(parents=True, exist_ok=True)
    bus = target / ".agentic-team"
    previous_record = load_json(bus / "install-manifest.json") if (bus / "install-manifest.json").is_file() else {}
    for directory in ("protocols", "config", "schemas"):
        copy_managed_tree(root / directory, bus / directory)
    if not (bus / "knowledge").exists():
        copy_managed_tree(root / "knowledge", bus / "knowledge")
    else:
        # Run-derived lessons and playbooks belong to the project; reinstall must not erase them.
        for relative in ("README.md", "playbooks/_template.md"):
            destination = bus / "knowledge" / relative
            if not destination.exists():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / "knowledge" / relative, destination)
    copy_managed_tree(root / "runtime" / "templates", bus / "templates")
    copy_managed_tree(root / "skills", target / manifest["harnesses"][harness]["skill_dir"])
    (bus / "bin").mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / "scripts" / "agentic_team.py", bus / "bin" / "agentic_team.py")
    installed_manifest = copy.deepcopy(manifest)
    installed_manifest["installation"] = {
        "harness": harness,
        "preset": preset,
        "installed_agents": [agent["id"] for agent in selected],
        "installed_at": utcnow(),
    }
    write_json_atomic(bus / "team.json", installed_manifest)
    write_text(bus / "AGENTS.md", (root / "runtime" / "templates" / "router.md").read_text(encoding="utf-8"))
    if not (bus / "CURRENT.md").exists():
        write_text(bus / "CURRENT.md", "# Current run\n\nNo active run. Initialize one with the AgenticTeam CLI.")
    emitters = {
        "claude-code": emit_claude,
        "codex": emit_codex,
        "opencode": emit_opencode,
        "antigravity": emit_antigravity,
        "gemini-cli": emit_gemini,
        "pi": emit_pi,
        "generic": emit_generic,
    }
    written = emitters[harness](target, selected, root)
    current_files = set(written)
    previous_skill_dir = previous_record.get("skill_dir")
    current_skill_dir = manifest["harnesses"][harness]["skill_dir"]
    if previous_skill_dir and previous_skill_dir != current_skill_dir:
        stale_skills = (target / previous_skill_dir).resolve()
        try:
            stale_skills.relative_to(target.resolve())
        except ValueError as exc:
            raise TeamError(f"Unsafe stale skill path in install manifest: {previous_skill_dir}") from exc
        if stale_skills.is_dir():
            # Claude Code auto-loads .claude/skills, so a leftover tree keeps running
            # against coordination paths the new harness may have re-pointed.
            shutil.rmtree(stale_skills, ignore_errors=True)
    for relative in set(previous_record.get("generated_files", [])) - current_files:
        candidate = (target / relative).resolve()
        try:
            candidate.relative_to(target.resolve())
        except ValueError as exc:
            raise TeamError(f"Unsafe stale generated path in install manifest: {relative}") from exc
        if relative in {"AGENTS.md", "CLAUDE.md", "GEMINI.md"}:
            remove_managed_block(candidate)
        elif candidate.is_file():
            candidate.unlink()
    record = {
        "version": VERSION,
        "harness": harness,
        "preset": preset,
        "agents": [agent["id"] for agent in selected],
        "skill_dir": manifest["harnesses"][harness]["skill_dir"],
        "generated_files": sorted(set(written)),
        "installed_at": utcnow(),
    }
    write_json_atomic(bus / "install-manifest.json", record)
    return record


def project_bus(project: Path) -> Path:
    bus = project.resolve() / ".agentic-team"
    if not (bus / "team.json").is_file():
        raise TeamError(f"AgenticTeam is not installed in {project.resolve()}")
    return bus


def find_run(project: Path, run: str | None) -> Path:
    bus = project_bus(project)
    if run:
        candidate = Path(run)
        if not candidate.is_absolute():
            candidate = bus / "runs" / run
    else:
        current = bus / "CURRENT.md"
        text = current.read_text(encoding="utf-8") if current.exists() else ""
        match = re.search(r"Run: `([^`]+)`", text)
        if not match:
            raise TeamError("No active run; pass --run or initialize a run")
        candidate = bus / "runs" / match.group(1)
    candidate = candidate.resolve()
    if not (candidate / "state.json").is_file():
        raise TeamError(f"Run not found: {candidate}")
    return candidate


def load_state(run_dir: Path) -> dict[str, Any]:
    return load_json(run_dir / "state.json")


def append_event(state: dict[str, Any], event_type: str, **details: Any) -> None:
    state.setdefault("events", []).append({"time": utcnow(), "type": event_type, **details})


def stage_contract(
    template: str,
    run_id: str,
    stage: tuple[str, str, str],
    active_stage: str,
    autonomy: str,
    context_method: str,
) -> str:
    stage_id, title, purpose = stage
    process = {
        "00_intake": "1. Normalize request and authority.\n2. Classify risk and entry.\n3. Record unknowns and recommendation.",
        "01_product": "1. Define users and outcomes.\n2. Bound scope.\n3. Write measurable acceptance and product risks.",
        "02_solution": "1. Map system and constraints.\n2. Define architecture/UX contracts.\n3. Run triggered specialist reviews.",
        "03_readiness": "1. Trace requirements to tasks/tests.\n2. Resolve dependencies and ownership.\n3. Record blockers and gates.",
        "04_build": "1. Claim ready tasks.\n2. Implement within ownership.\n3. Attach evidence.\n4. Integrate in dependency order.",
        "05_verify": "1. Build traceability matrix.\n2. Reproduce checks independently.\n3. Issue verdict and remediation.",
        "06_release": "1. Verify artifact identity.\n2. Prepare rollout/rollback.\n3. Obtain explicit human approval.",
        "07_learn": "1. Separate observation from inference.\n2. Create scoped lessons.\n3. Evaluate proposals before human promotion.",
    }[stage_id]
    outputs = {
        "00_intake": "- `../BRIEF.md`\n- `../ASSUMPTIONS.md`\n- initial risk and specialist routing",
        "01_product": "- `../PRD.md`\n- user journeys and acceptance map",
        "02_solution": "- `../ARCHITECTURE.md`\n- `../DESIGN.md` when applicable\n- decision and risk records",
        "03_readiness": "- `../READINESS.md`\n- executable task graph in state",
        "04_build": "- integrated product artifacts\n- task evidence under `tasks/` and state",
        "05_verify": "- `../VERIFICATION.md`\n- independent verdict and remediation tasks",
        "06_release": "- `../RELEASE.md`\n- approval, rollout, monitoring, and rollback evidence",
        "07_learn": "- `../RETROSPECTIVE.md`\n- scoped lessons and evaluated proposals",
    }[stage_id]
    gates = {
        "hitl": {"01_product", "02_solution", "03_readiness", "06_release"},
        "supervised": {"06_release"},
        "autonomous": {"06_release"},
    }
    human_check = "Human approval required before exit." if stage_id in gates[autonomy] else "No routine pause; record assumptions and continue if exit criteria pass."
    exit_criteria = "- Declared outputs exist and are internally consistent.\n- Material risks have owners.\n- Next work is executable from named context."
    return template.format(
        stage_title=title,
        run_id=run_id,
        stage=stage_id,
        status="active" if stage_id == active_stage else "pending",
        context_method=context_method,
        purpose=purpose,
        process=process,
        outputs=outputs,
        human_check=human_check,
        exit_criteria=exit_criteria,
    )


def initial_stage(entry_mode: str) -> str:
    return {"idea": "00_intake", "plan-given": "03_readiness", "execute-only": "04_build"}[entry_mode]


def init_run(project: Path, name: str, run_id: str | None, autonomy: str, entry_mode: str, context_method: str) -> Path:
    bus = project_bus(project)
    policy = load_json(bus / "config" / "policies.json")
    if autonomy not in policy["profiles"]:
        raise TeamError(f"Unknown autonomy profile '{autonomy}'")
    run_id = run_id or f"{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}-{slug(name)}"
    run_dir = bus / "runs" / slug(run_id)
    if run_dir.exists():
        raise TeamError(f"Run already exists: {run_dir.name}")
    template = (bus / "templates" / "stage-context.md").read_text(encoding="utf-8")
    active_stage = initial_stage(entry_mode)
    for stage_spec in STAGES:
        stage_dir = run_dir / stage_spec[0]
        stage_dir.mkdir(parents=True, exist_ok=True)
        write_text(stage_dir / "CONTEXT.md", stage_contract(template, run_dir.name, stage_spec, active_stage, autonomy, context_method))
    (run_dir / "04_build" / "tasks").mkdir(parents=True, exist_ok=True)
    for child in ("proposals", "critiques"):
        (run_dir / "_fusion" / child).mkdir(parents=True, exist_ok=True)
    (run_dir / "_decisions").mkdir(parents=True, exist_ok=True)
    (run_dir / "_context").mkdir(parents=True, exist_ok=True)
    stage = active_stage
    state: dict[str, Any] = {
        "version": VERSION,
        "run_id": run_dir.name,
        "project": name,
        "status": "active",
        "autonomy": autonomy,
        "entry_mode": entry_mode,
        "context_method": context_method,
        "stage": stage,
        "created_at": utcnow(),
        "updated_at": utcnow(),
        "tasks": {},
        "active_specialists": {},
        "checkpoints": [],
        "fusion_sessions": [],
        "events": [],
    }
    append_event(state, "run-created", stage=stage, autonomy=autonomy, entry_mode=entry_mode)
    token_path = issue_owner_token(run_dir.name, state)
    write_json_atomic(run_dir / "state.json", state)
    update_current(bus, state)
    print(
        f"Owner token written to {token_path}",
        file=sys.stderr,
    )
    print(
        "Keep it outside this project and do not paste it into an agent session; "
        "it is what proves a checkpoint decision came from you.",
        file=sys.stderr,
    )
    return run_dir


def update_current(bus: Path, state: dict[str, Any]) -> None:
    content = (
        "# Current run\n\n"
        f"Run: `{state['run_id']}`  \n"
        f"Status: `{state['status']}`  \n"
        f"Stage: `{state['stage']}`  \n"
        f"Context: `.agentic-team/runs/{state['run_id']}/{state['stage']}/CONTEXT.md`  \n"
        f"State: `.agentic-team/runs/{state['run_id']}/state.json`\n"
    )
    write_text(bus / "CURRENT.md", content)


def is_current_run(project: Path, run_dir: Path) -> bool:
    pointer = project_bus(project) / "CURRENT.md"
    if not pointer.is_file():
        return True
    return run_dir.name in pointer.read_text(encoding="utf-8")


def save_state(project: Path, run_dir: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = utcnow()
    write_json_atomic(run_dir / "state.json", state)
    update_current(project_bus(project), state)


def refresh_ready(state: dict[str, Any]) -> None:
    tasks = state["tasks"]
    for task in tasks.values():
        if task["status"] not in {"pending", "ready"}:
            continue
        dependencies = task.get("depends_on", [])
        task["status"] = "ready" if all(tasks.get(dep, {}).get("status") == "completed" for dep in dependencies) else "pending"


def route_specialists(project: Path, run_dir: Path, signals: list[str]) -> list[dict[str, Any]]:
    manifest = load_json(project_bus(project) / "team.json")
    installed = set(manifest.get("installation", {}).get("installed_agents", []))
    normalized = " ".join(signals).lower().replace("_", "-")
    searchable = f"{normalized} {normalized.replace(' ', '-')} {normalized.replace('-', ' ')}"
    matches: list[dict[str, Any]] = []
    for agent in manifest["agents"]:
        triggers = agent.get("activate_when", [])
        hit = [trigger for trigger in triggers if trigger.lower() in searchable]
        if hit and (not installed or agent["id"] in installed):
            matches.append({"agent": agent["id"], "matched": hit, "capabilities": agent["capabilities"]})
    with state_lock(run_dir):
        state = load_state(run_dir)
        for match in matches:
            state.setdefault("active_specialists", {})[match["agent"]] = {
                "status": "active",
                "reason": f"Matched signals: {', '.join(match['matched'])}",
                "activated_at": utcnow(),
            }
            append_event(state, "specialist-activated", agent=match["agent"], triggers=match["matched"])
        save_state(project, run_dir, state)
    return matches


def deactivate_specialist(project: Path, run_dir: Path, agent: str, reason: str) -> None:
    with state_lock(run_dir):
        state = load_state(run_dir)
        record = state.setdefault("active_specialists", {}).get(agent)
        if not record or record["status"] != "active":
            raise TeamError(f"Specialist is not active: {agent}")
        record.update(status="complete", deactivated_at=utcnow(), result=reason)
        append_event(state, "specialist-deactivated", agent=agent, reason=reason)
        save_state(project, run_dir, state)


def task_file(run_dir: Path, task_id: str) -> Path:
    return run_dir / "04_build" / "tasks" / f"{slug(task_id)}.md"


def add_task(project: Path, run_dir: Path, args: argparse.Namespace) -> None:
    installed_manifest = load_json(project_bus(project) / "team.json")
    installed = set(installed_manifest.get("installation", {}).get("installed_agents", []))
    if installed and args.owner not in installed:
        raise TeamError(f"Task owner '{args.owner}' is not installed in this project")
    with state_lock(run_dir):
        state = load_state(run_dir)
        if args.id in state["tasks"]:
            raise TeamError(f"Task already exists: {args.id}")
        missing = [dep for dep in args.depends_on if dep not in state["tasks"]]
        if missing:
            raise TeamError(f"Unknown dependencies: {', '.join(missing)}")
        objective = args.objective or args.title
        floor = derive_risk_floor(args.title, objective, args.stage, args.path)
        effective_risk = args.risk
        if RISK_ORDER[floor] > RISK_ORDER[args.risk]:
            effective_risk = floor
        task = {
            "id": args.id,
            "title": args.title,
            "objective": objective,
            "owner": args.owner,
            "stage": args.stage,
            "status": "pending",
            "risk": effective_risk,
            "declared_risk": args.risk,
            "risk_floor": floor,
            "depends_on": args.depends_on,
            "owned_paths": args.path,
            "inputs": args.input,
            "acceptance": args.acceptance,
            "evidence_contract": args.evidence_contract,
            "attempts": 0,
            "evidence": [],
            "created_at": utcnow(),
        }
        state["tasks"][args.id] = task
        refresh_ready(state)
        append_event(state, "task-added", task=args.id, owner=args.owner, risk=effective_risk)
        if effective_risk != args.risk:
            append_event(
                state, "risk-raised", task=args.id, declared=args.risk, effective=effective_risk
            )
        save_state(project, run_dir, state)
        template = (project_bus(project) / "templates" / "task.md").read_text(encoding="utf-8")
        write_text(
            task_file(run_dir, args.id),
            template.format(
                task_id=args.id,
                title=args.title,
                owner=args.owner,
                stage=args.stage,
                risk=args.risk,
                dependencies=", ".join(args.depends_on) or "none",
                owned_paths=", ".join(args.path) or "none declared",
                objective=task["objective"],
                inputs="\n".join(f"- {value}" for value in args.input) or "- None named",
                acceptance="\n".join(f"- [ ] {value}" for value in args.acceptance) or "- [ ] Objective demonstrated",
                evidence_contract="\n".join(f"- {value}" for value in args.evidence_contract) or "- Artifact paths and checks with results",
            ),
        )


# Words that betray an externally-visible or irreversible action regardless of how
# the calling agent chose to label the task. Risk is never taken on trust alone.
RISK_SIGNALS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "R4",
        (
            "drop table", "drop database", "truncate", "delete production", "purge",
            "force push", "force-push", "rewrite history", "credential", "secret key",
            "api key", "payment", "card number", "wire transfer", "contract", "legal",
        ),
    ),
    (
        "R3",
        (
            "deploy", "release to", "publish", "ship to production", "go live",
            "send email", "send sms", "broadcast", "post to", "announce",
            "purchase", "buy ", "spend", "billing", "invoice", "provision",
            "register domain", "dns", "campaign launch",
        ),
    ),
    (
        "R2",
        ("migration", "migrate", "install", "dependency", "upgrade", "refactor across", "schema change"),
    ),
)


def derive_risk_floor(title: str, objective: str, stage: str, paths: list[str]) -> str:
    """Lowest risk this task may legitimately claim, inferred from what it says it does.

    The declared --risk is a *request*; this is the floor it cannot go below. An agent
    labelling "deploy to production" as R1 does not get to skip the gate.
    """
    haystack = " ".join([title or "", objective or "", " ".join(paths or [])]).lower()
    floor = "R0"
    for level, needles in RISK_SIGNALS:
        if any(needle in haystack for needle in needles):
            if RISK_ORDER[level] > RISK_ORDER[floor]:
                floor = level
    if stage == "06_release" and RISK_ORDER[floor] < RISK_ORDER["R3"]:
        floor = "R3"
    return floor


def paths_overlap(left: str, right: str) -> bool:
    a = left.replace("\\", "/").strip("/")
    b = right.replace("\\", "/").strip("/")
    if not a or not b:
        return False
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def claim_task(project: Path, run_dir: Path, task_id: str, agent: str, lease_minutes: int) -> None:
    with state_lock(run_dir):
        state = load_state(run_dir)
        refresh_ready(state)
        task = state["tasks"].get(task_id)
        if not task:
            raise TeamError(f"Unknown task: {task_id}")
        if task["status"] != "ready":
            raise TeamError(f"Task {task_id} is {task['status']}, not ready")
        policy = load_json(project_bus(project) / "config" / "policies.json")["profiles"][state["autonomy"]]
        floor = derive_risk_floor(
            task.get("title", ""), task.get("objective", ""), task.get("stage", ""), task.get("owned_paths", [])
        )
        if RISK_ORDER[floor] > RISK_ORDER[task["risk"]]:
            task["risk"] = floor
            append_event(state, "risk-raised", task=task_id, effective=floor)
        if state.get("status") == "blocked":
            raise TeamError(
                "Run is blocked by a human rejection. Resolve the rejected checkpoint before claiming work."
            )
        requires_human = task["risk"] in policy["pause_at"] or task["risk"] in {"R3", "R4"}
        approved = any(
            item.get("kind") == "risk"
            and item.get("task") == task_id
            and item["status"] == "approved"
            for item in state["checkpoints"]
        )
        if requires_human and not approved:
            existing = next(
                (
                    item
                    for item in state["checkpoints"]
                    if item.get("kind") == "risk" and item.get("task") == task_id and item["status"] == "pending"
                ),
                None,
            )
            if not existing:
                checkpoint_id = f"CP-{len(state['checkpoints']) + 1:03d}"
                state["checkpoints"].append(
                    {
                        "id": checkpoint_id,
                        "status": "pending",
                        "kind": "risk",
                        "task": task_id,
                        "stage": task["stage"],
                        "risk": task["risk"],
                        "question": f"Approve {task['risk']} task {task_id}: {task['title']}?",
                        "recommendation": "Review the action, impact, evidence, and rollback before approval.",
                        "created_at": utcnow(),
                    }
                )
                append_event(state, "checkpoint-created", checkpoint=checkpoint_id, task=task_id, risk=task["risk"])
            state["status"] = "waiting-human"
            save_state(project, run_dir, state)
            raise TeamError(f"Task {task_id} requires human checkpoint approval before claim")
        for other in state["tasks"].values():
            if other["status"] != "claimed":
                continue
            for left in task.get("owned_paths", []):
                for right in other.get("owned_paths", []):
                    if paths_overlap(left, right):
                        raise TeamError(f"Owned path '{left}' overlaps claimed task {other['id']} path '{right}'")
        expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=lease_minutes)
        task.update(
            status="claimed",
            claimed_by=agent,
            claimed_at=utcnow(),
            lease_expires=expires.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        )
        append_event(state, "task-claimed", task=task_id, agent=agent)
        save_state(project, run_dir, state)


def complete_task(project: Path, run_dir: Path, task_id: str, agent: str, evidence: list[str]) -> None:
    if not evidence:
        raise TeamError("Completion requires at least one --evidence value")
    with state_lock(run_dir):
        state = load_state(run_dir)
        task = state["tasks"].get(task_id)
        if not task:
            raise TeamError(f"Unknown task: {task_id}")
        if task["status"] != "claimed" or task.get("claimed_by") != agent:
            raise TeamError(f"Task {task_id} is not claimed by {agent}")
        task.update(status="completed", completed_at=utcnow(), evidence=evidence)
        task.pop("lease_expires", None)
        refresh_ready(state)
        append_event(state, "task-completed", task=task_id, agent=agent, evidence=evidence)
        save_state(project, run_dir, state)


def fail_task(project: Path, run_dir: Path, task_id: str, agent: str, reason: str) -> None:
    with state_lock(run_dir):
        state = load_state(run_dir)
        task = state["tasks"].get(task_id)
        if not task or task.get("claimed_by") != agent or task["status"] != "claimed":
            raise TeamError(f"Task {task_id} is not claimed by {agent}")
        policy = load_json(project_bus(project) / "config" / "policies.json")
        maximum = policy["profiles"][state["autonomy"]]["max_task_retries"]
        task["attempts"] += 1
        task["last_failure"] = {"time": utcnow(), "reason": reason}
        task["status"] = "ready" if task["attempts"] <= maximum else "failed"
        append_event(state, "task-failed", task=task_id, agent=agent, reason=reason, retry=task["status"] == "ready")
        if task["status"] == "failed" and not policy["profiles"][state["autonomy"]]["continue_after_noncritical_failure"]:
            state["status"] = "blocked"
        save_state(project, run_dir, state)


def recover_leases(project: Path, run_dir: Path) -> int:
    recovered = 0
    with state_lock(run_dir):
        state = load_state(run_dir)
        policy = load_json(project_bus(project) / "config" / "policies.json")["profiles"][state["autonomy"]]
        now = dt.datetime.now(dt.timezone.utc)
        for task in state["tasks"].values():
            if task["status"] != "claimed" or not task.get("lease_expires"):
                continue
            expiry = dt.datetime.fromisoformat(task["lease_expires"].replace("Z", "+00:00"))
            if expiry > now:
                continue
            previous_agent = task.get("claimed_by")
            task["attempts"] += 1
            task["last_failure"] = {"time": utcnow(), "reason": "claim lease expired"}
            task["status"] = "ready" if task["attempts"] <= policy["max_task_retries"] else "failed"
            for field in ("claimed_by", "claimed_at", "lease_expires"):
                task.pop(field, None)
            append_event(
                state,
                "lease-recovered",
                task=task["id"],
                previous_agent=previous_agent,
                retry=task["status"] == "ready",
            )
            recovered += 1
        if recovered:
            refresh_ready(state)
            if any(task["status"] == "failed" for task in state["tasks"].values()) and not policy["continue_after_noncritical_failure"]:
                state["status"] = "blocked"
            save_state(project, run_dir, state)
    return recovered


def create_checkpoint(project: Path, run_dir: Path, question: str, recommendation: str, risk: str, kind: str, stage: str | None = None) -> str:
    with state_lock(run_dir):
        state = load_state(run_dir)
        checkpoint_id = f"CP-{len(state['checkpoints']) + 1:03d}"
        checkpoint = {
            "id": checkpoint_id,
            "status": "pending",
            "kind": kind,
            "stage": stage or state["stage"],
            "risk": risk,
            "question": question,
            "recommendation": recommendation,
            "created_at": utcnow(),
        }
        state["checkpoints"].append(checkpoint)
        state["status"] = "waiting-human"
        append_event(state, "checkpoint-created", checkpoint=checkpoint_id, risk=risk)
        save_state(project, run_dir, state)
        return checkpoint_id


def owner_token_path(run_id: str) -> Path:
    """Owner tokens live OUTSIDE the project, so a workspace-scoped agent cannot read them."""
    return Path.home() / ".agentic-team" / "owner-tokens" / f"{run_id}.token"


def issue_owner_token(run_id: str, state: dict[str, Any]) -> Path:
    token = secrets.token_urlsafe(24)
    state["owner_token_sha256"] = hashlib.sha256(token.encode("utf-8")).hexdigest()
    path = owner_token_path(run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(token + chr(10), encoding="utf-8")
    with contextlib.suppress(OSError, NotImplementedError):
        os.chmod(path, 0o600)
    return path


def assert_human_authority(project: Path, state: dict[str, Any], by: str, token: str | None) -> None:
    """A checkpoint decision must come from a human, not from the agent it is gating.

    Three independent barriers, because a filesystem cannot authenticate on its own:
      1. the approver may not name an installed agent;
      2. a headless caller must present the owner token, which is stored outside the project;
      3. an interactive terminal is accepted as the human channel when no token exists yet.
    """
    approver = (by or "").strip()
    if not approver:
        raise TeamError("--by is required and must name the responsible human")
    manifest = project_bus(project) / "team.json"
    if manifest.is_file():
        installed = load_json(manifest).get("installation", {}).get("installed_agents", [])
        lowered = {str(item).lower() for item in installed}
        probe = approver.lower()
        if probe in lowered or any(probe.startswith(f"{name} ") or f"({name}" in probe for name in lowered):
            raise TeamError(
                f"'{by}' is an installed agent. Checkpoint decisions require a human approver; "
                "agents may not approve the gates that block them."
            )
    digest = state.get("owner_token_sha256")
    hint = owner_token_path(state.get("run_id", "<run-id>"))
    if digest:
        # An agent shares the operator's terminal, so a TTY proves nothing here.
        # Possession of the out-of-project token is the only accepted proof.
        if not token:
            raise TeamError(
                "This decision requires the owner token. Pass --token with the value stored at "
                f"{hint}. Agents must not read that path."
            )
        if not secrets.compare_digest(hashlib.sha256(token.encode("utf-8")).hexdigest(), digest):
            raise TeamError("Invalid owner token.")
        return
    # Legacy runs created before tokens existed: fall back to an interactive channel.
    if sys.stdin.isatty():
        return
    raise TeamError(
        "This run predates owner tokens and cannot be decided headlessly. "
        "Re-run the decision from an interactive terminal."
    )


def approve_checkpoint(project: Path, run_dir: Path, checkpoint_id: str, by: str, decision: str, token: str | None = None) -> None:
    with state_lock(run_dir):
        state = load_state(run_dir)
        assert_human_authority(project, state, by, token)
        checkpoint = next((item for item in state["checkpoints"] if item["id"] == checkpoint_id), None)
        if not checkpoint:
            raise TeamError(f"Unknown checkpoint: {checkpoint_id}")
        if checkpoint["status"] != "pending":
            raise TeamError(f"Checkpoint {checkpoint_id} is already {checkpoint['status']}")
        checkpoint.update(status="approved", approved_by=by, decision=decision, approved_at=utcnow())
        still_rejected = any(item["status"] == "rejected" for item in state["checkpoints"])
        pending = any(item["status"] == "pending" for item in state["checkpoints"])
        state["status"] = "blocked" if still_rejected else ("waiting-human" if pending else "active")
        append_event(state, "checkpoint-approved", checkpoint=checkpoint_id, by=by)
        save_state(project, run_dir, state)


def reject_checkpoint(project: Path, run_dir: Path, checkpoint_id: str, by: str, decision: str, token: str | None = None) -> None:
    with state_lock(run_dir):
        state = load_state(run_dir)
        assert_human_authority(project, state, by, token)
        checkpoint = next((item for item in state["checkpoints"] if item["id"] == checkpoint_id), None)
        if not checkpoint:
            raise TeamError(f"Unknown checkpoint: {checkpoint_id}")
        if checkpoint["status"] != "pending":
            raise TeamError(f"Checkpoint {checkpoint_id} is already {checkpoint['status']}")
        checkpoint.update(status="rejected", rejected_by=by, decision=decision, rejected_at=utcnow())
        state["status"] = "blocked"
        append_event(state, "checkpoint-rejected", checkpoint=checkpoint_id, by=by)
        save_state(project, run_dir, state)


def clear_stale_lock(run_dir: Path, max_age_seconds: int = 0) -> str:
    """Remove a lock left behind by a process that died mid-command."""
    lock_path = run_dir / ".state.lock"
    if not lock_path.exists():
        return "No lock held."
    held = 0.0
    with contextlib.suppress(OSError):
        held = time.time() - lock_path.stat().st_mtime
    if max_age_seconds and held < max_age_seconds:
        raise TeamError(
            f"Lock is only {int(held)}s old; another command may still be running. "
            "Re-run with --force if you are sure."
        )
    lock_path.unlink()
    return f"Cleared stale lock held for {int(held)}s."


def reopen_task(project: Path, run_dir: Path, task_id: str, reason: str) -> None:
    """Return a failed or wedged task to the queue so a stage is never permanently stuck."""
    with state_lock(run_dir):
        state = load_state(run_dir)
        task = state["tasks"].get(task_id)
        if not task:
            raise TeamError(f"Unknown task: {task_id}")
        if task["status"] == "done":
            raise TeamError(f"Task {task_id} is already complete")
        task.update(status="pending", claimed_by=None, lease_expires_at=None, attempts=0)
        task["reopened_reason"] = reason
        refresh_ready(state)
        append_event(state, "task-reopened", task=task_id, reason=reason)
        save_state(project, run_dir, state)


def cancel_task(project: Path, run_dir: Path, task_id: str, reason: str) -> None:
    """Descope a task the human no longer wants, so it stops blocking the stage gate."""
    with state_lock(run_dir):
        state = load_state(run_dir)
        task = state["tasks"].get(task_id)
        if not task:
            raise TeamError(f"Unknown task: {task_id}")
        task.update(status="cancelled", claimed_by=None, lease_expires_at=None)
        task["cancelled_reason"] = reason
        refresh_ready(state)
        append_event(state, "task-cancelled", task=task_id, reason=reason)
        save_state(project, run_dir, state)


def advance_stage(project: Path, run_dir: Path) -> str:
    with state_lock(run_dir):
        state = load_state(run_dir)
        if state.get("status") == "blocked":
            raise TeamError(
                "Run is blocked by a human rejection. Resolve the rejected checkpoint before advancing."
            )
        current = state["stage"]
        open_tasks = [task["id"] for task in state["tasks"].values() if task["stage"] == current and task["status"] != "completed"]
        if open_tasks:
            raise TeamError(f"Current stage has unfinished tasks: {', '.join(open_tasks)}")
        policy = load_json(project_bus(project) / "config" / "policies.json")["profiles"][state["autonomy"]]
        gate_name = {"01_product": "product", "02_solution": "architecture", "03_readiness": "readiness", "06_release": "release"}.get(current)
        requires_human = gate_name == "release" or gate_name in policy["pause_at"]
        approved = any(
            item["kind"] == "stage" and item["stage"] == current and item["status"] == "approved"
            for item in state["checkpoints"]
        )
        if requires_human and not approved:
            existing = next(
                (item for item in state["checkpoints"] if item["kind"] == "stage" and item["stage"] == current and item["status"] == "pending"),
                None,
            )
            if not existing:
                checkpoint_id = f"CP-{len(state['checkpoints']) + 1:03d}"
                state["checkpoints"].append(
                    {
                        "id": checkpoint_id,
                        "status": "pending",
                        "kind": "stage",
                        "stage": current,
                        "risk": "R3" if current == "06_release" else "R2",
                        "question": f"Approve exit from {current}?",
                        "recommendation": "Approve only after reviewing declared outputs and evidence.",
                        "created_at": utcnow(),
                    }
                )
                append_event(state, "checkpoint-created", checkpoint=checkpoint_id, stage=current)
            state["status"] = "waiting-human"
            save_state(project, run_dir, state)
            return "waiting-human"
        index = STAGE_NAMES.index(current)
        if index == len(STAGE_NAMES) - 1:
            state["status"] = "complete"
            append_event(state, "run-completed")
            save_state(project, run_dir, state)
            return "complete"
        state["stage"] = STAGE_NAMES[index + 1]
        state["status"] = "verifying" if state["stage"] == "05_verify" else "active"
        append_event(state, "stage-advanced", previous=current, stage=state["stage"])
        save_state(project, run_dir, state)
        return state["stage"]


def fusion_dir(run_dir: Path, fusion_id: str) -> Path:
    return run_dir / "_fusion" / slug(fusion_id)


def fusion_init(project: Path, run_dir: Path, args: argparse.Namespace) -> None:
    contributors = list(dict.fromkeys(args.contributor))
    if len(contributors) < 2:
        raise TeamError("Fusion requires at least two distinct --contributor agents")
    if args.moderator in contributors or args.verifier in contributors:
        raise TeamError("Moderator and verifier must remain independent from contributors")
    installed_manifest = load_json(project_bus(project) / "team.json")
    installed = set(installed_manifest.get("installation", {}).get("installed_agents", []))
    participants = set(contributors + [args.moderator, args.verifier])
    missing = participants - installed if installed else set()
    if missing:
        raise TeamError(f"Fusion participants are not installed: {', '.join(sorted(missing))}")
    with state_lock(run_dir):
        state = load_state(run_dir)
        if any(item["id"] == args.id for item in state["fusion_sessions"]):
            raise TeamError(f"Fusion session already exists: {args.id}")
        session = {
            "id": args.id,
            "status": "proposals",
            "question": args.question,
            "sponsor": args.sponsor,
            "moderator": args.moderator,
            "verifier": args.verifier,
            "contributors": contributors,
            "submissions": {"proposal": {}, "critique": {}, "synthesis": {}, "verification": {}},
            "created_at": utcnow(),
        }
        state["fusion_sessions"].append(session)
        append_event(state, "fusion-created", fusion=args.id, contributors=contributors)
        save_state(project, run_dir, state)
    base = fusion_dir(run_dir, args.id)
    templates = project_bus(project) / "templates"
    brief = (templates / "fusion-brief.md").read_text(encoding="utf-8").format(
        fusion_id=args.id,
        question=args.question,
        sponsor=args.sponsor,
        moderator=args.moderator,
        verifier=args.verifier,
        contributors=", ".join(contributors),
    )
    write_text(base / "brief.md", brief)
    proposal = (templates / "fusion-proposal.md").read_text(encoding="utf-8")
    critique = (templates / "fusion-critique.md").read_text(encoding="utf-8")
    for agent in contributors:
        write_text(base / "proposals" / f"{agent}.md", proposal.format(agent=agent))
        write_text(base / "critiques" / f"{agent}.md", critique.format(agent=agent))
    write_text(base / "synthesis.md", (templates / "fusion-synthesis.md").read_text(encoding="utf-8"))
    write_text(base / "dissent.md", "# Dissent ledger\n\nRecord material unresolved arguments and consequences if they are correct.")
    write_text(base / "decision.md", (templates / "fusion-decision.md").read_text(encoding="utf-8"))


def fusion_submit(project: Path, run_dir: Path, fusion_id: str, kind: str, agent: str, evidence: str) -> str:
    with state_lock(run_dir):
        state = load_state(run_dir)
        session = next((item for item in state["fusion_sessions"] if item["id"] == fusion_id), None)
        if not session:
            raise TeamError(f"Unknown fusion session: {fusion_id}")
        allowed = {
            "proposal": session["contributors"],
            "critique": session["contributors"],
            "synthesis": [session["moderator"]],
            "verification": [session["verifier"]],
        }
        if agent not in allowed[kind]:
            raise TeamError(f"{agent} is not allowed to submit {kind}")
        session["submissions"][kind][agent] = {"time": utcnow(), "evidence": evidence}
        if kind == "proposal" and all(name in session["submissions"]["proposal"] for name in session["contributors"]):
            session["status"] = "critiques"
        elif kind == "critique" and all(name in session["submissions"]["critique"] for name in session["contributors"]):
            session["status"] = "synthesis"
        elif kind == "synthesis":
            session["status"] = "verification"
        elif kind == "verification":
            session["status"] = "decision"
        append_event(state, "fusion-submission", fusion=fusion_id, kind=kind, agent=agent)
        save_state(project, run_dir, state)
        return session["status"]


def fusion_close(project: Path, run_dir: Path, fusion_id: str, sponsor: str, decision: str) -> None:
    with state_lock(run_dir):
        state = load_state(run_dir)
        session = next((item for item in state["fusion_sessions"] if item["id"] == fusion_id), None)
        if not session:
            raise TeamError(f"Unknown fusion session: {fusion_id}")
        if session["status"] != "decision":
            raise TeamError(f"Fusion session is {session['status']}; synthesis and verification are required")
        if sponsor != session["sponsor"]:
            raise TeamError(f"Only sponsor {session['sponsor']} can close this council")
        session.update(status="complete", decision=decision, decided_at=utcnow())
        append_event(state, "fusion-completed", fusion=fusion_id, sponsor=sponsor)
        save_state(project, run_dir, state)


def learn(project: Path, run_dir: Path, title: str, evidence: str, lesson: str, scope: str, counterexample: str) -> Path:
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = run_dir / "07_learn" / f"lesson-{timestamp}-{slug(title)}.md"
    content = (
        f"# {title}\n\n- Source run: `{run_dir.name}`\n- Scope: {scope}\n- Recorded: {utcnow()}\n\n"
        f"## Evidence\n\n{evidence}\n\n## Scoped lesson\n\n{lesson}\n\n"
        f"## Counterexample / when not to apply\n\n{counterexample}\n\n"
        "## Promotion status\n\nCandidate only. Evaluate against a baseline and obtain human approval before changing team policy.\n"
    )
    write_text(path, content)
    with state_lock(run_dir):
        state = load_state(run_dir)
        append_event(state, "lesson-recorded", path=str(path.relative_to(run_dir)))
        save_state(project, run_dir, state)
    return path


def render_status(state: dict[str, Any]) -> str:
    counts: dict[str, int] = {}
    for task in state["tasks"].values():
        counts[task["status"]] = counts.get(task["status"], 0) + 1
    lines = [
        f"Run: {state['run_id']}",
        f"Status: {state['status']}",
        f"Stage: {state['stage']}",
        f"Autonomy: {state['autonomy']}",
        f"Context: {state['context_method']}",
        "Tasks: " + (", ".join(f"{key}={value}" for key, value in sorted(counts.items())) or "none"),
        f"Pending checkpoints: {sum(1 for item in state['checkpoints'] if item['status'] == 'pending')}",
        f"Fusion sessions: {len(state['fusion_sessions'])}",
        f"Active specialists: {sum(1 for item in state.get('active_specialists', {}).values() if item['status'] == 'active')}",
    ]
    return "\n".join(lines)


def generate_report(project: Path, run_dir: Path) -> Path:
    state = load_state(run_dir)
    path = run_dir / "DELIVERY-REPORT.md"
    completed = [task for task in state["tasks"].values() if task["status"] == "completed"]
    unfinished = [task for task in state["tasks"].values() if task["status"] != "completed"]
    evidence = "\n".join(f"- `{task['id']}`: {'; '.join(task.get('evidence', []))}" for task in completed) or "- No completed-task evidence recorded."
    open_work = "\n".join(f"- `{task['id']}` — {task['status']}: {task['title']}" for task in unfinished) or "- None recorded."
    approvals = "\n".join(f"- `{item['id']}` — {item['status']}: {item['question']}" for item in state["checkpoints"]) or "- No checkpoints recorded."
    content = (
        f"# AgenticTeam delivery report — {state['project']}\n\n"
        f"Generated: {utcnow()}  \nRun: `{state['run_id']}`  \nStatus: `{state['status']}`  \nStage: `{state['stage']}`\n\n"
        "## Outcome\n\nComplete this with the verified user outcome; state alone cannot infer product quality.\n\n"
        f"## Completed work and evidence\n\n{evidence}\n\n"
        f"## Open risks and unfinished work\n\n{open_work}\n\n"
        f"## Human approvals\n\n{approvals}\n\n"
        "## Verification, release, rollback, and learning\n\nLink the authoritative stage artifacts before presenting this report as final.\n"
    )
    write_text(path, content)
    return path


def doctor(project: Path) -> list[str]:
    findings: list[str] = []
    bus = project_bus(project)
    required = [
        "team.json",
        "AGENTS.md",
        "CURRENT.md",
        "bin/agentic_team.py",
        "config/policies.json",
        "protocols/guardrails.md",
        "protocols/agent-contract.md",
        "protocols/plan-modes.md",
    ]
    for relative in required:
        if not (bus / relative).is_file():
            findings.append(f"missing .agentic-team/{relative}")
    install = load_json(bus / "install-manifest.json") if (bus / "install-manifest.json").is_file() else None
    if not install:
        findings.append("missing install-manifest.json")
    else:
        manifest = load_json(bus / "team.json")
        known = {agent["id"] for agent in manifest["agents"]}
        missing_agents = set(install.get("agents", [])) - known
        if missing_agents:
            findings.append(f"install references unknown agents: {', '.join(sorted(missing_agents))}")
    with contextlib.suppress(TeamError):
        run_dir = find_run(project, None)
        lock_path = run_dir / ".state.lock"
        if lock_path.exists():
            held = 0
            with contextlib.suppress(OSError):
                held = int(time.time() - lock_path.stat().st_mtime)
            findings.append(
                f"run state lock held for {held}s; if no command is running, clear it with 'unlock'"
            )
        state = load_state(run_dir)
        if state.get("version") != VERSION:
            findings.append(f"active run version is {state.get('version')}, expected {VERSION}")
        if state.get("stage") not in STAGE_NAMES:
            findings.append(f"active run has unknown stage {state.get('stage')}")
    return findings


def add_common_run_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", default=".", help="Installed project root")
    parser.add_argument("--run", help="Run id; defaults to CURRENT.md")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AgenticTeam installer and deterministic orchestration state")
    parser.add_argument("--source", help="AgenticTeam source root (normally auto-detected)")
    parser.add_argument("--version", action="version", version=f"AgenticTeam {VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="Validate the source manifest, agents, skills, and required contracts")
    listing = sub.add_parser("list", help="List available agents, presets, or harnesses")
    listing.add_argument("kind", choices=["agents", "presets", "harnesses"])

    install = sub.add_parser("install", help="Compile and install native definitions into a project")
    install.add_argument("target")
    install.add_argument("--harness", required=True)
    install.add_argument("--preset", default="full-company")
    install.add_argument("--agent", action="append", default=[], help="Add an agent beyond the preset")
    install.add_argument("--only-agent", action="append", default=[], help="Install an exact custom selection; repeat per agent")

    init = sub.add_parser("init-run", help="Create a resumable progressive run")
    init.add_argument("--project", default=".")
    init.add_argument("--name", required=True)
    init.add_argument("--run-id")
    init.add_argument("--autonomy", choices=["autonomous", "supervised", "hitl"], default="hitl")
    init.add_argument("--entry", choices=["idea", "plan-given", "execute-only"], default="idea")
    init.add_argument("--context", choices=["adaptive", "bmad-progressive"], default="adaptive")

    status = sub.add_parser("status", help="Show durable run status")
    add_common_run_args(status)
    status.add_argument("--json", action="store_true")

    route = sub.add_parser("route-specialists", help="Activate installed specialists whose triggers match project signals")
    add_common_run_args(route)
    route.add_argument("--signal", action="append", required=True)
    route.add_argument("--json", action="store_true")

    deactivate = sub.add_parser("deactivate-specialist", help="Close a bounded specialist activation with its result")
    add_common_run_args(deactivate)
    deactivate.add_argument("--agent", required=True)
    deactivate.add_argument("--reason", required=True)

    add = sub.add_parser("add-task", help="Add a task envelope to the run graph")
    add_common_run_args(add)
    add.add_argument("--id", required=True)
    add.add_argument("--title", required=True)
    add.add_argument("--objective")
    add.add_argument("--owner", required=True)
    add.add_argument("--stage", choices=STAGE_NAMES, default="04_build")
    add.add_argument("--risk", choices=list(RISK_ORDER), default="R1")
    add.add_argument("--depends-on", action="append", default=[])
    add.add_argument("--path", action="append", default=[])
    add.add_argument("--input", action="append", default=[])
    add.add_argument("--acceptance", action="append", default=[])
    add.add_argument("--evidence-contract", action="append", default=[])

    claim = sub.add_parser("claim", help="Atomically claim a ready task")
    add_common_run_args(claim)
    claim.add_argument("--task", required=True)
    claim.add_argument("--agent", required=True)
    claim.add_argument("--lease-minutes", type=int, default=60)

    complete = sub.add_parser("complete", help="Complete a claimed task with evidence")
    add_common_run_args(complete)
    complete.add_argument("--task", required=True)
    complete.add_argument("--agent", required=True)
    complete.add_argument("--evidence", action="append", required=True)

    fail = sub.add_parser("fail", help="Record a failed attempt and apply retry policy")
    add_common_run_args(fail)
    fail.add_argument("--task", required=True)
    fail.add_argument("--agent", required=True)
    fail.add_argument("--reason", required=True)

    recover = sub.add_parser("recover-leases", help="Recover expired task claims according to retry policy")
    add_common_run_args(recover)

    checkpoint = sub.add_parser("checkpoint", help="Create a human decision checkpoint")
    add_common_run_args(checkpoint)
    checkpoint.add_argument("--question", required=True)
    checkpoint.add_argument("--recommendation", required=True)
    checkpoint.add_argument("--risk", choices=list(RISK_ORDER), default="R2")
    checkpoint.add_argument("--kind", default="decision")

    approve = sub.add_parser("approve", help="Record explicit human checkpoint approval")
    add_common_run_args(approve)
    approve.add_argument("--checkpoint", required=True)
    approve.add_argument("--by", required=True, help="Name of the responsible human (never an agent id)")
    approve.add_argument("--decision", required=True)
    approve.add_argument("--token", help="Owner token; required when running without an interactive terminal")

    reject = sub.add_parser("reject", help="Record explicit human rejection and block the run for correction")
    add_common_run_args(reject)
    reject.add_argument("--checkpoint", required=True)
    reject.add_argument("--by", required=True, help="Name of the responsible human (never an agent id)")
    reject.add_argument("--token", help="Owner token; required when running without an interactive terminal")
    reject.add_argument("--decision", required=True)

    advance = sub.add_parser("advance", help="Advance after task and policy gates pass")
    add_common_run_args(advance)

    unlock = sub.add_parser("unlock", help="Clear a state lock left by a process that died")
    add_common_run_args(unlock)
    unlock.add_argument("--force", action="store_true", help="Clear even a recently touched lock")

    reopen = sub.add_parser("reopen", help="Return a failed or wedged task to the queue")
    add_common_run_args(reopen)
    reopen.add_argument("--task", required=True)
    reopen.add_argument("--reason", required=True)

    cancel = sub.add_parser("cancel", help="Descope a task so it stops blocking the stage gate")
    add_common_run_args(cancel)
    cancel.add_argument("--task", required=True)
    cancel.add_argument("--reason", required=True)

    fusion = sub.add_parser("fusion-init", help="Create an independent fusion council workspace")
    add_common_run_args(fusion)
    fusion.add_argument("--id", required=True)
    fusion.add_argument("--question", required=True)
    fusion.add_argument("--sponsor", default="human-owner")
    fusion.add_argument("--moderator", default="fusion-moderator")
    fusion.add_argument("--verifier", default="qa-lead")
    fusion.add_argument("--contributor", action="append", required=True)

    submit = sub.add_parser("fusion-submit", help="Record a council proposal, critique, synthesis, or verification")
    add_common_run_args(submit)
    submit.add_argument("--fusion", required=True)
    submit.add_argument("--kind", choices=["proposal", "critique", "synthesis", "verification"], required=True)
    submit.add_argument("--agent", required=True)
    submit.add_argument("--evidence", required=True)

    close = sub.add_parser("fusion-close", help="Record the sponsor's final council decision")
    add_common_run_args(close)
    close.add_argument("--fusion", required=True)
    close.add_argument("--sponsor", required=True)
    close.add_argument("--decision", required=True)

    learning = sub.add_parser("learn", help="Record an evidence-scoped learning candidate")
    add_common_run_args(learning)
    learning.add_argument("--title", required=True)
    learning.add_argument("--evidence", required=True)
    learning.add_argument("--lesson", required=True)
    learning.add_argument("--scope", required=True)
    learning.add_argument("--counterexample", required=True)

    report = sub.add_parser("report", help="Generate a delivery report from durable evidence")
    add_common_run_args(report)

    health = sub.add_parser("doctor", help="Check an installed team and active run")
    health.add_argument("--project", default=".")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        root = source_root(args.source) if args.command in {"validate", "list", "install"} else None
        if args.command == "validate":
            if is_installed_bus(root):
                raise TeamError(
                    "This is the installed copy of the CLI, which has no role source tree. "
                    "Run 'validate' from the AgenticTeam source checkout, or use "
                    "'doctor --project .' to check this installation."
                )
            errors = validate_source(root)
            if errors:
                print("AgenticTeam validation failed:", file=sys.stderr)
                for error in errors:
                    print(f"- {error}", file=sys.stderr)
                return 1
            manifest = load_json(root / "team.json")
            print(f"OK: {len(manifest['agents'])} agents, {len(manifest['presets'])} presets, {len(manifest['harnesses'])} harnesses")
        elif args.command == "list":
            manifest = load_json(root / "team.json")
            if args.kind == "agents":
                for agent in manifest["agents"]:
                    trigger = f"; activates: {', '.join(agent.get('activate_when', []))}" if agent.get("activate_when") else ""
                    print(f"{agent['id']} [{agent['department']}/{agent['tier']}/{agent['access']}]{trigger}")
            else:
                for name, spec in manifest[args.kind].items():
                    print(f"{name}: {spec.get('description', '')}".rstrip())
        elif args.command == "install":
            errors = validate_source(root)
            if errors:
                raise TeamError("Source validation failed; run validate for details")
            record = install_team(root, Path(args.target).expanduser().resolve(), args.harness, args.preset, args.agent, args.only_agent)
            print(f"Installed {len(record['agents'])} agents for {record['harness']} using {record['preset']}")
        elif args.command == "init-run":
            run_dir = init_run(Path(args.project), args.name, args.run_id, args.autonomy, args.entry, args.context)
            print(run_dir)
        elif args.command == "doctor":
            findings = doctor(Path(args.project))
            if findings:
                print("Doctor found issues:", file=sys.stderr)
                for finding in findings:
                    print(f"- {finding}", file=sys.stderr)
                return 1
            print("OK: installation and active state are consistent")
        else:
            project = Path(args.project)
            run_dir = find_run(project, args.run)
            if args.command == "status":
                state = load_state(run_dir)
                print(json.dumps(state, indent=2) if args.json else render_status(state))
            elif args.command == "route-specialists":
                matches = route_specialists(project, run_dir, args.signal)
                if args.json:
                    print(json.dumps(matches, indent=2))
                else:
                    print("\n".join(f"{item['agent']}: {', '.join(item['matched'])}" for item in matches) or "No installed specialist triggers matched")
            elif args.command == "deactivate-specialist":
                deactivate_specialist(project, run_dir, args.agent, args.reason)
                print(f"Deactivated {args.agent}")
            elif args.command == "add-task":
                add_task(project, run_dir, args)
                print(f"Added task {args.id}")
            elif args.command == "claim":
                claim_task(project, run_dir, args.task, args.agent, args.lease_minutes)
                print(f"Claimed {args.task} by {args.agent}")
            elif args.command == "complete":
                complete_task(project, run_dir, args.task, args.agent, args.evidence)
                print(f"Completed {args.task}")
            elif args.command == "fail":
                fail_task(project, run_dir, args.task, args.agent, args.reason)
                print(f"Recorded failure for {args.task}")
            elif args.command == "recover-leases":
                print(f"Recovered {recover_leases(project, run_dir)} expired lease(s)")
            elif args.command == "checkpoint":
                checkpoint_id = create_checkpoint(project, run_dir, args.question, args.recommendation, args.risk, args.kind)
                print(checkpoint_id)
            elif args.command == "approve":
                approve_checkpoint(project, run_dir, args.checkpoint, args.by, args.decision, args.token)
                print(f"Approved {args.checkpoint}")
            elif args.command == "reject":
                reject_checkpoint(project, run_dir, args.checkpoint, args.by, args.decision, args.token)
                print(f"Rejected {args.checkpoint}; run is blocked for correction")
            elif args.command == "advance":
                outcome = advance_stage(project, run_dir)
                print(outcome)
                if outcome == "waiting-human":
                    # Non-zero so that `advance && next-step` cannot walk through a gate.
                    print(
                        "Stopped at a human gate: approve the open checkpoint before continuing.",
                        file=sys.stderr,
                    )
                    return 2
            elif args.command == "unlock":
                print(clear_stale_lock(run_dir, 0 if args.force else 30))
            elif args.command == "reopen":
                reopen_task(project, run_dir, args.task, args.reason)
                print(f"Reopened {args.task}")
            elif args.command == "cancel":
                cancel_task(project, run_dir, args.task, args.reason)
                print(f"Cancelled {args.task}")
            elif args.command == "fusion-init":
                fusion_init(project, run_dir, args)
                print(f"Created fusion session {args.id}")
            elif args.command == "fusion-submit":
                status = fusion_submit(project, run_dir, args.fusion, args.kind, args.agent, args.evidence)
                print(f"Fusion {args.fusion}: {status}")
            elif args.command == "fusion-close":
                fusion_close(project, run_dir, args.fusion, args.sponsor, args.decision)
                print(f"Completed fusion session {args.fusion}")
            elif args.command == "learn":
                path = learn(project, run_dir, args.title, args.evidence, args.lesson, args.scope, args.counterexample)
                print(path)
            elif args.command == "report":
                print(generate_report(project, run_dir))
        return 0
    except TeamError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
