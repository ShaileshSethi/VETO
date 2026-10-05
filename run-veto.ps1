[CmdletBinding()]
param([switch]$SetupOnly, [ValidateSet('mock','nebius')][string]$Mode)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
function Check-Exit([string]$Step) {
    if ($LASTEXITCODE -ne 0) { throw "$Step failed. See the error above." }
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw 'Python missing. Install Python 3.11 or newer from python.org with PATH enabled.' }
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { throw 'Node.js missing. Install Node.js 22.12+ LTS from nodejs.org.' }
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
    python -m venv .venv
    Check-Exit 'Python environment setup'
}
$VetoPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if ($SetupOnly -or -not (Test-Path -LiteralPath '.venv/veto-dependencies-ready')) {
    & $VetoPython -m pip install -r backend/requirements-lock.txt
    Check-Exit 'Backend dependency installation'
    Set-Content -LiteralPath '.venv/veto-dependencies-ready' -Value 'ready'
}
Push-Location -LiteralPath 'frontend'
try {
    if ($SetupOnly -or -not (Test-Path -LiteralPath 'node_modules')) {
        npm.cmd ci --no-audit --no-fund
        Check-Exit 'Frontend dependency installation'
    }
    npm.cmd run build
    Check-Exit 'Interface build'
} finally { Pop-Location }
& $VetoPython scripts/generate_samples.py
Check-Exit 'Sample generation'
if ($SetupOnly) { Write-Host 'Setup complete. Run .\run-veto.ps1 to start Veto.'; exit 0 }
Write-Host 'Open http://127.0.0.1:8765 in your browser. Press Ctrl+C here to stop Veto.'
Write-Host 'Voice is off. Only the selected sample folder can be sorted after exact approval.'
$VetoPreviousMode = $env:VETO_MODE
try {
    if ($Mode) { $env:VETO_MODE = $Mode }
    & $VetoPython -m uvicorn backend.main:create_app --factory --host 127.0.0.1 --port 8765 --no-access-log --log-level info
    Check-Exit 'Veto server'
} finally { $env:VETO_MODE = $VetoPreviousMode }
