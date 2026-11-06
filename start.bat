@echo off
title RailFare AI - Dual Server Ecosystem
:: Always navigate to the script directory regardless of where it was launched
cd /d "%~dp0"
echo ==============================================================================
echo   RAILFARE AI - INTEGRATED STREAMLIT COCKPIT ^& CINEMATIC LANDING SYSTEM
echo ==============================================================================
echo.
python start_ecosystem.py
if errorlevel 1 (
    echo.
    echo Running with virtual environment Python...
    .\ir_env\Scripts\python.exe start_ecosystem.py
)
pause

