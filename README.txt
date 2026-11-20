SHARED CODEX + ANTIGRAVITY SKILLS

One editable collection is stored in skills/. Both applications read those same
files through Windows directory junctions; there are no separate active copies.

This PC is connected as follows:
  %USERPROFILE%/.agents/skills                    -> this repository/skills
  %USERPROFILE%/.gemini/config/skills             -> this repository/skills
Existing legacy Antigravity global_skills, antigravity-ide/skills and the old
.antigravity-sync skills folder are also connected to this same directory.
The existing .gemini/antigravity/skills alias follows the config/skills link.
Codex's managed .codex/skills/.system folder remains application-managed.
Previous Codex user copies have been retired from the discovery location.

DAILY USE
Edit, add, or remove skills in skills/. Both apps see the same files.
Restart the apps after setup. If a new skill is not visible, reload/restart.
Keep this repository in its present location after connecting it. If you move
or rename the repository, run setup-shared-skills.ps1 from its new location.
External APIs, MCP tools, credentials and programs required by individual skills
must still be installed/configured in each application and on each device.
Shared discovery does not prove every workflow runs in both applications.

GITHUB SYNC
1. GitHub repository: https://github.com/skdsam/ai-skills
   This local folder is configured with that repository as origin.
   For reference, the initial publication commands are:
   From this folder, for a new empty remote repository:
     git init -b main
     git add .
     git commit -m "Add shared Codex and Antigravity skills"
     git remote add origin https://github.com/skdsam/ai-skills.git
     git push -u origin main
2. On the other Windows PC, clone the repository into a stable local folder:
     git clone https://github.com/skdsam/ai-skills.git
     cd ai-skills
   If that PC already has additional skills, collect/reconcile them first using
   collect-skills.py before running setup. Existing versions will be preserved.
3. In PowerShell from the cloned folder, run:
     .\setup-shared-skills.ps1 -WhatIf
     .\setup-shared-skills.ps1
   The setup script uses the current Windows user profile and clone location.
   Junctions are created locally on each device; Git does not transfer them.
4. Restart Codex and Antigravity on that PC.
5. After editing skills on either PC:
     git add skills archive metadata-adjustments.json skill-sources.json
     git commit -m "Update shared skills"
     git push
   On the other PC, before editing:
     git pull --ff-only
   Review and commit local changes before pulling. Diverging edits need a normal
   Git merge. Sync is manual when needed, not a background service.

ARCHIVES AND BACKUPS
archive/variants contains 18 differing versions from the original collections.
These are kept outside skills/ so applications do not discover duplicate versions.
archive/metadata-originals preserves original SKILL.md text for 13 discovery
metadata repairs. metadata-adjustments.json lists those repairs. Distinct skills
that shared discovery names now have unique names; imagen's description is fixed.
skill-sources.json records original sources and selected destinations. Its hashes
record the original imports, before the listed metadata adjustments.
.local-backups/ contains previous installation folders and restore maps. These
are recovery snapshots, not active skills, and are excluded from Git. Retained
pre-existing Gemini backups also remain untouched. Do not routinely edit backups.
The detailed skill-inventory.local.json is also excluded from Git.
Do not sync entire account/configuration folders or credentials.

VERIFICATION (20 November 2026)
1,273 primary folders have nonempty names/descriptions and unique discovery names.
Codex app-server skills/list loaded all 1,273, plus nested skills, with zero errors.
All five connected user skill directories resolve to this repository's skills/.
Antigravity in-app discovery needs checking after restarting the application.
Setup was checked with an isolated profile, WhatIf and repeated execution.

REFERENCES
https://learn.chatgpt.com/docs/build-skills
https://antigravity.google/docs/skills

GITHUB ADDITIONS (20 November 2026)
363 missing skills added from 17 upstream collections. See
SKILL-ADDITIONS-2026-11-20.txt for the selection, sources and dependencies.
github-skill-imports-2026-11-20.json pins revisions and records compatibility edits.
github-skill-research-2026-11-20.json records repository stars and weekly trending.
third-party-notices/ retains upstream licenses and attribution.
