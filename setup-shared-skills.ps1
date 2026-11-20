[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$UserRoot = [Environment]::GetFolderPath('UserProfile')
)

$ErrorActionPreference = 'Stop'
$repoPath = [IO.Path]::GetFullPath($PSScriptRoot)
$sharedPath = Join-Path $repoPath 'discovery'
$profilePath = [IO.Path]::GetFullPath($UserRoot)
$backupPath = Join-Path $repoPath ('.local-backups\' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$events = [Collections.Generic.List[object]]::new()

if (-not (Test-Path -LiteralPath (Join-Path $sharedPath 'project-skill-router\SKILL.md'))) {
    throw "Shared router missing: $sharedPath"
}
if ($sharedPath.StartsWith($profilePath + '\.codex\skills\', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Keep the repository outside the application skill directories.'
}

function Save-ExistingPath([string]$Path) {
    $resolved = [IO.Path]::GetFullPath($Path)
    if (-not $resolved.StartsWith($profilePath + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to move a path outside the selected user profile: $resolved"
    }
    $relative = $resolved.Substring($profilePath.Length + 1)
    $destination = [IO.Path]::GetFullPath((Join-Path $backupPath $relative))
    if (-not $destination.StartsWith($backupPath + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Backup path escaped its intended directory.'
    }
    New-Item -ItemType Directory -Path (Split-Path $destination -Parent) -Force | Out-Null
    $item = Get-Item -LiteralPath $resolved -Force
    if ($item.Attributes.HasFlag([IO.FileAttributes]::ReparsePoint)) {
        # Never Move-Item a junction across volumes: PowerShell may move its target contents.
        $linkTarget = [string]$item.Target[0]
        if (-not [IO.Path]::IsPathRooted($linkTarget)) { $linkTarget = Join-Path (Split-Path $resolved -Parent) $linkTarget }
        $linkTarget = [IO.Path]::GetFullPath($linkTarget)
        # Save the link description, not a second traversable alias to the full library.
        $destination += '.link.json'
        @{kind='directory-link'; original=$resolved; target=$linkTarget; link_type=$item.LinkType} |
            ConvertTo-Json | Set-Content -LiteralPath $destination -Encoding UTF8
        [IO.Directory]::Delete($resolved) # Non-recursive: remove only the verified directory link.
        $events.Add(@{ original = $resolved; backup = $destination; link_target = $linkTarget })
    } else {
        Move-Item -LiteralPath $resolved -Destination $destination
        $events.Add(@{ original = $resolved; backup = $destination })
    }
    $events | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $backupPath 'restore-map.json') -Encoding UTF8
}

function Connect-SkillRoot([string]$Path) {
    $existing = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if ($existing -and $existing.LinkType -eq 'Junction' -and
        [IO.Path]::GetFullPath([string]$existing.Target[0]).TrimEnd('\') -eq $sharedPath.TrimEnd('\')) {
        Write-Output "Already connected: $Path"
        return
    }
    if ($PSCmdlet.ShouldProcess($Path, "Back up existing path and create a junction to $sharedPath")) {
        if ($existing) { Save-ExistingPath $Path }
        try {
            New-Item -ItemType Directory -Path (Split-Path $Path -Parent) -Force | Out-Null
            New-Item -ItemType Junction -Path $Path -Target $sharedPath | Out-Null
        }
        catch {
            $last = $events | Where-Object { $_.original -eq $Path } | Select-Object -Last 1
            if ($last -and -not (Test-Path -LiteralPath $Path)) {
                if ($last.link_target) {
                    New-Item -ItemType Junction -Path $Path -Target $last.link_target | Out-Null
                } else {
                    Move-Item -LiteralPath $last.backup -Destination $Path
                }
            }
            throw
        }
        Write-Output "Connected: $Path"
    }
}

# Expose only the router globally. The full canonical library stays in skills/.
Connect-SkillRoot (Join-Path $profilePath '.agents\skills')
Connect-SkillRoot (Join-Path $profilePath '.gemini\config\skills')

# Existing older Antigravity installations and the previous sync location.
foreach ($relative in @(
    '.gemini\antigravity\global_skills',
    '.gemini\antigravity-ide\skills',
    '.antigravity-sync\antigravity\global_skills'
)) {
    $path = Join-Path $profilePath $relative
    if (Get-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue) {
        Connect-SkillRoot $path
    }
}

# Remove old user copies from Codex discovery while preserving system skills.
$legacyPath = Join-Path $profilePath '.codex\skills'
if (Test-Path -LiteralPath $legacyPath) {
    foreach ($folder in Get-ChildItem -LiteralPath $legacyPath -Directory -Force) {
        if ($folder.Name -ne '.system' -and (Test-Path -LiteralPath (Join-Path $folder.FullName 'SKILL.md')) -and
            (Test-Path -LiteralPath (Join-Path $repoPath ('skills\' + $folder.Name + '\SKILL.md')))) {
            if ($PSCmdlet.ShouldProcess($folder.FullName, 'Retire old user skill into the local backup')) {
                Save-ExistingPath $folder.FullName
            }
        }
    }
}

if (-not $WhatIfPreference) {
    foreach ($path in @('.agents\skills', '.gemini\config\skills')) {
        $linked = Join-Path $profilePath $path
        if (-not (Test-Path -LiteralPath (Join-Path $linked 'project-skill-router\SKILL.md'))) {
            throw "Link verification failed: $linked"
        }
    }
    if ($events.Count) {
        $events | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $backupPath 'restore-map.json') -Encoding UTF8
        Write-Output "Previous folders preserved in: $backupPath"
    }
    $guidanceTemplate = [IO.File]::ReadAllText((Join-Path $repoPath 'routing\standing-guidance.txt'))
    foreach ($target in @(
        @{Path=(Join-Path $profilePath '.codex\AGENTS.md'); Router=(Join-Path $profilePath '.agents\skills\project-skill-router\SKILL.md')},
        @{Path=(Join-Path $profilePath '.gemini\GEMINI.md'); Router=(Join-Path $profilePath '.gemini\config\skills\project-skill-router\SKILL.md')}
    )) {
        $startMarker = '<!-- BEGIN shared-skill-routing -->'
        $endMarker = '<!-- END shared-skill-routing -->'
        $existingText = if (Test-Path -LiteralPath $target.Path) { [IO.File]::ReadAllText($target.Path) } else { '' }
        $block = $startMarker + "`n" + $guidanceTemplate.Replace('{ROUTER}', $target.Router.Replace('\', '/')).Trim() + "`n" + $endMarker
        if ($existingText.Contains($startMarker) -and $existingText.Contains($endMarker)) {
            $begin = $existingText.IndexOf($startMarker)
            $finish = $existingText.IndexOf($endMarker) + $endMarker.Length
            $updatedText = $existingText.Substring(0, $begin) + $block + $existingText.Substring($finish)
        } else {
            $updatedText = $existingText.TrimEnd() + "`n`n" + $block + "`n"
        }
        if ($existingText -ne $updatedText) {
            if (Test-Path -LiteralPath $target.Path) {
                $relative = $target.Path.Substring($profilePath.Length + 1)
                $backupTarget = Join-Path $backupPath $relative
                New-Item -ItemType Directory -Path (Split-Path $backupTarget -Parent) -Force | Out-Null
                Copy-Item -LiteralPath $target.Path -Destination $backupTarget
            }
            New-Item -ItemType Directory -Path (Split-Path $target.Path -Parent) -Force | Out-Null
            [IO.File]::WriteAllText($target.Path, $updatedText, [Text.UTF8Encoding]::new($false))
        }
    }
    Write-Output 'Both tools now discover only the shared router globally; standing guidance installed for future projects.'
    Write-Output 'The complete library remains available through the router. Restart both applications.'
}
