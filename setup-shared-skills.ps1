[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$UserRoot = [Environment]::GetFolderPath('UserProfile')
)

$ErrorActionPreference = 'Stop'
$repoPath = [IO.Path]::GetFullPath($PSScriptRoot)
$sharedPath = Join-Path $repoPath 'skills'
$profilePath = [IO.Path]::GetFullPath($UserRoot)
$backupPath = Join-Path $repoPath ('.local-backups\' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$events = [Collections.Generic.List[object]]::new()

if (-not (Test-Path -LiteralPath $sharedPath -PathType Container)) {
    throw "Shared skills folder missing: $sharedPath"
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
    Move-Item -LiteralPath $resolved -Destination $destination
    $events.Add(@{ original = $resolved; backup = $destination })
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
                Move-Item -LiteralPath $last.backup -Destination $Path
            }
            throw
        }
        Write-Output "Connected: $Path"
    }
}

# Codex's documented user location; application-managed .system stays in .codex.
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
        if ($folder.Name -ne '.system' -and (Test-Path -LiteralPath (Join-Path $folder.FullName 'SKILL.md'))) {
            if ($PSCmdlet.ShouldProcess($folder.FullName, 'Retire old user skill into the local backup')) {
                Save-ExistingPath $folder.FullName
            }
        }
    }
}

if (-not $WhatIfPreference) {
    foreach ($path in @('.agents\skills', '.gemini\config\skills')) {
        $linked = Join-Path $profilePath $path
        if (-not (Test-Path -LiteralPath (Join-Path $linked 'blender-core\SKILL.md'))) {
            throw "Link verification failed: $linked"
        }
    }
    if ($events.Count) {
        $events | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $backupPath 'restore-map.json') -Encoding UTF8
        Write-Output "Previous folders preserved in: $backupPath"
    }
    Write-Output 'Both tools now read the shared skills folder. Restart both applications.'
}
