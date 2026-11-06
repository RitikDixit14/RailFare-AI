Set-Location -Path $PSScriptRoot
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  RAILFARE AI - INTEGRATED STREAMLIT COCKPIT & CINEMATIC LANDING SYSTEM" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host ""
if (Test-Path ".\ir_env\Scripts\python.exe") {
    .\ir_env\Scripts\python.exe start_ecosystem.py
} else {
    python start_ecosystem.py
}

