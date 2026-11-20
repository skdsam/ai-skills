[CmdletBinding()]
param([switch]$SkipPackageInstall)

$ErrorActionPreference = 'Stop'
$profilePath = [Environment]::GetFolderPath('UserProfile')
$backupPath = Join-Path $PSScriptRoot ('.local-backups\google-browser-tools-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))

if (-not $SkipPackageInstall) {
    & npm.cmd install --global --ignore-scripts --no-audit --no-fund chrome-devtools-mcp@1.13.0 modern-web-guidance@1.0.1
    if ($LASTEXITCODE -ne 0) { throw 'npm package installation failed.' }
}
$nodePath = (Get-Command node.exe -ErrorAction Stop).Source
$npmRoot = (& npm.cmd root --global | Select-Object -Last 1).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Cannot locate the global npm packages.' }
$serverPath = Join-Path $npmRoot 'chrome-devtools-mcp\out\Default\gen\src\bin\chrome-devtools-mcp.js'
if (-not (Test-Path -LiteralPath $serverPath)) { throw "Chrome DevTools runtime missing: $serverPath" }
$serverArgs = @($serverPath, '--headless', '--isolated', '--no-usage-statistics', '--no-performance-crux')

function Backup-Config([string]$Path, [string]$Name) {
    if (Test-Path -LiteralPath $Path) {
        New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
        Copy-Item -LiteralPath $Path -Destination (Join-Path $backupPath $Name)
    }
}

$codexPath = Join-Path $profilePath '.codex\config.toml'
$codexText = if (Test-Path -LiteralPath $codexPath) { [IO.File]::ReadAllText($codexPath) } else { '' }
if ($codexText -match '(?m)^\[mcp_servers\.(?:chrome-devtools|"chrome-devtools")\]') {
    Write-Output 'Codex already has chrome-devtools configured; existing settings retained.'
} else {
    Backup-Config $codexPath 'codex-config.toml'
    New-Item -ItemType Directory -Path (Split-Path $codexPath -Parent) -Force | Out-Null
    $nodeToml = ConvertTo-Json -InputObject $nodePath -Compress
    $argsToml = ConvertTo-Json -InputObject $serverArgs -Compress
    $section = "`n[mcp_servers.chrome-devtools]`ncommand = $nodeToml`nargs = $argsToml`nstartup_timeout_sec = 60`n"
    [IO.File]::WriteAllText($codexPath, $codexText + $section, [Text.UTF8Encoding]::new($false))
    Write-Output 'Configured Chrome DevTools for Codex.'
}

$antigravityConfigs = @((Join-Path $profilePath '.gemini\config\mcp_config.json'))
$legacyIdeConfig = Join-Path $profilePath '.gemini\antigravity-ide\mcp_config.json'
if (Test-Path -LiteralPath $legacyIdeConfig) { $antigravityConfigs += $legacyIdeConfig }
foreach ($configPath in $antigravityConfigs) {
    $config = if (Test-Path -LiteralPath $configPath) { Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json } else { [pscustomobject]@{} }
    if (-not $config.PSObject.Properties['mcpServers']) {
        $config | Add-Member -NotePropertyName mcpServers -NotePropertyValue ([pscustomobject]@{})
    }
    if ($config.mcpServers.PSObject.Properties['chrome-devtools']) {
        Write-Output "Chrome DevTools already configured; existing settings retained: $configPath"
        continue
    }
    $backupName = if ($configPath -eq $legacyIdeConfig) { 'antigravity-ide-mcp.json' } else { 'antigravity-mcp.json' }
    Backup-Config $configPath $backupName
    $config.mcpServers | Add-Member -NotePropertyName 'chrome-devtools' -NotePropertyValue ([pscustomobject]@{command=$nodePath; args=$serverArgs})
    New-Item -ItemType Directory -Path (Split-Path $configPath -Parent) -Force | Out-Null
    $json = ConvertTo-Json -InputObject $config -Depth 50
    [IO.File]::WriteAllText($configPath, $json + "`n", [Text.UTF8Encoding]::new($false))
    Write-Output "Configured Chrome DevTools for Antigravity: $configPath"
}
Write-Output 'Google browser tools configured. Restart Codex and Antigravity to load the MCP tools.'
