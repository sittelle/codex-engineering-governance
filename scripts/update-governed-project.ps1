param(
    [string]$ProjectRoot,
    [switch]$Apply,
    [switch]$AllowDirtyGit
)

$ErrorActionPreference = "Stop"

function Fail([string]$Message) {
    Write-Error $Message
    exit 1
}

$GovernanceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$CentralVersion = (Get-Content -Raw (Join-Path $GovernanceRoot "VERSION")).Trim()

if (-not $ProjectRoot) {
    $ProjectRoot = Read-Host "Enter governed project root"
}
if (-not $ProjectRoot) {
    Fail "Project root is required."
}

try {
    $ProjectRoot = (Resolve-Path $ProjectRoot).Path
} catch {
    Fail "Project root does not exist: $ProjectRoot"
}

$Manifest = Join-Path $ProjectRoot "project-governance.yml"
$Agents = Join-Path $ProjectRoot "AGENTS.md"

if (-not (Test-Path $Manifest)) {
    Fail "Not a governed project: project-governance.yml not found in $ProjectRoot"
}
if (-not (Test-Path $Agents)) {
    Fail "Not a governed project: AGENTS.md not found in $ProjectRoot"
}

$ManifestText = Get-Content -Raw $Manifest
$BaselineMatch = [regex]::Match($ManifestText, '(?m)^\s*baseline:\s*["'']?([^"'']+)["'']?\s*$')
if (-not $BaselineMatch.Success) {
    Fail "Could not find governance baseline in project-governance.yml"
}
$ProjectVersion = $BaselineMatch.Groups[1].Value.Trim()

$GitDir = Join-Path $ProjectRoot ".git"
if (Test-Path $GitDir) {
    $Dirty = git -C $ProjectRoot status --porcelain
    if ($LASTEXITCODE -ne 0) {
        Fail "git status failed for $ProjectRoot"
    }
    if ($Dirty -and -not $AllowDirtyGit) {
        Fail "Git worktree is dirty. Commit/stash changes first, or rerun with -AllowDirtyGit after deliberate review."
    }
}

$Begin = "<!-- BEGIN CODEX-GOVERNANCE-MANAGED -->"
$End = "<!-- END CODEX-GOVERNANCE-MANAGED -->"
$TemplateAgents = Join-Path $GovernanceRoot "templates\repository\AGENTS.md"
if (-not (Test-Path $TemplateAgents)) {
    Fail "Managed AGENTS template not found: $TemplateAgents"
}
$TemplateAgentsText = Get-Content -Raw $TemplateAgents
$EscBegin = [regex]::Escape($Begin)
$EscEnd = [regex]::Escape($End)
$ManagedMatch = [regex]::Match($TemplateAgentsText, "(?s)$EscBegin.*?$EscEnd")
if (-not $ManagedMatch.Success) {
    Fail "Managed AGENTS block not found in template: $TemplateAgents"
}
$ManagedBlock = $ManagedMatch.Value

# Build migrated manifest conservatively.
$NewManifest = $ManifestText
$NewManifest = [regex]::Replace(
    $NewManifest,
    '(?m)^(\s*baseline:\s*)["'']?[^"'']+["'']?\s*$',
    ('${1}"' + $CentralVersion + '"'),
    1
)

if ($NewManifest -notmatch '(?m)^\s*source:\s*') {
    $NewManifest = [regex]::Replace(
        $NewManifest,
        '(?m)^(\s*baseline:\s*["''][^"'']+["'']\s*)$',
        '$1' + "`r`n  source: `"codex-home-locator`"",
        1
    )
}
if ($NewManifest -notmatch '(?m)^\s*locator:\s*') {
    if ($NewManifest -match '(?m)^\s*source:\s*') {
        $NewManifest = [regex]::Replace(
            $NewManifest,
            '(?m)^(\s*source:\s*.+)$',
            '$1' + "`r`n  locator: `"`$CODEX_HOME/GOVERNANCE_ROOT`"",
            1
        )
    }
}

$TechnologyBaselineAdded = $false
if ($NewManifest -notmatch '(?m)^technology_baseline:\s*$') {
    $TechnologyBaselineBlock = @'
# Governed architecture-significant technology state.
# Added during legacy governance migration; reconcile before treating the historical stack as established.
technology_baseline:
  state: "RECONCILIATION_REQUIRED"
  record: "docs/design.md#technology-baseline"
'@
    if ($NewManifest -match '(?m)^platforms:\s*$') {
        $NewManifest = [regex]::Replace(
            $NewManifest,
            '(?m)^platforms:\s*$',
            ($TechnologyBaselineBlock.TrimEnd() + "`r`n`r`nplatforms:"),
            1
        )
    } else {
        $NewManifest = $NewManifest.TrimEnd() + "`r`n`r`n" + $TechnologyBaselineBlock.TrimEnd() + "`r`n"
    }
    $TechnologyBaselineAdded = $true
}

$AgentsText = Get-Content -Raw $Agents

if ($AgentsText -match "(?s)$EscBegin.*?$EscEnd") {
    $NewAgents = [regex]::Replace($AgentsText, "(?s)$EscBegin.*?$EscEnd", $ManagedBlock.TrimEnd(), 1)
    $AgentsMode = "refresh managed block"
} else {
    $NewAgents = $AgentsText.TrimEnd() + "`r`n`r`n" + $ManagedBlock.TrimEnd() + "`r`n"
    $AgentsMode = "append managed block"
}

Write-Host ""
Write-Host "Governed project update preview"
Write-Host "Project:          $ProjectRoot"
Write-Host "Project baseline: $ProjectVersion"
Write-Host "Target baseline:  $CentralVersion"
Write-Host "AGENTS action:    $AgentsMode"
Write-Host ""
Write-Host "Will update:"
Write-Host "  - project-governance.yml: baseline/source/locator"
if ($TechnologyBaselineAdded) {
    Write-Host "  - project-governance.yml: add missing Technology Baseline as RECONCILIATION_REQUIRED"
} else {
    Write-Host "  - project-governance.yml: preserve existing Technology Baseline"
}
Write-Host "  - AGENTS.md: central managed block only"
Write-Host ""
Write-Host "Will NOT update:"
Write-Host "  - requirements/design/security/ADRs/risks"
Write-Host "  - maturity or assurance"
Write-Host "  - verification commands"
Write-Host "  - an existing project-owned Technology Baseline"
Write-Host "  - project-specific AGENTS instructions"
Write-Host ""

if (-not $Apply) {
    Write-Host "DRY RUN ONLY. Re-run with -Apply to make these changes."
    exit 0
}

$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
Copy-Item $Manifest "$Manifest.governance-backup-$Stamp"
Copy-Item $Agents "$Agents.governance-backup-$Stamp"

Set-Content -Path $Manifest -Value $NewManifest.TrimEnd() -Encoding UTF8
Set-Content -Path $Agents -Value $NewAgents.TrimEnd() -Encoding UTF8

Write-Host "Applied governance update to $CentralVersion"
Write-Host "Backups:"
Write-Host "  $Manifest.governance-backup-$Stamp"
Write-Host "  $Agents.governance-backup-$Stamp"
Write-Host ""
Write-Host "Review with:"
Write-Host "  git -C `"$ProjectRoot`" diff -- AGENTS.md project-governance.yml"
Write-Host ""
Write-Host "Then commit the governance migration separately if correct."
