param(
    [string]$ATPRoot = "",
    [string]$SetMM = "",
    [string]$Extension = "",
    [string]$TargetLabel = "",
    [string]$RunRoot = ""
)

$ErrorActionPreference = "Stop"

$DataRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

if (-not $ATPRoot) {
    $parent = Split-Path $DataRoot -Parent
    $candidate = Join-Path $parent "ATP"
    if (Test-Path $candidate) {
        $ATPRoot = (Resolve-Path $candidate).Path
    } else {
        throw "Could not find sibling ATP checkout. Pass -ATPRoot C:\path\to\ATP"
    }
}

if (-not $SetMM) {
    $candidate = Join-Path $ATPRoot "set.mm"
    if (Test-Path $candidate) {
        $SetMM = (Resolve-Path $candidate).Path
    } else {
        throw "Could not find set.mm under ATP. Pass -SetMM C:\path\to\frozen\set.mm"
    }
}

if (-not $RunRoot) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $RunRoot = Join-Path $DataRoot "runs\haloproof-$stamp"
}

$script = Join-Path $PSScriptRoot "prepare_haloproof.py"
$argsList = @(
    $script,
    "--atp-root", $ATPRoot,
    "--setmm", $SetMM,
    "--run-root", $RunRoot
)

if ($Extension) {
    $argsList += @("--extension", $Extension)
}
if ($TargetLabel) {
    $argsList += @("--target-label", $TargetLabel)
}

Write-Host "HaloProof advanced campaign"
Write-Host "ATP root:  $ATPRoot"
Write-Host "set.mm:   $SetMM"
Write-Host "run root: $RunRoot"
Write-Host ""

& python @argsList
$rc = $LASTEXITCODE

Write-Host ""
Write-Host "Manifest: $(Join-Path $RunRoot 'HALOPROOF_MANIFEST.json')"
exit $rc
