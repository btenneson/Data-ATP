@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (
    py -3 autopilot.py --mode full --output results\latest
) else (
    python autopilot.py --mode full --output results\latest
)
if errorlevel 1 (
    echo.
    echo AUTOPILOT FAILED. See results\latest\AUTOPILOT_REPORT.md and AUTOPILOT_RESULT.json
    pause
    exit /b 1
)
echo.
echo AUTOPILOT PASSED. Read results\latest\AUTOPILOT_REPORT.md
pause
