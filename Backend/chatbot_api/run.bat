@echo off
REM Startup script for KAIROS Chatbot API on Windows

echo.
echo ============================================================
echo KAIROS Chatbot API - Windows Launcher
echo ============================================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Change to script directory
cd /d "%SCRIPT_DIR%"

echo Directory: %SCRIPT_DIR%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo Python found: 
python --version

echo.
echo Installing/Checking dependencies...
python -m pip install -r requirements.txt --quiet

echo.
echo ============================================================
echo Starting KAIROS Chatbot API Server
echo ============================================================
echo.
echo Server will run on: http://127.0.0.1:8001
echo API Docs:          http://127.0.0.1:8001/docs
echo ReDoc:             http://127.0.0.1:8001/redoc
echo.
echo Press Ctrl+C to stop the server
echo.

python run.py

pause
