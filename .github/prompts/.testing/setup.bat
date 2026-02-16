@echo off
REM Windows setup script for LLM Prompt Testing Framework

echo ============================================================
echo LLM Prompt Testing Framework - Windows Setup
echo ============================================================
echo.

REM Check if Python 3.12 is installed via the launcher
py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python launcher (py) is not installed or not working
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Install dependencies
echo Installing Python dependencies...
py -3.12 -m pip install -r .testing\requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.

REM Setup .env file
if not exist .testing\.env (
    echo Creating .env file...
    copy .testing\.env.example .testing\.env >nul
    echo [OK] Created .env file
    echo [IMPORTANT] Edit .testing\.env and add your API keys!
) else (
    echo [INFO] .env file already exists
)
echo.

REM Create results directory
if not exist .testing\results mkdir .testing\results
echo [OK] Results directory ready
echo.

echo ============================================================
echo Setup completed successfully!
echo ============================================================
echo.
echo Next steps:
echo   1. Edit .testing\.env and add your API keys
echo   2. Run: npm test path\to\prompt.md
echo   3. Check .testing\QUICKSTART.md for more info
echo.
pause
