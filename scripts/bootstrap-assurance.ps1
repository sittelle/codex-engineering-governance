param(
    [string]$ProjectRoot,
    [switch]$Apply,
    [switch]$SkipCI,
    [switch]$AllowUnconfiguredCI
)
$ErrorActionPreference = "Stop"
$argsList = @()
if ($ProjectRoot) { $argsList += @("--project-root", $ProjectRoot) }
if ($Apply) { $argsList += "--apply" }
if ($SkipCI) { $argsList += "--skip-ci" }
if ($AllowUnconfiguredCI) { $argsList += "--allow-unconfigured-ci" }
python (Join-Path $PSScriptRoot "bootstrap-assurance.py") @argsList
exit $LASTEXITCODE
