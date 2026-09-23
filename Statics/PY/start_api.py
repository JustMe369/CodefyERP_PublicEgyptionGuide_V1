#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Startup script for CodefyERP Data Validation API Server
"""

import subprocess
import sys
import os
import signal
import time

def start_api_server():
    """Start the Flask API server."""
    print("Starting CodefyERP Data Validation API Server...")
    print("Initializing enhanced analyzer with advanced features...")
    
    # Start the Flask server using the enhanced analyzer
    try:
        # Change to the PY directory to run the server
        py_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(py_dir)
        
        # Run the API server
        process = subprocess.Popen([sys.executable, 'api_server.py'])
        
        print(f"API server started with PID {process.pid}")
        print("Server is running on http://localhost:5000")
        print("Enhanced analyzer with Shift Engine and Time Control Center is active")
        print("\nPress Ctrl+C to stop the server")
        
        # Wait for the process to complete (or be interrupted)
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\nStopping API server...")
            process.send_signal(signal.SIGTERM)
            try:
                process.wait(timeout=5)  # Wait up to 5 seconds for graceful shutdown
            except subprocess.TimeoutExpired:
                process.kill()  # Force kill if it doesn't shut down gracefully
            print("API server stopped.")
            
    except Exception as e:
        print(f"Error starting API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_api_server()