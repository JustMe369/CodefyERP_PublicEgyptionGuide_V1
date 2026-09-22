#!/bin/bash

echo "Starting CodefyERP Data Validation System..."
echo

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python is not installed. Please install Python first."
    exit 1
fi

echo "Installing required Node.js packages..."
npm install

if [ $? -ne 0 ]; then
    echo "Error installing packages"
    exit 1
fi

# Start the local server in the background
echo "Starting local server on http://localhost:3000"
node server.js > server.log 2>&1 &
SERVER_PID=$!

# Give the server a moment to start
sleep 3

# Start the Python API server in the background
echo "Starting Python API server on http://localhost:5000"
cd Statics/PY && python3 api_server.py > api.log 2>&1 &
API_PID=$!

echo
echo "Servers started successfully!"
echo
echo "- Local Server: http://localhost:3000"
echo "- API Server: http://localhost:5000"
echo

# Open the application in the default browser (works on macOS and some Linux distros)
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
elif command -v open &> /dev/null; then
    open http://localhost:3000
else
    echo "Please open http://localhost:3000 in your browser"
fi

echo
echo "Note: The servers are running in the background."
echo "To stop the services, run: kill $SERVER_PID $API_PID"
echo

# Keep the script running
wait $SERVER_PID $API_PID