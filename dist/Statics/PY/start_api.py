#!/usr/bin/env python3
"""
Start script for the CodefyExcelAnalyzer API Server
"""

import subprocess
import sys
import os
import signal
import time

def main():
    print("🚀 Starting CodefyExcelAnalyzer API Server...")
    print("📁 Location: ./Statics/PY/api_server.py")
    print("🔗 Running on: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        # Change to the PY directory
        py_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(py_dir)
        
        # Run the API server
        process = subprocess.Popen([
            sys.executable, 'api_server.py'
        ])
        
        # Wait for the process to finish
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down API server...")
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("✅ API server stopped.")
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
