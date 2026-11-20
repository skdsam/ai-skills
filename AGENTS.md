# Shared skills library

Keep one canonical skill collection in `skills/`. Both apps globally discover only the router in `discovery/`; do not link the whole library into global discovery. Project selections link only relevant canonical folders under each project's `.agents/skills`.

Use `discovery/project-skill-router/scripts/skills.py` for bounded search, project recommendations and project-local selections. Regenerate the catalog with its `build` command after importing, editing metadata or removing skills. Do not run the global installer merely to add another library skill.

Do not add skills dedicated to Unity, Godot or Roblox, including engine-specific Blender exporters. The user does not use these engines. Follow `skill-exclusions.json` when collecting or importing skills. Keep Unreal Engine and engine-neutral skills.

Preserve upstream licenses, source revisions and local compatibility changes when importing skills. Keep machine-specific recovery backups out of Git.

This collection is additional, focused material only. Follow `library-policy.json`: never copy application-managed system, builtin or plugin skills here. Verify origins; a user-installed skill is not necessarily bundled. Restrict new imports to the approved creative/development areas and add their reviewed IDs to the policy. Keep one maintained version and use Git history for older versions; do not rebuild an archive of duplicate skill folders.
