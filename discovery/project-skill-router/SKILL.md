---
name: project-skill-router
description: Select a small set of skills from the shared library for project work. Use at project start, when the task changes domain, or when a specialist skill is needed; avoid reading the whole library.
---

# Project skill router

The full library is intentionally outside global skill discovery. Start here rather than enumerating every SKILL.md. Routine questions and simple edits may need no specialist skills.

Use the script beside this skill (Python 3.10+). Resolve `<router>` to this skill's base directory, preserving quotes around paths with spaces:

```text
python "<router>/scripts/skills.py" recommend --project "<project>" --task "<current task>"
python "<router>/scripts/skills.py" search "<focused topic>" --limit 6
python "<router>/scripts/skills.py" show <skill-id>
```

The script resolves the shared repository from its own real path, so it works through the application directory links and after cloning on another device. Queries read generated metadata only. `show` returns the canonical instruction path: read that SKILL.md and only the supporting references needed for the current work. Host instructions and project conventions remain authoritative.

For actual project implementation, expose a small project-specific selection when useful:

```text
python "<router>/scripts/skills.py" use --project "<project>" --profile web
python "<router>/scripts/skills.py" use --project "<project>" --profile web --apply
python "<router>/scripts/skills.py" use --project "<project>" --skill <skill-id> --apply
```

The first command previews. `--apply` adds links to the canonical folders under the project's `.agents/skills`, used by both apps, without copying skills. With no profile/skill arguments it restores that project's saved selection. Existing selections are extended by default; add `--replace` when intentionally switching the managed selection to a different task. Unmanaged project skills are preserved. Newly exposed skills may require a new conversation or app reload; read their canonical files directly for the current turn.

Choose the minimum set that changes the result, normally 1–5 skills plus necessary dependencies. Add specialist skills as the task reaches them; do not activate whole categories. Profile choices are starting points, not permission to expand the task. Check available tools before relying on an MCP connection or external program. Use project fingerprints and the user's request; preserve their chosen stack. Unity, Godot and Roblox are excluded by user preference.

`profiles` lists starter sets; `categories` lists category counts. `catalog/INDEX.txt` in the shared repository is the small human entry point, with focused indexes in `catalog/categories/`. Prefer bounded `search` results to reading whole category indexes. If the catalog is stale after installing/removing skills, run `build` once; it requires PyYAML. Selection, search and profile restoration need only the Python standard library.

Install new shared skills into the canonical `skills/` directory and rebuild the catalog rather than adding whole packs to global discovery. If Python is unavailable, follow the directory link to the shared repository, read `catalog/INDEX.txt` and one relevant category index, then open only the selected `skills/<id>/SKILL.md` files.

This is an additional-skills collection, not a mirror of application defaults. Follow `library-policy.json`: exclude application-managed system/builtin/plugin skills, review origins and creative/development scope before approving new IDs, and retain one maintained version. Use native/bundled capabilities directly when they already cover the task rather than copying their instructions into this library.
