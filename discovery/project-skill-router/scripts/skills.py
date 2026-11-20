"""Bounded skill lookup and project-local links; Python 3.10+, stdlib at runtime."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

REPO = Path(__file__).resolve().parents[3]
LIBRARY = REPO / "skills"
CATALOG = REPO / "catalog"
STOP = set("a an the to of for and or with in on use when this skill project create build implement fix".split())
CATEGORY_LABELS = {
    "blender": "Blender assets, scenes and add-ons",
    "unreal": "Unreal Engine",
    "audio": "Audio, music, JUCE and DSP",
    "threejs": "Three.js, shaders and 3D web graphics",
    "ui-web": "UI/UX, frontend and web design",
    "games": "Engine-neutral game development and other engines",
    "google": "Google, Chrome, Stitch and browser tools",
    "other": "Related creative and interface helpers",
}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tokens(text):
    return set(re.findall(r"[a-z0-9]+", text.lower())) - STOP


def excluded(name):
    engines = read_json(REPO / "skill-exclusions.json")["excluded_engines"]
    return bool(set(re.split(r"[-_/]", name.lower())) & set(engines))


def category(name, description):
    n, d = name.lower(), description.lower()
    if "blender" in n or "blender" in d:
        return "blender"
    if "unreal" in n or n.startswith("ue-"):
        return "unreal"
    if re.search(r"audio|juce|sound|music|dsp|synth|webaudio|earshot|vst3|clap-review|au-review", n):
        return "audio"
    if re.search(r"threejs|three-js|^3d-|webgl|shader|ocean|raymarch", n):
        return "threejs"
    if re.search(r"frontend|interface|^ui-|ux|design|css|tailwind|stitch|gsap|animate|animation|browser|chrome|react|nextjs|^web-|accessibility", n):
        return "ui-web"
    if re.search(r"game|gamedev|bevy|phaser|pixijs|defold|love2d|pygame|ebitengine|platformer|roguelike|^rpg$|tower-defense|^puzzle$|card-game", n):
        return "games"
    if re.search(r"docx|^pdf$|pptx|xlsx|spreadsheet|presentation|doc-coauthor|notebook|transcrib", n):
        return "documents"
    if re.search(r"security|pentest|penetration|vulnerab|exploit|forensic|red-team|threat|injection|fuzz|privilege|metasploit|nmap|burp", n + " " + d[:100]):
        return "security"
    if n.endswith("-automation") or "-integration" in n:
        return "automation"
    if re.search(r"azure|aws|cloud|database|postgres|sql|backend|api-|graphql|kubernetes|k8s|docker|redis|terraform|mongo|serverless", n):
        return "backend"
    if re.search(r"code|git|test|debug|review|architect|refactor|python|typescript|javascript|dotnet|csharp|cpp|java|rust|golang|devops|workflow|agent|context", n):
        return "engineering"
    return "other"


def build_catalog():
    try:
        import yaml
    except ImportError:
        raise ValueError("Catalog rebuilding requires PyYAML: python -m pip install PyYAML. Lookup and project selection do not.")
    records = []
    policy = read_json(REPO / "library-policy.json")
    approved = set(policy["approved_primary_ids"])
    managed = set(policy["application_managed_names"])
    google_ids = {Path(i["destination"]).name for i in read_json(REPO / "google-browser-skills.json")["chrome_devtools"]["skills"]}
    google_ids.update(Path(i["destination"]).name for i in read_json(REPO / "github-skill-imports-2026-11-20.json")["imports"] if i["repository"].startswith(("GoogleChrome/", "google-labs-code/")))
    google_ids.update({"gemini-api-dev", "imagen"})
    for file in sorted(LIBRARY.rglob("SKILL.md")):
        if file.is_symlink() or "_shared" in file.relative_to(LIBRARY).parts:
            continue
        identifier = file.parent.relative_to(LIBRARY).as_posix()
        if identifier.split("/")[0] not in approved:
            raise ValueError(f"Unreviewed skill outside library policy: {identifier}")
        if excluded(identifier):
            continue
        text = file.read_text(encoding="utf-8-sig")
        parts = text.split("---", 2)
        if not text.startswith("---") or len(parts) != 3:
            raise ValueError(f"Missing skill frontmatter: {identifier}")
        try:
            metadata = yaml.safe_load(parts[1])
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid skill frontmatter: {identifier}: {exc}") from exc
        if not isinstance(metadata, dict) or not isinstance(metadata.get("name"), str) or not isinstance(metadata.get("description"), str):
            raise ValueError(f"Skill name and description must be strings: {identifier}")
        name = metadata["name"].strip()
        description = " ".join(metadata["description"].split())
        if not name or not description:
            raise ValueError(f"Missing name/description: {identifier}")
        if name in managed:
            raise ValueError(f"Application-managed skill must not be copied into the additional library: {identifier}")
        group = "google" if identifier in google_ids else category(name, description)
        if group not in CATEGORY_LABELS:
            group = "other"
        records.append({"id": identifier, "name": name, "description": description,
                        "category": group, "path": file.relative_to(REPO).as_posix(),
                        "primary": "/" not in identifier, "dependencies": [],
                        "sha256": hashlib.sha256(file.read_bytes()).hexdigest()})
    ids = {r["id"] for r in records}
    for row in records:
        text = (REPO / row["path"]).read_text(encoding="utf-8-sig")
        dependencies = set(re.findall(r"\.\./([a-z0-9][a-z0-9-]+)/", text)) & ids
        if row["category"] == "blender" and row["id"] != "blender-core":
            dependencies.add("blender-core")
        dependencies.discard(row["id"])
        row["dependencies"] = sorted(dependencies)
    profiles = read_json(CATALOG / "profiles.json")
    for name, profile in profiles.items():
        unknown = set(profile["skills"]) - ids
        if unknown:
            raise ValueError(f"Profile {name} has unknown skills: {sorted(unknown)}")
    audit = subprocess.run([sys.executable, str(REPO / "tools/audit-library.py")], capture_output=True, text=True, encoding="utf-8")
    if audit.returncode != 0 or json.loads(audit.stdout).get("identical_instruction_bodies"):
        raise ValueError("Bundled, duplicate or invalid instructions detected. Run python tools/audit-library.py to review before publishing the catalog.")
    write_json(CATALOG / "skills.json", {"version": 1, "skills": records})
    counts = collections.Counter(r["category"] for r in records)
    lines = ["SHARED SKILL CATALOG", "", "Start with project-skill-router; query metadata before reading selected instructions.",
             f"{sum(r['primary'] for r in records)} primary skills; {len(records)} total entries including nested skills.",
             "All canonical skill files remain in skills/. Only discovery/project-skill-router is globally exposed.", "", "CATEGORIES"]
    for key, label in CATEGORY_LABELS.items():
        lines.append(f"{key}: {counts[key]} — {label} (categories/{key}.txt)")
        category_lines = [label, "", "Generated metadata index; prefer bounded CLI search to reading this entire file.", ""]
        for r in records:
            if r["category"] == key:
                category_lines.append(f"{r['id']} | {r['name']} | {r['description'][:140]}")
        path = CATALOG / "categories" / (key + ".txt")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(category_lines) + "\n", encoding="utf-8")
    lines += ["", "STARTER PROFILES"] + [f"{k}: {v['description']} ({len(v['skills'])} starter skills)" for k, v in profiles.items()]
    (CATALOG / "INDEX.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"entries": len(records), "primary_skills": sum(r["primary"] for r in records), "categories": dict(counts)}


def load_catalog():
    path = CATALOG / "skills.json"
    if not path.exists():
        raise ValueError("Catalog missing. Run this script with build first.")
    return read_json(path)["skills"]


def lookup(records, key):
    exact = [r for r in records if r["id"] == key]
    matches = exact or [r for r in records if r["name"] == key]
    if not matches:
        raise ValueError(f"Unknown skill: {key}. Search the catalog first.")
    return sorted(matches, key=lambda r: (not r["primary"], r["id"]))[0]


def search(records, query, category_filter=None, limit=6):
    wanted = tokens(query)
    ranked = []
    for row in records:
        if category_filter and row["category"] != category_filter:
            continue
        title = tokens(row["id"] + " " + row["name"])
        positive = re.split(r"\b(?:skip for|not for|do not (?:use|invoke|trigger))\b", row["description"], maxsplit=1, flags=re.I)[0]
        desc = tokens(positive)
        matched = wanted & (title | desc)
        if wanted and not matched:
            continue
        score = 6 * len(wanted & title) + len(wanted & desc) + 4 * (wanted <= title) + len(matched) / max(1, len(wanted))
        ranked.append((len(matched), score, row))
    # Do not pad a precise match (e.g. Unreal Niagara) with unrelated Unreal skills.
    coverage = max((item[0] for item in ranked), default=0)
    ranked = [item for item in ranked if item[0] == coverage]
    ranked.sort(key=lambda item: (-item[1], not item[2]["primary"], item[2]["id"]))
    return [{"id": r["id"], "name": r["name"], "category": r["category"], "description": r["description"][:220]} for _, _, r in ranked[:limit]]


def expand_selection(records, keys):
    selected = {}
    pending = list(keys)
    while pending:
        row = lookup(records, pending.pop(0))
        if row["id"] in selected:
            continue
        if excluded(row["id"]):
            raise ValueError(f"Excluded engine skill: {row['id']}")
        selected[row["id"]] = row
        pending += row["dependencies"]
    return sorted(selected)


def recommend(project, task):
    project = Path(project).expanduser().resolve()
    if not project.is_dir():
        raise ValueError(f"Project directory missing: {project}")
    profiles, signals = [], []
    def add(profile, reason):
        if profile not in profiles:
            profiles.append(profile)
            signals.append(reason)
    task_lower = task.lower()
    files = list(project.iterdir())[:300]
    if any(p.suffix.lower() == ".uproject" for p in files) or re.search(r"\bunreal\b|\bue5\b", task_lower):
        add("unreal", "Unreal project/request")
    cmake = project / "CMakeLists.txt"
    cmake_text = cmake.read_text(encoding="utf-8", errors="replace")[:64000].lower() if cmake.is_file() else ""
    if "juce" in cmake_text or "juce" in task_lower:
        add("juce", "JUCE project/request")
    elif re.search(r"\baudio\b|\bdsp\b|synthesi", task_lower):
        add("audio", "Audio/DSP request")
    if "blender" in task_lower or any(p.suffix.lower() == ".blend" for p in files):
        add("blender-addon" if re.search(r"add.?on|extension", task_lower) else "blender", "Blender project/request")
    package = project / "package.json"
    deps = {}
    if package.is_file():
        try:
            data = read_json(package)
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        except (ValueError, TypeError):
            signals.append("package.json could not be parsed; no framework assumed")
    if "three" in deps or re.search(r"three\.?js|\bwebgl\b|\bwebgpu\b", task_lower):
        add("threejs", "Three.js/3D web project or request")
    ui_task = bool(re.search(r"\bui\b|\bux\b|web.?site|landing page|frontend|dashboard|web design|\breact\b|next\.?js|\bcss\b|\bhtml\b", task_lower))
    frontend_deps = bool(set(deps) & {"react", "next", "vue", "svelte", "@angular/core", "astro", "vite"})
    if ui_task or (not task and (frontend_deps or (project / "index.html").is_file())):
        add("react" if "react" in deps or "next" in deps else "web", "Web interface request/project")
    if re.search(r"browser automat|chrome devtools|inspect.*page|debug.*browser", task_lower):
        add("browser", "Live browser automation/debugging request")
    return {"profiles": profiles or ["general"], "signals": signals,
            "note": "Preview only. Choose relevant profiles and add specialists for the current task; routine work may need none."}


def is_link(path):
    return path.is_symlink() or (os.name == "nt" and bool(os.lstat(path).st_file_attributes & 0x400))


def link_directory(source, destination):
    if os.name == "nt":
        # Environment variables avoid injecting paths into PowerShell source text.
        env = {**os.environ, "SKILLS_LINK_SOURCE": str(source), "SKILLS_LINK_DEST": str(destination)}
        subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                        "New-Item -ItemType Junction -Path $env:SKILLS_LINK_DEST -Target $env:SKILLS_LINK_SOURCE | Out-Null"],
                       env=env, check=True, capture_output=True)
    else:
        destination.symlink_to(source, target_is_directory=True)


def selection(records, project, profiles, skills, apply=False, replace=False):
    project = Path(project).expanduser().resolve()
    if not project.is_dir():
        raise ValueError(f"Project directory missing: {project}")
    agents = project / ".agents"
    root = agents / "skills"
    state_file = agents / ".skill-links.local.json"
    manifest_file = agents / "skill-profile.json"
    definitions = read_json(CATALOG / "profiles.json")
    requested = list(skills)
    for profile in profiles:
        if profile not in definitions:
            raise ValueError(f"Unknown profile: {profile}")
        requested += definitions[profile]["skills"]
    manifest = read_json(manifest_file) if manifest_file.exists() else {"profiles": [], "skills": []}
    if not requested and not profiles:
        requested = manifest["skills"]
        profiles = manifest["profiles"]
    elif not replace:
        requested += manifest["skills"]
        profiles = sorted(set(profiles + manifest["profiles"]))
    identifiers = expand_selection(records, requested)
    result = {"project": str(project), "profiles": profiles, "skills": identifiers, "applied": False}
    if not apply:
        return result
    if project == Path.home().resolve() or (agents.exists() and agents.resolve() != agents) or (root.exists() and root.resolve() != root):
        raise ValueError("Project skill root must be a real project-local directory, not a global or redirected skill root.")
    state = read_json(state_file) if state_file.exists() else {"links": {}}
    old = state["links"]
    desired = {identifier.replace("/", "--"): str((REPO / lookup(records, identifier)["path"]).parent.resolve()) for identifier in identifiers}
    if identifiers and (LIBRARY / "_shared").is_dir():
        desired["_shared"] = str((LIBRARY / "_shared").resolve())
    # Preflight the entire change before creating or removing any links.
    for name in set(old) | set(desired):
        if Path(name).name != name or name in {".", ".."}:
            raise ValueError("Invalid managed link name")
        path = root / name
        present = os.path.lexists(path)
        if present:
            expected = old.get(name, desired.get(name))
            if not is_link(path) or str(path.resolve()) != expected:
                raise ValueError(f"Unmanaged or changed project skill preserved; resolve collision first: {path}")
        if name in desired and not Path(desired[name]).is_dir():
            raise ValueError(f"Missing canonical skill: {name}")
    root.mkdir(parents=True, exist_ok=True)
    # Add before pruning, retaining the previous selection if a new link fails.
    for name, target in desired.items():
        path = root / name
        if not os.path.lexists(path):
            link_directory(Path(target), path)
    for name in set(old) - set(desired):
        path = root / name
        if os.path.lexists(path):
            if path.is_symlink():
                path.unlink()
            else:
                os.rmdir(path)  # Remove the verified junction itself, never its target.
    write_json(state_file, {"version": 1, "links": desired})
    write_json(manifest_file, {"version": 1, "profiles": profiles, "skills": identifiers})
    update_block(agents / ".gitignore", "skill-routing", ".skill-links.local.json")
    update_block(root / ".gitignore", "skill-routing", "\n".join("/" + name + "/" for name in sorted(desired)))
    return {**result, "applied": True, "manifest": str(manifest_file), "note": "Read canonical SKILL.md paths now; reload the app/new conversation if discovery has not refreshed."}


def update_block(path, marker, content):
    start, end = f"# BEGIN {marker}", f"# END {marker}"
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    block = start + "\n" + content + "\n" + end
    if start in current and end in current:
        current = current[:current.index(start)] + block + current[current.index(end) + len(end):]
    else:
        current = current.rstrip() + ("\n\n" if current.strip() else "") + block + "\n"
    path.write_text(current, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build")
    sub.add_parser("categories")
    sub.add_parser("profiles")
    search_cmd = sub.add_parser("search")
    search_cmd.add_argument("query")
    search_cmd.add_argument("--category", choices=list(CATEGORY_LABELS))
    search_cmd.add_argument("--limit", type=int, choices=range(1, 51), default=6, metavar="1..50")
    show = sub.add_parser("show")
    show.add_argument("skill")
    recommend_cmd = sub.add_parser("recommend")
    recommend_cmd.add_argument("--project", required=True)
    recommend_cmd.add_argument("--task", default="")
    use = sub.add_parser("use")
    use.add_argument("--project", required=True)
    use.add_argument("--profile", action="append", default=[])
    use.add_argument("--skill", action="append", default=[])
    use.add_argument("--apply", action="store_true")
    use.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    if args.command == "build":
        result = build_catalog()
    elif args.command == "profiles":
        result = read_json(CATALOG / "profiles.json")
    elif args.command == "recommend":
        result = recommend(args.project, args.task)
    else:
        records = load_catalog()
        if args.command == "categories":
            result = dict(collections.Counter(row["category"] for row in records))
        elif args.command == "search":
            result = search(records, args.query, args.category, args.limit)
        elif args.command == "show":
            row = lookup(records, args.skill)
            result = {**row, "instruction_file": str((REPO / row["path"]).resolve())}
        else:
            result = selection(records, args.project, args.profile, args.skill, args.apply, args.replace)
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        sys.exit(1)
