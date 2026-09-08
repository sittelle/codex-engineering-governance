param(
    [ValidateSet("New","Adopt")] [string]$Mode,
    [string]$ParentRoot,
    [string]$ProjectName,
    [string]$ProjectRoot,
    [switch]$Apply,
    [switch]$NoGitInit,
    [switch]$AllowDirtyGit
)

$ErrorActionPreference = "Stop"
function Fail([string]$Message) { Write-Error $Message; exit 1 }

$GovernanceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Version = (Get-Content -Raw (Join-Path $GovernanceRoot "VERSION")).Trim()
$TemplateRoot = Join-Path $GovernanceRoot "templates\repository"
$Begin = "<!-- BEGIN CODEX-GOVERNANCE-MANAGED -->"
$End = "<!-- END CODEX-GOVERNANCE-MANAGED -->"
$TemplateAgentsPath = Join-Path $TemplateRoot "AGENTS.md"
$TemplateAgentsText = Get-Content -Raw $TemplateAgentsPath
$ManagedPattern = "(?s)$([regex]::Escape($Begin)).*?$([regex]::Escape($End))"
$ManagedMatch = [regex]::Match($TemplateAgentsText, $ManagedPattern)
if (-not $ManagedMatch.Success) { Fail "Managed AGENTS block not found in template: $TemplateAgentsPath" }
$ManagedBlock = $ManagedMatch.Value

if (-not $Mode) {
    Write-Host "1) Create a new governed project"
    Write-Host "2) Adopt an existing ungoverned project"
    $choice = Read-Host "Choose 1 or 2"
    if ($choice -eq "1") { $Mode = "New" }
    elseif ($choice -eq "2") { $Mode = "Adopt" }
    else { Fail "Invalid choice." }
}

if ($Mode -eq "New") {
    if (-not $ParentRoot) { $ParentRoot = Read-Host "Parent folder" }
    if (-not $ProjectName) { $ProjectName = Read-Host "Project name" }
    if (-not $ParentRoot -or -not $ProjectName) { Fail "ParentRoot and ProjectName are required." }
    if ($ProjectName -match '[\\/:*?"<>|]') { Fail "ProjectName contains invalid Windows filename characters." }

    try { $ParentRoot = (Resolve-Path $ParentRoot).Path }
    catch { Fail "Parent folder does not exist: $ParentRoot" }

    $Target = Join-Path $ParentRoot $ProjectName
    if (Test-Path $Target) {
        if (@(Get-ChildItem -Force $Target).Count -gt 0) {
            Fail "Target exists and is not empty: $Target. Use -Mode Adopt."
        }
    }

    Write-Host ""
    Write-Host "NEW governed project preview"
    Write-Host "Target:             $Target"
    Write-Host "Governance version: $Version"
    Write-Host "Git init:           $(-not $NoGitInit)"
    Write-Host "No application code will be generated."

    if (-not $Apply) {
        Write-Host "DRY RUN ONLY. Re-run with -Apply."
        exit 0
    }

    New-Item -ItemType Directory -Force $Target | Out-Null
    foreach ($d in @("docs","src","tests")) {
        New-Item -ItemType Directory -Force (Join-Path $Target $d) | Out-Null
    }

    Copy-Item (Join-Path $TemplateRoot "AGENTS.md") (Join-Path $Target "AGENTS.md")
    Copy-Item (Join-Path $TemplateRoot "project-governance.yml") (Join-Path $Target "project-governance.yml")
    $verificationPlan = Join-Path $TemplateRoot "verification-plan.json"
    if (Test-Path $verificationPlan) { Copy-Item $verificationPlan (Join-Path $Target "verification-plan.json") }
    foreach ($name in @(".editorconfig",".gitignore")) {
        $source = Join-Path $TemplateRoot $name
        if (Test-Path $source) { Copy-Item $source (Join-Path $Target $name) }
    }
    $design = Join-Path $TemplateRoot "docs\design.md"
    if (Test-Path $design) { Copy-Item $design (Join-Path $Target "docs\design.md") }

    $manifest = Join-Path $Target "project-governance.yml"
    $m = Get-Content -Raw $manifest
    $m = [regex]::Replace($m, '(?m)^(\s*name:\s*).+$', ('${1}"' + $ProjectName + '"'), 1)
    Set-Content $manifest $m.TrimEnd() -Encoding UTF8

    if (-not $NoGitInit) {
        git -C $Target init | Out-Null
        if ($LASTEXITCODE -ne 0) { Fail "Project created, but git init failed." }
    }

    Write-Host "Created governed project: $Target"
    Write-Host "Next: open it in Codex and start the new-project workflow. Do not create an approved-design commit until design is actually approved."
    exit 0
}

if ($Mode -eq "Adopt") {
    if (-not $ProjectRoot) { $ProjectRoot = Read-Host "Existing project root" }
    if (-not $ProjectRoot) { Fail "ProjectRoot is required." }
    try { $ProjectRoot = (Resolve-Path $ProjectRoot).Path }
    catch { Fail "Project root does not exist: $ProjectRoot" }

    if (Test-Path (Join-Path $ProjectRoot "project-governance.yml")) {
        Fail "This project is already governed. Use update-governed-project.ps1."
    }

    $GitPresent = Test-Path (Join-Path $ProjectRoot ".git")
    if ($GitPresent) {
        $dirty = git -C $ProjectRoot status --porcelain
        if ($LASTEXITCODE -ne 0) { Fail "git status failed." }
        if ($dirty -and -not $AllowDirtyGit) {
            Fail "Git worktree is dirty. Commit/stash first, or rerun with -AllowDirtyGit after deliberate review."
        }
    }

    Write-Host ""
    Write-Host "ADOPT governance preview"
    Write-Host "Project:            $ProjectRoot"
    Write-Host "Governance version: $Version"
    Write-Host "Git present:        $GitPresent"
    Write-Host "Existing project content will be preserved."
    Write-Host "Adoption state will be RECONCILIATION_REQUIRED."

    if (-not $Apply) {
        Write-Host "DRY RUN ONLY. Re-run with -Apply."
        exit 0
    }

    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $agents = Join-Path $ProjectRoot "AGENTS.md"

    if (Test-Path $agents) {
        Copy-Item $agents "$agents.governance-backup-$stamp"
        $a = Get-Content -Raw $agents
        if ($a -match $ManagedPattern) {
            $newAgents = [regex]::Replace($a, $ManagedPattern, $ManagedBlock.TrimEnd(), 1)
        } else {
            $newAgents = $a.TrimEnd() + "`r`n`r`n" + $ManagedBlock.TrimEnd() + "`r`n"
        }
        Set-Content $agents $newAgents.TrimEnd() -Encoding UTF8
    } else {
        Copy-Item $TemplateAgentsPath $agents
    }

    $manifest = Join-Path $ProjectRoot "project-governance.yml"
    Copy-Item (Join-Path $TemplateRoot "project-governance.yml") $manifest
    $leaf = Split-Path $ProjectRoot -Leaf
    $m = Get-Content -Raw $manifest
    $m = [regex]::Replace($m, '(?m)^(\s*name:\s*).+$', ('${1}"' + $leaf + '"'), 1)
    $m = [regex]::Replace($m, '(?m)^([ \t]*state:[ \t]*)"UNESTABLISHED"[ \t]*$', '${1}"RECONCILIATION_REQUIRED"', 1)
    $m += @"

adoption:
  state: "RECONCILIATION_REQUIRED"
  adopted_from_existing_project: true
  historical_governance_approval: false
  note: "Pre-existing requirements, design, implementation, dependencies, verification, and risks require governance reconciliation."
"@
    Set-Content $manifest $m.TrimEnd() -Encoding UTF8

    New-Item -ItemType Directory -Force (Join-Path $ProjectRoot "docs") | Out-Null
    $recon = Join-Path $ProjectRoot "docs\governance-adoption.md"
    @"
# Governance adoption

Governance baseline: $Version
Adoption date: $(Get-Date -Format "yyyy-MM-dd")
Status: RECONCILIATION_REQUIRED

This repository existed before governance adoption.

No pre-existing requirement, design decision, implementation behavior, dependency choice, security posture, verification result, or risk acceptance is represented as historically approved under this governance baseline.

Before substantial C2/C3, security-sensitive, or release work, perform governance reconciliation and create a truthful post-adoption evidence baseline.
"@ | Set-Content $recon -Encoding UTF8

    if (-not $GitPresent -and -not $NoGitInit) {
        git -C $ProjectRoot init | Out-Null
        if ($LASTEXITCODE -ne 0) { Fail "Governance adopted, but git init failed." }
    }

    Write-Host "Governance adopted: $ProjectRoot"
    Write-Host "Status: RECONCILIATION_REQUIRED"
    Write-Host "Next: open the project in Codex and request governance reconciliation."
}
