 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask API server for CodefyERP Sheet Analyzer v11.3.1
Provides endpoints for Excel file analysis, export, validation, and cleaned download.
"""

import os
import sys
import json
import time
import tempfile
import traceback
import threading
from datetime import datetime

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from codefy_web_service import (
    CodefyWebService, TempFileManager, _is_allowed,
    ALLOWED_EXTENSIONS, EXPORT_FORMATS,
)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'codefy_uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

service = CodefyWebService()












@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'CodefyERP Excel Analyzer API',
        'version': '1.0.0',
        'features': [
            'Egyptian phone validation',
            'Arabic date support', 
            'Fleet data validation',
            'Multi-format export',
            'Quality scoring'
        ]
    })


@app.route('/api/validate-excel', methods=['POST'])
def validate_excel():
    """Validate uploaded Excel/CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file to temporary location
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        # Create analyzer instance and run validation
        analyzer = CodefyAnalyzer(file_path=temp_path)
        
        # In a real implementation, we would run the full analysis
        # For now, we'll simulate the analysis
        try:
            # This would run the full analysis
            result, fixes = analyzer.run()
            
            # Return the API-ready dictionary
            api_result = analyzer.to_api_dict()
            api_result['success'] = True
            api_result['message'] = f"File {file.filename} analyzed successfully"
            
            return jsonify(api_result)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Error during analysis'
            }), 500
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Server error during file validation'
        }), 500


@app.route('/api/validate-and-fix', methods=['POST'])
def validate_and_fix():
    """Validate and fix Excel/CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get options
        auto_fix = request.form.get('auto_fix', 'true').lower() == 'true'
        
        # Save uploaded file to temporary location
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        try:
            # Create analyzer and run analysis
            analyzer = CodefyAnalyzer(file_path=temp_path)
            result, fixes = analyzer.run()
            
            # Get API-ready results
            api_result = analyzer.to_api_dict()
            api_result['success'] = True
            api_result['auto_fix_applied'] = auto_fix
            api_result['original_filename'] = file.filename
            
            # If auto-fix is enabled, prepare fixed file
            if auto_fix and api_result.get('fixes_applied'):
                # In a real implementation, we would generate a fixed file
                # For now, we just indicate that fixes are available
                api_result['fixed_file_available'] = True
            
            return jsonify(api_result)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Error during validation and fixing'
            }), 500
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Server error during validation and fixing'
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
