@echo off
echo Starting CodefyERP Data Validation API Server...
echo.

REM Change to the Scripts directory
cd /d "%~dp0Statics\PY"

echo Checking if required packages are installed...
python -c "import flask, pandas, openpyxl" 2>nul
if errorlevel 1 (
    echo Installing required packages...
    pip install flask pandas openpyxl
)

echo.
echo Starting the API server on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python api_server.py

pause