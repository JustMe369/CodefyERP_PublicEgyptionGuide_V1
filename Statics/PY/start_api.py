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

def install_requirements():
    """Install required packages if not already installed."""
    print("Checking for required packages...")
    
    required_packages = ['flask', 'openpyxl', 'pandas']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is already installed")
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def start_server():
    """Start the Flask API server."""
    print("Starting CodefyERP Data Validation API Server...")
    print("Server will be available at http://localhost:5000")
    
    try:
        # Import and run the Flask app
        from api_server import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("CodefyERP Data Validation API Server Startup")
    print("="*50)
    
    install_requirements()
    start_server()