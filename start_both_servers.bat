@echo off
REM Start script for CodefyERP Data Validation System
REM Starts both the main server and the Python API server with proper process management

echo.
echo ================================================
echo    CodefyERP Data Validation System - Dual Server Startup
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
python -c "import pandas, openpyxl, numpy, chardet, flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required Python packages...
    pip install pandas openpyxl numpy chardet flask python-dateutil
)

REM Check if required Node.js packages are installed
if not exist node_modules (
    echo Installing required Node.js packages...
    npm install
)

echo.
echo Starting servers...
echo.

REM Create temporary batch file to start Python API server
echo @echo off > temp_python_start.bat
echo cd Statics/PY >> temp_python_start.bat
echo echo Starting Python API Server... >> temp_python_start.bat
echo python api_server.py >> temp_python_start.bat

REM Start the Python API server in background
echo Starting Python API server on port 5000...
start "CodefyERP Python API Server" cmd /c "temp_python_start.bat"

REM Wait a moment for the Python server to start
echo Waiting for Python API server to start...
timeout /t 5 /nobreak >nul

REM Start the main server in the current window
echo Starting main server on port 3000...
echo Access the application at: http://localhost:3000
echo.
echo Press Ctrl+C to stop both servers
echo.

REM Start the main server
node server.js

REM Cleanup
del temp_python_start.bat

echo.
echo Servers stopped.
pause