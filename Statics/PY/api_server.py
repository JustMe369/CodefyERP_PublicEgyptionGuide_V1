#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask API server for CodefyERP Data Validation
Provides endpoints for Excel file validation and analysis
"""

import os
import tempfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # Add CORS support
from werkzeug.utils import secure_filename
from CodefyDataValidator import validate_excel_file

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure upload folder
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'codefy_uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/validate', methods=['POST', 'OPTIONS'])
def validate_file():
    """Validate uploaded Excel file and return analysis results."""
    try:
        if request.method == 'OPTIONS':
            # Handle preflight request
            response = jsonify()
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
            
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload an Excel file.'}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        # Perform validation
        results = validate_excel_file(temp_path)
        
        # Clean up temporary file
        os.remove(temp_path)
        
        if results['success']:
            response = jsonify(results)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        else:
            response = jsonify({'error': results['error']}), 500
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
            
    except Exception as e:
        response = jsonify({'error': f'Server error: {str(e)}'}), 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/deep-analyze', methods=['POST', 'OPTIONS'])
def deep_analyze_file():
    """Perform deep analysis on uploaded Excel file using advanced analyzer."""
    try:
        if request.method == 'OPTIONS':
            # Handle preflight request
            response = jsonify()
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
            
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload an Excel file.'}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        # Import and use the advanced analyzer
        from CodefyExcelAnalyzer_V11.3.1 import CodefyAnalyzer, AppSettings
        settings = AppSettings()
        analyzer = CodefyAnalyzer(temp_path, settings=settings)
        
        # Run the full analysis
        report, fixes = analyzer.run()
        
        # Prepare detailed results
        results = {
            'success': True,
            'summary': analyzer.get_analysis_summary(),
            'detailed_issues': analyzer.build_issue_list(),
            'fixes_available': len(analyzer.fixes),
            'shift_upgrades': len(analyzer.issues['shift_upgrades']),
            'time_conflicts': len(analyzer.issues['time_conflicts']),
            'time_normalizations': len(analyzer.issues['time_normalizations']),
            'red_flags': len(analyzer.red_flag_cells),
            'ready_to_upload': analyzer.upload_ready
        }
        
        # Clean up temporary file
        os.remove(temp_path)
        
        response = jsonify(results)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
            
    except Exception as e:
        response = jsonify({'error': f'Server error during deep analysis: {str(e)}'}), 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/download-cleaned', methods=['POST', 'OPTIONS'])
def download_cleaned_file():
    """Generate and return a cleaned version of the validated file."""
    try:
        if request.method == 'OPTIONS':
            # Handle preflight request
            response = jsonify()
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
            
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload an Excel file.'}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"input_{filename}")
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"cleaned_{filename}")
        file.save(input_path)
        
        # Create validator and apply fixes
        from CodefyDataValidator import CodefyDataValidator
        validator = CodefyDataValidator(input_path)
        
        if not validator.analyze():
            os.remove(input_path)
            return jsonify({'error': 'Failed to analyze the file'}), 500
        
        success = validator.apply_fixes(output_path)
        
        # Clean up input file
        os.remove(input_path)
        
        if success:
            # Return the cleaned file
            response = send_file(output_path, as_attachment=True, download_name=f"cleaned_{filename}")
            # Schedule cleanup of output file after response
            import threading
            def cleanup():
                import time
                time.sleep(5)  # Wait 5 seconds before cleaning up
                try:
                    os.remove(output_path)
                except:
                    pass  # Ignore errors during cleanup
            threading.Thread(target=cleanup).start()
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        else:
            response = jsonify({'error': 'Failed to clean the file'}), 500
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
            
    except Exception as e:
        response = jsonify({'error': f'Server error: {str(e)}'}), 500
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    response = jsonify({'status': 'healthy', 'service': 'CodefyERP Data Validator API'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)