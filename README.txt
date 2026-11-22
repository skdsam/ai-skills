SHARED SKILLS WITH SELECTIVE PROJECT ROUTING

One canonical library, available to Codex and Antigravity.
488 primary additional skills remain in skills/ (498 catalog entries including nested skills).
Only project-skill-router is globally discoverable. The complete library stays
available through bounded metadata search and selected canonical instruction files.

LAYOUT
  skills/          Full canonical skill folders and shared resources; no copies per app.
  discovery/       One small globally discovered router skill.
  catalog/INDEX.txt Small entry point, category indexes and starter profile definitions.
  catalog/skills.json Generated searchable names, descriptions, paths and dependencies.
  routing/         Standing guidance installed for both applications.
  third-party-notices/ Upstream licenses and source revisions.
  .local-backups/  Machine-specific recovery files; excluded from Git.

HOW IT WORKS
The application's global skills directory points to discovery/, not skills/.
The router uses the current project and task to choose a small set. It queries
catalog metadata without reading the full instruction library. The agent then
reads only the selected SKILL.md files and references needed for that task.
For implementation, it can create project-local directory links under
<project>/.agents/skills, a location supported by both applications. Typically
1-5 relevant skills are selected, with necessary dependencies. Specialized skills
can be added when needed; ordinary questions and simple edits can need none.
The full library remains stored once. Existing project-owned skills are preserved.

This PC's global Codex and Antigravity skill locations now point to discovery/.
Legacy Antigravity skill locations have been redirected too. Managed system skills,
plugins, MCP tools and existing Blender packaging preferences are retained.
Standing instructions in ~/.codex/AGENTS.md and ~/.gemini/GEMINI.md make routing
the default for future project work. This is persistent application guidance,
not a modification to a model. Restart the apps/new conversations to refresh
previously loaded catalogs. Old conversations may retain their previous metadata.

COMMANDS (PowerShell, Python 3.10+)
Set a convenient variable in your current shell:
  $router = "$env:USERPROFILE/.agents/skills/project-skill-router/scripts/skills.py"

Preview a task recommendation; nothing is written:
  python $router recommend --project "D:/Projects/MyProject" --task "Build a JUCE effect"

Search a focused topic; output is bounded:
  python $router search "Unreal Niagara" --limit 6
  python $router search "JUCE DSP" --category audio --limit 4
  python $router show juce-guide

Choose a starter profile and preview before applying:
  python $router use --project "D:/Projects/MyProject" --profile juce
  python $router use --project "D:/Projects/MyProject" --profile juce --apply

Add a specialist when it becomes relevant:
  python $router use --project "D:/Projects/MyProject" --skill juce-ui-fidelity --apply

Switch the managed selection to a different task:
  python $router use --project "D:/Projects/MyProject" --profile web --replace --apply

Restore a project's saved selection after cloning on another device:
  python $router use --project "D:/Projects/MyProject" --apply

Starter profiles: general, blender, blender-addon, web, react, threejs, unreal,
juce, audio, browser. Multiple --profile or --skill options can be used.
Profiles are small starting sets, not full-category activation. The generic profile
can contain no skills. Project fingerprints preserve the chosen stack; recommendations
are heuristics and can be overridden with explicit profiles or skill IDs.

PROJECT STATE
<project>/.agents/skill-profile.json stores portable profile/skill IDs and can be
committed with that project's code. <project>/.agents/.skill-links.local.json
records machine-local link targets and is ignored. Generated links are ignored
individually in .agents/skills/.gitignore; project-authored skills remain visible
to Git. --replace removes only verified links managed by this tool, never their
canonical targets or unrelated project skill directories.

GITHUB / SECOND WINDOWS PC
Repository: https://github.com/skdsam/ai-skills
1. Clone or pull this repository into a stable local folder.
2. Reconcile any skills unique to that device into skills/ first; the collector
   can help before switching discovery. From this folder, run
   .\setup-shared-skills.ps1 (preview: add -WhatIf).
   This installs global router links and the standing guidance on that device,
   preserving existing preferences and backing up displaced paths/configuration.
3. If browser tooling is wanted, run .\setup-google-browser-tools.ps1.
4. Restart Codex and Antigravity. Restore any project skill profiles as above.
5. Commit and push library changes on the device where you edited them; pull on
   the other device before editing. Sync is manual when needed.
Junctions, application accounts, credentials and local runtime configurations are
not transferred by Git. If the repository moves, rerun setup-shared-skills.ps1.
The installer replaces links themselves without moving their target contents.

ADDING OR REMOVING LIBRARY SKILLS
Review new skills against library-policy.json and the local managed inventory.
Approve only non-bundled skills within the listed creative/development areas,
add reviewed IDs to approved_primary_ids, and preserve licenses/provenance.
Import the canonical folders into skills/, then:
  python discovery/project-skill-router/scripts/skills.py build
Catalog rebuilding requires PyYAML (python -m pip install -r catalog/requirements-build.txt).
Normal search, recommendations and project selection use only the standard library.
The generated catalog is committed, so another PC does not need to rebuild on pull.
Rebuilds also audit current local system/builtin/plugin skills and reject copied
managed names, matching instruction files/bodies, and unapproved folders.
Run python tools/audit-library.py for the standalone read-only audit.
An existing user-installed skill is not automatically an application-bundled skill.
The collector skips unapproved/bundled material and alternate versions; old
versions are retained in Git history rather than duplicate archive folders.
collect-skills.py uses the canonical library, skips the discovery links and rebuilds
after new imports. Do not install large packs into the global discovery directory.
Unity, Godot and Roblox are excluded by the user's preference; Unreal remains.

GOOGLE BROWSER TOOLS
Chrome DevTools MCP 1.13.0 and Modern Web Guidance 1.0.1 are installed on this PC.
Their instruction skills are in the catalog and can be selected per project.
The Chrome MCP connection remains configured in both applications independently
of skill discovery. It uses headless Chrome with isolated temporary profiles;
usage statistics and CrUX trace-URL lookups are disabled. Modern Web Guidance is
a command-line skill rather than a second MCP server. On another device, run
setup-google-browser-tools.ps1 after installing Node.js/npm and Chrome.

VALIDATION AND LIMITS
ROUTING-VERIFICATION.json records fresh Codex runtime discovery before/after and
example web/JUCE project selections. Original broad-library baseline: 1,255 skills globally exposed;
after: one router. Their name/description metadata fell from 339,918 to 213
characters before adding a project's selection. These are characters, not token
counts or total-context measurements. Built-ins, plugins and MCP tools retain
their own overhead. Antigravity links and documented discovery paths were checked;
its in-app refresh requires restarting. Ten routing/policy tests cover profile changes,
read-only previews, conflict preservation, clone restoration and Windows cross-drive
junction safety. All retained canonical skill instruction hashes are unchanged.
  python -m unittest discover -s tests -v
Shared discovery does not prove every third-party workflow runs in both apps.
External tools, credentials, SDKs and models required by a skill still need setup.

PROVENANCE
skill-sources.json: original consolidated sources, with removed entries marked.
github-skill-imports-2026-11-20.json: imported revisions and compatibility edits.
github-skill-research-2026-11-20.json: popularity/trending research snapshot.
google-browser-skills.json: Google browser skill revisions and runtime versions.
SKILL-ADDITIONS-2026-11-20.txt: historical additions and dependency notes.

OFFICIAL DISCOVERY REFERENCES
https://learn.chatgpt.com/docs/build-skills
https://antigravity.google/docs/skills
https://antigravity.google/docs/rules

ADDITIONAL-ONLY CURATION
The collection is focused on 3D, Blender, Three.js, Google/browser tools, UI/UX,
web design, audio/JUCE, Unreal, games and related creative/interface helpers.
787 unrelated primary skill folders, 18 old archived variants, and one identical
nested Blender copy were removed. legal-advisor was third-party user-installed
material and was removed as outside scope, not mislabeled as an app default.
The final audit checked 63 managed instruction files and found no name, exact-file
or normalized-body matches; no identical retained instruction bodies remain.
LIBRARY-AUDIT.json records the cleanup and library-policy.json limits future imports.
Application-owned system/builtin/plugin files were not modified.
Recovery copies and research downloads are excluded from GitHub. Relocatable
material is in the ai-skills-recovery directory beside this repository; Windows-
locked recovery folders remain in the ignored .local-backups directory. Neither
location is scanned as the installed skill library.
Local backup filenames remain ignored for future setup/maintenance operations.
Historical source manifests can mention removed skills with an explicit status;
only the current catalog and approved skill folders represent installed extras.
