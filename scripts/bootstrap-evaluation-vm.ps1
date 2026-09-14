[CmdletBinding()]
param(
    [string]$Lock,
    [string]$ArtifactCache,
    [switch]$Fetch,
    [switch]$Apply,
    [string[]]$Artifact,
    [string]$VscodeCommand,
    [string]$VscodeUserDataDir,
    [switch]$Latest,
    [Alias('Host')][ValidateSet('codex', 'claude', 'all')][string]$AgentHost = 'all'
)

$ErrorActionPreference = 'Stop'

function Fail([string]$Message) { throw "Evaluation VM bootstrap: FAIL - $Message" }
function Get-Sha256([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }

if ($Latest) {
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) { Fail 'latest Windows bootstrap requires winget' }
    Write-Host "Latest Windows evaluation VM plan; host=$AgentHost"
    Write-Host '- install current Python and VS Code through winget'
    Write-Host '- install current selected Codex/Claude VS Code extensions into a dedicated test profile'
    Write-Host '- configure the selected framework host adapter'
    Write-Host '- account sign-in, model choice, and licence acceptance remain interactive'
    if (-not $Apply) { Write-Host 'DRY RUN ONLY. Re-run with -Apply after reviewing the plan.'; exit 0 }
    if ((Read-Host 'Type APPLY-LATEST-VM-BOOTSTRAP to install current VM prerequisites') -ne 'APPLY-LATEST-VM-BOOTSTRAP') { Fail 'installation confirmation did not match' }
    & $winget.Source install --exact --id Python.Python.3.14
    if ($LASTEXITCODE -ne 0) { Fail 'latest Python installation failed' }
    & $winget.Source install --exact --id Microsoft.VisualStudioCode
    if ($LASTEXITCODE -ne 0) { Fail 'latest VS Code installation failed' }
    if (-not $VscodeUserDataDir) { Fail 'latest Windows bootstrap requires -VscodeUserDataDir' }
    $profilePath = [System.IO.Path]::GetFullPath($VscodeUserDataDir)
    $marker = Join-Path $profilePath '.manual-vscode-test-profile.json'
    if (Test-Path -LiteralPath $profilePath) {
        if (-not (Test-Path -LiteralPath $marker)) { Fail 'test profile exists but is not framework-initialized' }
    } else {
        $profileParent = Split-Path -Parent $profilePath
        if (-not (Test-Path -LiteralPath $profileParent)) { Fail 'test-profile parent does not exist' }
        New-Item -ItemType Directory -Path $profilePath | Out-Null
        @{ schema_version = '1'; kind = 'MANUAL_VSCODE_TEST_PROFILE' } | ConvertTo-Json | Set-Content -LiteralPath $marker -Encoding utf8
    }
    $codeCandidates = @(
        (Get-Command code -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
        (Join-Path $env:LOCALAPPDATA 'Programs\Microsoft VS Code\bin\code.cmd'),
        (Join-Path $env:ProgramFiles 'Microsoft VS Code\bin\code.cmd')
    )
    $code = $codeCandidates | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -First 1
    if (-not $code) { Fail 'VS Code command is unavailable after installation; start a new PowerShell and retry' }
    $extensionIds = if ($AgentHost -eq 'all') { @('openai.chatgpt', 'anthropic.claude-code') } elseif ($AgentHost -eq 'codex') { @('openai.chatgpt') } else { @('anthropic.claude-code') }
    foreach ($extension in $extensionIds) {
        & $code '--user-data-dir' $profilePath '--extensions-dir' (Join-Path $profilePath 'extensions') '--install-extension' $extension
        if ($LASTEXITCODE -ne 0) { Fail "latest VS Code extension installation failed: $extension" }
    }
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
    if (-not $python) { Fail 'Python command is unavailable after installation; start a new PowerShell and retry' }
    if ($python.Source -match '(?i)py(\.exe)?$') { & $python.Source -3 (Join-Path $PSScriptRoot '..\governance.py') host install --host $AgentHost -y } else { & $python.Source (Join-Path $PSScriptRoot '..\governance.py') host install --host $AgentHost -y }
    if ($LASTEXITCODE -ne 0) { Fail 'framework host-adapter configuration failed' }
    Write-Host 'Latest Windows evaluation VM bootstrap: PASS'
    Write-Host 'Interactive account sign-in, model choice, and licence acceptance: NOT PERFORMED'
    exit 0
}

if (-not $Lock -or -not $ArtifactCache) { Fail 'Lock and ArtifactCache are required unless -Latest is used' }

$lockPath = (Resolve-Path -LiteralPath $Lock -ErrorAction Stop).Path
$config = Get-Content -LiteralPath $lockPath -Raw | ConvertFrom-Json
if ($config.schema_version -ne '1' -or $config.kind -ne 'EVALUATION_VM_BOOTSTRAP_LOCK') { Fail 'unsupported bootstrap lock schema' }
$items = @($config.artifacts | Where-Object { $_.platform -eq 'Windows' })
if ($items.Count -eq 0) { Fail 'bootstrap lock has no Windows artifacts' }
if ($Artifact.Count -gt 0) {
    $missing = @($Artifact | Where-Object { $_ -notin @($items | ForEach-Object { $_.id }) })
    if ($missing.Count -gt 0) { Fail "requested artifact is not available for Windows: $($missing -join ', ')" }
    $items = @($items | Where-Object { $_.id -in $Artifact })
}
foreach ($item in $items) {
    if ($item.kind -notin @('windows-exe', 'vsix') -or -not $item.id -or -not $item.version -or -not $item.filename -or -not $item.url -or -not $item.sha256) { Fail 'Windows lock artifact is invalid' }
    if ($item.filename -ne [System.IO.Path]::GetFileName($item.filename) -or $item.url -notmatch '^https://') { Fail 'Windows lock artifact filename or URL is unsafe' }
    if ($item.sha256 -notmatch '^[0-9a-fA-F]{64}$') { Fail 'Windows lock artifact requires SHA-256' }
    if ($item.kind -eq 'windows-exe' -and $null -eq $item.install_args) { Fail 'windows-exe requires reviewed install_args in the lock' }
    if ($item.kind -eq 'windows-exe' -and (@($item.install_args | Where-Object { $_ -match '(?i)accept|eula|quiet|silent' }).Count -gt 0)) { Fail 'windows-exe install_args may not suppress or pre-accept licence prompts' }
}

$cachePath = [System.IO.Path]::GetFullPath($ArtifactCache)
if (-not (Test-Path -LiteralPath $cachePath)) {
    if (-not $Fetch) { Fail 'artifact cache does not exist; use -Fetch to create it' }
    $parent = Split-Path -Parent $cachePath
    if (-not (Test-Path -LiteralPath $parent)) { Fail 'artifact-cache parent does not exist' }
    New-Item -ItemType Directory -Path $cachePath -ErrorAction Stop | Out-Null
}
if (-not (Get-Item -LiteralPath $cachePath).PSIsContainer) { Fail 'artifact cache is not a directory' }

foreach ($item in $items) { Write-Host "- $($item.id) $($item.version) [$($item.kind)]" }
if ($Fetch) {
    foreach ($item in $items) {
        $target = Join-Path $cachePath $item.filename
        if (Test-Path -LiteralPath $target) {
            if ((Get-Sha256 $target) -ne $item.sha256.ToLowerInvariant()) { Fail "existing artifact hash differs: $($item.filename)" }
            Write-Host "Verified cached artifact: $($item.id)"
            continue
        }
        $partial = "$target.partial"
        if (Test-Path -LiteralPath $partial) { Fail "partial artifact already exists: $($item.filename)" }
        Write-Host "Downloading $($item.id) $($item.version)..."
        Invoke-WebRequest -Uri $item.url -OutFile $partial
        if ((Get-Sha256 $partial) -ne $item.sha256.ToLowerInvariant()) { Remove-Item -LiteralPath $partial -Force; Fail "download SHA-256 mismatch: $($item.id)" }
        Move-Item -LiteralPath $partial -Destination $target
    }
}

foreach ($item in $items) {
    $target = Join-Path $cachePath $item.filename
    if (-not (Test-Path -LiteralPath $target) -or (Get-Sha256 $target) -ne $item.sha256.ToLowerInvariant()) { Fail "missing or mismatched artifact: $($item.filename)" }
}
if (-not $Apply) { Write-Host 'DRY RUN ONLY. Re-run with -Apply after reviewing the displayed installers.'; exit 0 }
if ((Read-Host 'Type APPLY-LOCKED-VM-BOOTSTRAP to install the verified artifacts') -ne 'APPLY-LOCKED-VM-BOOTSTRAP') { Fail 'installation confirmation did not match' }

foreach ($item in $items) {
    $target = Join-Path $cachePath $item.filename
    if ($item.kind -eq 'windows-exe') {
        if ($null -eq $item.install_args) { Fail "windows-exe has no reviewed install_args: $($item.id)" }
        $process = Start-Process -FilePath $target -ArgumentList ([string[]]$item.install_args) -Wait -PassThru
        if ($process.ExitCode -ne 0) { Fail "installer failed: $($item.id) (exit $($process.ExitCode))" }
    } else {
        if (-not $VscodeCommand -or -not $VscodeUserDataDir) { Fail 'VSIX installation requires -VscodeCommand and -VscodeUserDataDir' }
        $marker = Join-Path $VscodeUserDataDir '.manual-vscode-test-profile.json'
        if (-not (Test-Path -LiteralPath $marker)) { Fail 'VSIX installation requires an initialized dedicated test profile' }
        & $VscodeCommand '--user-data-dir' $VscodeUserDataDir '--extensions-dir' (Join-Path $VscodeUserDataDir 'extensions') '--install-extension' $target
        if ($LASTEXITCODE -ne 0) { Fail "VSIX installation failed: $($item.id)" }
    }
}
Write-Host 'Evaluation VM bootstrap: PASS'
Write-Host 'Interactive account sign-in and license acceptance: NOT PERFORMED'
