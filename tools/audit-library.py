"""Read-only audit of additional skills against local application-managed skills."""
from pathlib import Path
import hashlib
import json
import sys

import yaml  # Same maintenance-only dependency as catalog rebuilding.

REPO = Path(__file__).resolve().parents[1]
HOME = Path.home()
ROOTS = [HOME / rel for rel in (
    ".codex/skills/.system", ".codex/plugins/cache",
    ".gemini/antigravity/builtin/skills", ".gemini/antigravity-ide/builtin/skills",
    ".gemini/antigravity-ide/plugins", ".gemini/config/plugins",
)]


def metadata(path, allow_plaintext=False):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    parts = text.split("---", 2)
    if not text.startswith("---") or len(parts) != 3:
        if not allow_plaintext:
            raise ValueError(f"Missing frontmatter: {path}")
        name, body = path.parent.name, text
    else:
        data = yaml.safe_load(parts[1])
        name, body = data["name"], parts[2]
    return {"name": name, "file_sha256": hashlib.sha256(raw).hexdigest(),
            "body_sha256": hashlib.sha256(body.strip().encode()).hexdigest()}


def main():
    managed = []
    errors = []
    for root in ROOTS:
        if not root.exists():
            continue
        for file in sorted(root.rglob("SKILL.md")):
            try:
                managed.append({**metadata(file, allow_plaintext=True), "source": file.relative_to(HOME).as_posix()})
            except (ValueError, KeyError, yaml.YAMLError) as exc:
                errors.append(str(exc))
    matches = []
    bodies = {}
    for file in sorted((REPO / "skills").rglob("SKILL.md")):
        info = metadata(file)
        identifier = file.parent.relative_to(REPO / "skills").as_posix()
        bodies.setdefault(info["body_sha256"], []).append(identifier)
        for bundle in managed:
            reasons = [key for key in ("name", "file_sha256", "body_sha256") if info[key] == bundle[key]]
            if reasons:
                matches.append({"id": identifier, "managed_source": bundle["source"], "matched": reasons})
    result = {"managed_files_checked": len(managed), "managed_names": sorted({x["name"] for x in managed}),
              "application_matches": matches, "identical_instruction_bodies": [ids for ids in bodies.values() if len(ids) > 1],
              "metadata_errors": errors,
              "limits": "Checks local managed skill roots by registered name, exact file hash and normalized instruction-body hash. Does not infer stock origin from a user skills directory or compare broad semantic capabilities."}
    print(json.dumps(result, indent=2))
    return 1 if matches or errors else 0


if __name__ == "__main__":
    sys.exit(main())
