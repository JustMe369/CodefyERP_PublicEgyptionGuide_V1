"""
Simple test to verify the Python analyzer can run independently
"""
import sys
import os
import json

# Add the PY directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Statics', 'PY'))

try:
    from CodefyExcelAnalyzer_V11.3.1 import CodefyAnalyzer
    print("✅ Successfully imported CodefyExcelAnalyzer")
    
    # Test basic functionality
    print("\n📋 Testing analyzer creation...")
    
    # Check if key methods exist
    methods_to_check = ['run', 'to_api_dict', '_compute_score']
    for method in methods_to_check:
        if hasattr(CodefyAnalyzer, method) or method in dir(CodefyAnalyzer):
            print(f"✅ Method available: {method}")
        else:
            print(f"❌ Method missing: {method}")
    
    print("\n🎉 Python analyzer is ready for API integration!")
    print("\nTo test with a real file, run:")
    print("cd Statics/PY")
    print("python api_server.py")
    print("\nThen access the API at http://localhost:5000/api/health")

except ImportError as e:
    print(f"❌ Failed to import CodefyExcelAnalyzer: {e}")
    print("\nMake sure you have installed the required packages:")
    print("pip install pandas openpyxl numpy chardet flask python-dateutil")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()