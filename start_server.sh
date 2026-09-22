#!/bin/bash

echo "Starting CodefyERP Data Validation API Server..."
echo

# Change to the Scripts directory
cd "$(dirname "$0")/Statics/PY"

echo "Checking if required packages are installed..."
if ! python3 -c "import flask, pandas, openpyxl" &> /dev/null; then
    echo "Installing required packages..."
    pip3 install flask pandas openpyxl
fi

echo
echo "Starting the API server on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo
python3 api_server.py