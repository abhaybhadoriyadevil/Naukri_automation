@echo off
REM =====================================================================
REM  Setup Windows Task Scheduler for Resume Upload Automation
REM  Run this script AS ADMINISTRATOR
REM =====================================================================

echo.
echo ======================================================
echo   Resume Upload Automation - Scheduler Setup
echo ======================================================
echo.

REM Get the directory where this script lives
set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%main.py"

REM Check if Python is available (try 'py' launcher first, then 'python')
where py >nul 2>nul
if errorlevel 1 (
    where python >nul 2>nul
    if errorlevel 1 (
        echo [ERROR] Python is not installed or not in PATH.
        echo Please install Python from https://python.org
        pause
        exit /b 1
    )
    for /f "delims=" %%i in ('where python') do set "PYTHON_PATH=%%i"
) else (
    for /f "delims=" %%i in ('where py') do set "PYTHON_PATH=%%i"
)

echo Using Python: %PYTHON_PATH%
echo Script: %PYTHON_SCRIPT%
echo Working Dir: %SCRIPT_DIR%
echo.

REM ── Delete old tasks if they exist ──────────────────────────
echo Removing old scheduled tasks (if any)...
schtasks /delete /tn "NaukriResumeUpload_9AM" /f >nul 2>nul
schtasks /delete /tn "NaukriResumeUpload_2PM" /f >nul 2>nul
echo Done.
echo.

REM ── Create 9:00 AM task ─────────────────────────────────────
echo Creating scheduled task: 9:00 AM daily...
schtasks /create ^
    /tn "NaukriResumeUpload_9AM" ^
    /tr "\"%PYTHON_PATH%\" \"%PYTHON_SCRIPT%\"" ^
    /sc daily ^
    /st 09:00 ^
    /rl HIGHEST ^
    /f

if errorlevel 1 (
    echo [ERROR] Failed to create 9 AM task.
    echo Make sure you are running this as Administrator.
    pause
    exit /b 1
)

echo [OK] 9:00 AM task created successfully!
echo.

REM ── Create 2:00 PM task ─────────────────────────────────────
echo Creating scheduled task: 2:00 PM daily...
schtasks /create ^
    /tn "NaukriResumeUpload_2PM" ^
    /tr "\"%PYTHON_PATH%\" \"%PYTHON_SCRIPT%\"" ^
    /sc daily ^
    /st 14:00 ^
    /rl HIGHEST ^
    /f

if errorlevel 1 (
    echo [ERROR] Failed to create 2 PM task.
    echo Make sure you are running this as Administrator.
    pause
    exit /b 1
)

echo [OK] 2:00 PM task created successfully!
echo.

REM ── Verify ──────────────────────────────────────────────────
echo ======================================================
echo   Verifying scheduled tasks...
echo ======================================================
echo.
schtasks /query /tn "NaukriResumeUpload_9AM" /fo LIST
echo.
schtasks /query /tn "NaukriResumeUpload_2PM" /fo LIST
echo.

echo ======================================================
echo   Setup Complete!
echo ======================================================
echo.
echo Your resume will be automatically uploaded to
echo Naukri and Indeed at:
echo   - 09:00 AM daily
echo   - 02:00 PM daily
echo.
echo To test manually, run:  python main.py --dry-run
echo.
pause
