#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask API server for CodefyERP Sheet Analyzer v11.3.1
Provides endpoints for Excel file analysis, export, validation, and cleaned download.
"""

import os
import sys
import json
import tempfile
from datetime import datetime

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import the main analyzer class from CodefyDataValidator
import importlib.util
analyzer_spec = importlib.util.spec_from_file_location(
    "CodefyDataValidator", 
    os.path.join(os.path.dirname(__file__), "CodefyDataValidator.py")
)
analyzer_module = importlib.util.module_from_spec(analyzer_spec)
analyzer_spec.loader.exec_module(analyzer_module)
CodefyAnalyzer = analyzer_module.CodefyDataValidator

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'codefy_uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

service = CodefyWebService()


@app.route('/', methods=['GET'])
def index():
    """Home route with API documentation"""
    return jsonify({
        'service': 'CodefyERP Excel Analyzer API',
        'version': '11.3.1',
        'endpoints': {
            'POST /api/validate': 'Validate Excel file and return issues',
            'POST /api/validate-excel': 'Validate Excel file and return issues',
            'POST /api/validate-and-fix': 'Validate and return fixed file',
            'POST /api/export': 'Export file in various formats',
            'GET /api/health': 'Health check',
            'GET /api/settings': 'Get current settings',
            'POST /api/settings': 'Update settings'
        }
    })


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
            # Run the full analysis
            success = analyzer.analyze()
            if not success:
                return jsonify({
                    'success': False,
                    'error': 'Analysis failed',
                    'message': 'Could not analyze the uploaded file'
                }), 500
            
            # Return the API-ready dictionary
            api_result = {
                'success': True,
                'summary': analyzer.get_analysis_summary(),
                'issues': analyzer._all_issues(),
                'fixes_available': len(analyzer.fixes) > 0,
                'message': f"File {file.filename} analyzed successfully"
            }
            
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
    """Validate and fix Excel/CSV file, returning the fixed file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get options - check both form data and query parameters
        auto_fix = request.form.get('auto_fix', 'true').lower() == 'true'
        
        # Save uploaded file to temporary location
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        file.save(temp_path)
        
        try:
            # Create analyzer and run analysis
            analyzer = CodefyAnalyzer(file_path=temp_path)
            
            # Run the analysis
            success = analyzer.analyze()
            if not success:
                return jsonify({
                    'success': False,
                    'error': 'Analysis failed',
                    'message': 'Could not analyze the uploaded file'
                }), 500
            
            # Prepare response
            api_result = {
                'success': True,
                'summary': analyzer.get_analysis_summary(),
                'issues': analyzer._all_issues(),
                'fixes_available': len(analyzer.fixes) > 0,
                'message': f"File {file.filename} analyzed successfully",
                'fixes_applied': len(analyzer.fixes)
            }
            
            # If auto_fix is enabled, save the fixed file and return it
            if auto_fix:
                fixed_file_path = os.path.join(temp_dir, f"fixed_{file.filename}")
                try:
                    # Use the export_fixed method to save the corrected file
                    export_result = analyzer.export_fixed(fixed_file_path)
                    
                    # Verify file exists
                    if os.path.exists(fixed_file_path):
                        # Return the fixed file for download with proper headers
                        response = send_file(
                            fixed_file_path,
                            as_attachment=True,
                            download_name=f"fixed_{file.filename}",
                            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                        )
                        
                        # Add additional headers for file downloads
                        response.headers['Content-Length'] = os.path.getsize(fixed_file_path)
                        response.headers['X-File-Name'] = f"fixed_{file.filename}"
                        response.headers['X-File-Size'] = os.path.getsize(fixed_file_path)
                        
                        return response
                    else:
                        # If export failed somehow, return the analysis results
                        return jsonify(api_result)
                        
                except Exception as e:
                    print(f"Error exporting fixed file: {e}")
                    # If export fails, return the analysis results without the file
                    api_result['export_error'] = str(e)
                    return jsonify(api_result)
            
            return jsonify(api_result)
            
        finally:
            # Clean up temporary files
            for temp_file in [temp_path, fixed_file_path]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Server error during file validation'
        }), 500


@app.route('/api/export-fixed', methods=['POST'])
def export_fixed():
    """Export fixed Excel file"""
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
        
        try:
            # Create analyzer and run analysis
            analyzer = CodefyAnalyzer(file_path=temp_path)
            analyzer.run()  # Run analysis first
            
            # Create output path for the fixed file
            output_path = os.path.join(temp_dir, f"fixed_{file.filename}")
            
            # Export the fixed file
            export_result = analyzer.export_fixed(output_path)
            
            # Return the fixed file for download with proper headers
            response = send_file(
                output_path,
                as_attachment=True,
                download_name=f"fixed_{file.filename}",
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            # Add additional headers for file downloads
            response.headers['Content-Length'] = os.path.getsize(output_path)
            response.headers['X-File-Name'] = f"fixed_{file.filename}"
            response.headers['X-File-Size'] = os.path.getsize(output_path)
            
            return response
            
        finally:
            # Clean up temporary files
            for temp_file in [temp_path, output_path]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Server error during file export'
        }), 500


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current analyzer settings"""
    return jsonify({
        'success': True,
        'message': 'Settings endpoint not implemented in core version'
    })


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update analyzer settings"""
    return jsonify({
        'success': True,
        'message': 'Settings endpoint not implemented in core version'
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)