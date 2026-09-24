#!/bin/bash

echo ""
echo "🌊 Starting CodefyERP Excel Analyzer Integration..."
echo ""
echo "This will start both the Python API server and Node.js server"
echo ""
echo "Press Ctrl+C to stop the servers"
echo "================================="
echo ""

# Start the Python API server in the background
echo "🚀 Starting Python API server..."
cd "$(dirname "$0")/Statics/PY" && python api_server.py &
PYTHON_PID=$!

# Wait a moment for the Python server to start
sleep 3

# Start the Node.js server in the foreground
echo ""
echo "🚀 Starting Node.js server..."
echo "Access the validation tab at http://localhost:3000/#validation"
echo ""

cd "$(dirname "$0")"
npm start

# Cleanup on exit
trap 'kill $PYTHON_PID 2>/dev/null' EXIT