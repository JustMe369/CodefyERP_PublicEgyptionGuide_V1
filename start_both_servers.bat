@echo off
echo Starting CodefyERP Data Validation System...
echo.

REM Check if node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python first.
    pause
    exit /b 1
)

echo Installing required Node.js packages...
npm install

if errorlevel 1 (
    echo Error installing packages
    pause
    exit /b 1
)

REM Start the local server in the background
echo Starting local server on http://localhost:3000
start "CodefyERP Local Server" cmd /c "node server.js"

REM Give the server a moment to start
timeout /t 3 /nobreak >nul

REM Start the Python API server in the background
echo Starting Python API server on http://localhost:5000
start "CodefyERP API Server" cmd /c "cd Statics/PY && python api_server.py"

echo.
echo Servers started successfully!
echo.
echo - Local Server: http://localhost:3000
echo - API Server: http://localhost:5000
echo.
echo Opening the application in your default browser...
start http://localhost:3000

echo.
echo Note: Keep this command window open while using the application.
echo Press Ctrl+C in each server window to stop the services.
echo.

pause