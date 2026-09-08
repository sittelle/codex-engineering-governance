param(
    [string]$GovernanceRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" })
)

$ErrorActionPreference = "Stop"

$GovernanceRoot = (Resolve-Path $GovernanceRoot).Path
$Kernel = Join-Path $GovernanceRoot "codex-home\AGENTS.md"
$VersionFile = Join-Path $GovernanceRoot "VERSION"

if (-not (Test-Path $Kernel)) {
    throw "Governance kernel not found: $Kernel"
}
if (-not (Test-Path $VersionFile)) {
    throw "Governance VERSION not found: $VersionFile"
}

New-Item -ItemType Directory -Force $CodexHome | Out-Null

$TargetAgents = Join-Path $CodexHome "AGENTS.md"
$Locator = Join-Path $CodexHome "GOVERNANCE_ROOT"

if (Test-Path $TargetAgents) {
    $Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $Backup = "$TargetAgents.backup-$Timestamp"
    Copy-Item $TargetAgents $Backup
    Write-Host "Backed up existing AGENTS.md to $Backup"
}

Copy-Item $Kernel $TargetAgents -Force
Set-Content -Path $Locator -Value $GovernanceRoot -NoNewline -Encoding UTF8

$Version = (Get-Content -Raw $VersionFile).Trim()

Write-Host ""
Write-Host "Installed Codex engineering governance $Version"
Write-Host "AGENTS.md:       $TargetAgents"
Write-Host "GOVERNANCE_ROOT: $Locator"
Write-Host "Governance repo: $GovernanceRoot"
Write-Host ""
Write-Host "Start a fresh Codex session after installation."
