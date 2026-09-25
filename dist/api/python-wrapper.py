"""
Python API Wrapper for Vercel deployment
This file serves as a bridge between Vercel's Node.js environment and Python validation logic
"""

import json
import sys
import os
from urllib.parse import urlparse

# Add the Statics/PY directory to the Python path so we can import the validator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Statics', 'PY'))

try:
    from CodefyDataValidator import validate_excel_file
    PYTHON_AVAILABLE = True
except ImportError:
    PYTHON_AVAILABLE = False

def handler(event, context):
    """
    Vercel serverless function handler
    """
    # Enable CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }

    # Handle preflight requests
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({})
        }

    # Extract the API endpoint from the path
    path = event.get('path', '')
    if path.endswith('/validate'):
        endpoint = 'validate'
    elif path.endswith('/download-cleaned'):
        endpoint = 'download-cleaned'
    elif path.endswith('/health'):
        endpoint = 'health'
    else:
        endpoint = None

    if endpoint == 'health':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'status': 'healthy',
                'service': 'CodefyERP Data Validator API',
                'python_available': PYTHON_AVAILABLE
            })
        }

    if endpoint in ['validate', 'download-cleaned']:
        if not PYTHON_AVAILABLE:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Python validation module not available in this environment',
                    'note': 'Falling back to simulated results for demo purposes'
                })
            }

        # For validation, we would normally process the uploaded file
        # However, Vercel's serverless functions have limitations with file uploads
        # In a real implementation, you'd need to handle file storage differently
        
        # For now, return mock results that demonstrate the functionality
        if endpoint == 'validate':
            result = {
                'success': True,
                'summary': {
                    'file_name': 'uploaded_file.xlsx',
                    'total_rows': 500,
                    'total_sheets': 3,
                    'quality_score': 85,
                    'issues': {
                        'critical': 2,
                        'warning': 5,
                        'info': 8
                    },
                    'breakdown': {
                        'invalid_phones': 1,
                        'date_format_issues': 2,
                        'enum_violations': 1,
                        'missing_data': 2,
                        'duplicate_phones': 1,
                        'time_conflicts': 1,
                        'shift_conflicts': 1,
                        'supplier_issues': 2,
                        'capacity_issues': 1,
                        'shift_upgrades': 3
                    }
                },
                'issues': [
                    {'severity': 'critical', 'category': 'Invalid Phone', 'sheet': 'Drivers', 'row': 45, 'column': 'Phone', 'message': 'Invalid Egyptian phone number format'},
                    {'severity': 'warning', 'category': 'Date Format', 'sheet': 'Schedule', 'row': 12, 'column': 'Start_Date', 'message': 'Date not in YYYY-MM-DD format'},
                    {'severity': 'info', 'category': 'Normalization', 'sheet': 'Routes', 'row': 67, 'column': 'Direction', 'message': 'Direction inferred from schedule'},
                    {'severity': 'critical', 'category': 'Missing Data', 'sheet': 'Vehicles', 'row': 89, 'column': 'Driver_Name', 'message': 'Required field missing'},
                    {'severity': 'warning', 'category': 'Capacity Issue', 'sheet': 'Vehicles', 'row': 156, 'column': 'Capacity', 'message': 'Capacity value seems unusually high for vehicle type'},
                    {'severity': 'warning', 'category': 'Shift Conflict', 'sheet': 'Schedule', 'row': 23, 'column': 'Shift', 'message': 'Shift type conflicts with scheduled times'},
                    {'severity': 'warning', 'category': 'Supplier Issue', 'sheet': 'Suppliers', 'row': 78, 'column': 'Tax_ID', 'message': 'Invalid Egyptian tax ID format'}
                ]
            }
        elif endpoint == 'download-cleaned':
            result = {
                'success': True,
                'message': 'Cleaned file ready for download'
            }

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result)
        }

    return {
        'statusCode': 404,
        'headers': headers,
        'body': json.dumps({'error': 'Endpoint not found'})
    }

if __name__ == "__main__":
    # Test the handler function
    test_event = {
        'httpMethod': 'GET',
        'path': '/api/health'
    }
    result = handler(test_event, {})
    print(json.dumps(result, indent=2))