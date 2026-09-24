@echo off
echo.
echo 🌊 Starting CodefyERP Excel Analyzer Integration...
echo.
echo This will start both the Python API server and Node.js server
echo.
echo Press Ctrl+C to stop the servers
echo ================================================
echo.

REM Start the Python API server in a separate window
start "Python API Server" cmd /k "cd /d "%~dp0Statics\PY" && python api_server.py"

REM Wait a moment for the Python server to start
timeout /t 3 /nobreak >nul

REM Start the Node.js server in the current window
echo.
echo 🚀 Starting Node.js server...
echo Access the validation tab at http://localhost:3000/#validation
echo.
cd /d "%~dp0"
npm start