#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Startup script for CodefyERP Data Validation API Server
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages from requirements.txt"""
    requirements = [
        'flask',
        'pandas',
        'openpyxl',
        'flask-cors'
    ]
    
    for package in requirements:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} is already installed")
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")

def main():
    print("CodefyERP Data Validation API Server")
    print("=====================================")
    
    # Install requirements if not already installed
    install_requirements()
    
    # Change to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("\nStarting API server on http://localhost:5000")
    print("Press Ctrl+C to stop the server\n")
    
    # Import and run the API server
    try:
        from api_server import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    main()