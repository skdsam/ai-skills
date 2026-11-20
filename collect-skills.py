"""Collect local user skills without overwriting existing versions. Python 3.9+."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parent
DEST = REPO / "skills"
HOME = Path.home()
SOURCES = [HOME / p for p in [
    ".codex/skills", ".gemini/config/skills",
    ".gemini/antigravity/global_skills", ".gemini/antigravity-ide/skills",
    ".antigravity-sync/antigravity/global_skills", ".gemini/antigravity-backup/skills",
]]
SKIP = {".git", "__pycache__", "node_modules", ".venv", "venv"}

def excluded_skill(name):
    config = json.loads((REPO / "skill-exclusions.json").read_text(encoding="utf-8"))
    words = set(re.split(r"[-_]", name.lower()))
    return bool(words.intersection(config["excluded_engines"]))

def content(folder):
    result = {}
    for p in sorted(folder.rglob("*")):
        rel = p.relative_to(folder)
        if p.is_file() and not any(x in SKIP for x in rel.parts) and p.suffix != ".pyc":
            result[rel.as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result

def digest(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()

def main():
    known = {}
    for p in DEST.iterdir():
        if p.is_dir() and (p / "SKILL.md").exists():
            known.setdefault(p.name, {})[digest(content(p))] = p.name
    variants = REPO / "archive" / "variants"
    if variants.exists():
        for p in variants.iterdir():
            if p.is_dir() and (p / "SKILL.md").exists():
                name = p.name.rsplit("--", 1)[0]
                known.setdefault(name, {})[digest(content(p))] = "../archive/variants/" + p.name
    records = []
    copied = 0
    for root in SOURCES:
        if not root.exists() or root.resolve() in {DEST.resolve(), (REPO / "discovery").resolve()}:
            continue
        for source in sorted(root.iterdir()):
            if not source.is_dir() or not (source / "SKILL.md").is_file():
                continue
            if excluded_skill(source.name):
                continue
            files = content(source)
            fingerprint = digest(files)
            versions = known.setdefault(source.name, {})
            target = versions.get(fingerprint)
            if target is None:
                target = source.name if not (DEST / source.name).exists() else f"../archive/variants/{source.name}--{fingerprint[:16]}"
                out = DEST / target
                if out.exists():
                    raise RuntimeError(f"Destination collision: {out}")
                out.mkdir(parents=True)
                for rel in files:
                    dst = out / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source / rel, dst)
                if content(out) != files:
                    raise RuntimeError(f"Copy verification failed: {out}")
                versions[fingerprint] = target
                copied += 1
            records.append({"source": source.relative_to(HOME).as_posix(), "destination": target, "sha256": fingerprint})
    (REPO / "last-collection.local.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print(f"Copied {copied} skill folders; catalogued {len(records)} source folders.")
    print(f"Primary skills: {sum((p / 'SKILL.md').is_file() for p in DEST.iterdir() if p.is_dir())}")
    print(f"Alternate versions: {len(list(variants.iterdir())) if variants.exists() else 0}")
    if copied:
        subprocess.run([sys.executable, str(REPO / "discovery/project-skill-router/scripts/skills.py"), "build"], check=True)

if __name__ == "__main__":
    main()
