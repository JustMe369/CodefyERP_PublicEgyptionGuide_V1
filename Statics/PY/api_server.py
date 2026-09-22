#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask API server for CodefyERP Data Validation
Provides endpoints for Excel file validation and analysis
"""

import os
import tempfile
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from CodefyDataValidator import validate_excel_file

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'codefy_uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/validate', methods=['POST'])
def validate_file():
    """Validate uploaded Excel file and return analysis results."""
    try:
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
            return jsonify(results)
        else:
            return jsonify({'error': results['error']}), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/download-cleaned', methods=['POST'])
def download_cleaned_file():
    """Generate and return a cleaned version of the validated file."""
    try:
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
            return response
        else:
            return jsonify({'error': 'Failed to clean the file'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'CodefyERP Data Validator API'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)