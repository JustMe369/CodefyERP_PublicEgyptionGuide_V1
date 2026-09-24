@echo off
REM Start script for CodefyERP Data Validation System
REM Starts both the main server and the Python API server

echo.
echo ================================================
echo    CodefyERP Data Validation System - Startup
echo ================================================
echo.

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if required Python packages are installed
echo Checking Python packages...
python -c "import pandas" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required Python packages...
    pip install pandas openpyxl numpy chardet python-dateutil
)

REM Check if required Node.js packages are installed
if not exist node_modules (
    echo Installing required Node.js packages...
    npm install
)

echo.
echo Starting servers...
echo.

REM Start the Python API server in background
echo Starting Python API server on port 5000...
start "Python API Server" cmd /c "cd Statics/PY && python api_server.py"

REM Wait a moment for the Python server to start
timeout /t 3 /nobreak >nul

REM Start the main server
echo Starting main server on port 3000...
node server.js

pause