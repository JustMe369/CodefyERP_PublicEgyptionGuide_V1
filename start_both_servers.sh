#!/bin/bash
# Start script for CodefyERP Data Validation System
# Starts both the main server and the Python API server

echo ""
echo "================================="
echo "  CodefyERP Data Validation System - Dual Server Startup"
echo "================================="
echo ""

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed or not in PATH"
    echo "Please install Python from https://www.python.org/"
    exit 1
fi

# Check if required Python packages are installed
echo "Checking Python packages..."
if ! python3 -c "import pandas, openpyxl, numpy, chardet, flask" &> /dev/null; then
    echo "Installing required Python packages..."
    pip3 install pandas openpyxl numpy chardet flask python-dateutil
fi

# Check if required Node.js packages are installed
if [ ! -d "node_modules" ]; then
    echo "Installing required Node.js packages..."
    npm install
fi

echo ""
echo "Starting servers..."
echo ""

# Start the Python API server in background
echo "Starting Python API server on port 5000..."
cd Statics/PY &
python3 api_server.py &
PYTHON_PID=$!
cd ..

# Wait a moment for the Python server to start
echo "Waiting for Python API server to start..."
sleep 5

# Start the main server
echo "Starting main server on port 3000..."
echo "Access the application at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start the main server and capture its PID
node server.js &
MAIN_PID=$!

# Function to handle shutdown
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $MAIN_PID $PYTHON_PID 2>/dev/null
    echo "Servers stopped."
    exit 0
}

# Trap Ctrl+C to perform cleanup
trap cleanup INT

# Wait for the main server to finish
wait $MAIN_PID