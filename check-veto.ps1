# Project checks run without an API key and never enable voice or personal folders.
[CmdletBinding()]
param([switch]$Install)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$VetoPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
function Assert-Check([string]$Step) {
    if ($LASTEXITCODE -ne 0) { throw "$Step failed. Fix the reported error before committing." }
}
if (-not (Test-Path -LiteralPath $VetoPython)) {
    throw 'Run .\run-veto.ps1 -SetupOnly first to create the Python environment.'
}
if ($Install) {
    & $VetoPython -m pip install -r backend/requirements-dev.txt
    Assert-Check 'Development dependency installation'
}
& $VetoPython -m ruff check backend scripts tests
Assert-Check 'Python lint'
& $VetoPython -m ruff format --check backend scripts tests
Assert-Check 'Python formatting'
& $VetoPython -m pytest
Assert-Check 'Sample safety tests'
Push-Location -LiteralPath 'frontend'
try {
    npm.cmd run check
    Assert-Check 'Interface types, lint and formatting'
    npm.cmd run build
    Assert-Check 'Production interface build'
} finally { Pop-Location }
Write-Host 'All Veto checks passed. Live NVIDIA testing remains a separate pending gate.'
