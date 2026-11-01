"""Refresh the local, offline team reference from the audited roster and repository."""
import csv
import io
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
manifest = json.loads((ROOT / "team.json").read_text(encoding="utf-8"))
roster = json.loads((HERE / "roster.json").read_text(encoding="utf-8"))
if isinstance(roster, dict):
    roster = roster["agents"]
assert [r["id"] for r in roster] == [r["id"] for r in manifest["agents"]]
for role, canonical in zip(roster, manifest["agents"]):
    role.update({k: canonical[k] for k in ("id", "department", "tier", "access", "reports_to", "capabilities")})
    role["path"] = canonical["file"]
    role["prompt"] = (ROOT / canonical["file"]).read_text(encoding="utf-8")
core = ["delivery-lead", "context-engineer", "qa-lead", "eval-engineer", "security-engineer", "sre-engineer"]
data = {
    "date": "2026-11-01", "timezone": "Asia/Riyadh", "version": manifest["version"],
    "commit": subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip(),
    "agents": roster, "harnesses": manifest["harnesses"], "profiles": manifest["model_profiles"],
    "presets": manifest["presets"], "defaults": manifest["defaults"], "core": core,
    "safety": json.loads((HERE / "safety.json").read_text(encoding="utf-8")),
    "guarantees": json.loads((ROOT / "config/guarantees.json").read_text(encoding="utf-8")),
}
documents = []
for ident, title, plan_name, prompt_name in [
    ("master", "Complete implementation program", "autonomy-implementation-plan.md", "autonomy-implementation-prompt.md"),
    ("supervisor", "Supervisor safety, pilot and activation", "supervisor-completion-plan.md", "supervisor-completion-prompt.md"),
    ("quality", "Quality qualification and model changes", "quality-qualification-plan.md", "quality-qualification-prompt.md"),
    ("core", "Six persistent core responsibilities", "durable-core-plan.md", "durable-core-prompt.md"),
]:
    plan = (ROOT / "docs" / plan_name).read_text(encoding="utf-8")
    prompt = (ROOT / "docs" / prompt_name).read_text(encoding="utf-8")
    blocks = re.findall(r"```(?:text)?\n(.*?)```", prompt, re.S)
    documents.append({"id": ident, "title": title, "plan_name": plan_name,
                      "prompt_name": prompt_name, "plan": plan, "prompt": prompt,
                      "copy_prompt": max(blocks, key=len).strip() if blocks else (prompt.partition("\n---\n")[2] or prompt).strip()})
data["documents"] = documents
encoded = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
template = (HERE / "guide.template.html").read_text(encoding="utf-8")
assert template.count("__GUIDE_DATA__") == 1
(HERE / "index.html").write_text(template.replace("__GUIDE_DATA__", encoded), encoding="utf-8")
out = io.StringIO(newline="")
writer = csv.writer(out, lineterminator="\n")
writer.writerow(["Order", "Agent", "Department", "Reports to", "Harness", "Typical tasks", "Specialty", "Description", "Prompt file", "Access", "Model tier", "Activation", "Durable agent today / recommended target"])
for i, role in enumerate(roster, 1):
    tasks = role["tasks"]
    if isinstance(tasks, list): tasks = "; ".join(tasks)
    writer.writerow([i, role["id"], role["department"], role["reports_to"], "All 13 compiler targets; runtime support varies", tasks, role["specialty"], role["description"], role["path"], role["access"], role["tier"], role.get("activation", ""), "Saved role; no active durable service verified" + (" / proposed persistent core" if role["id"] in core else " / on-demand worker")])
(HERE / "agent-roster.csv").write_text(out.getvalue(), encoding="utf-8-sig")
print(f"Built offline guide and CSV: {len(roster)} roles, {len(data['harnesses'])} harness targets; source {data['commit']}.")
