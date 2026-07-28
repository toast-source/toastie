@echo off
cd /d "%~dp0"
echo Starting Aseprite Viewer...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)
python -m pip show pygame >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
)
python ase_viewer.py %*
set APP_EXIT_CODE=%errorlevel%
pause
exit /b %APP_EXIT_CODE%
