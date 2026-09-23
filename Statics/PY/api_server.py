#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask API server for CodefyERP Data Validation
Provides endpoints for Excel file validation and analysis
"""

import os
import sys
import json
import traceback
from datetime import datetime, timedelta
import re
import tempfile
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS  # Add CORS support
from werkzeug.utils import secure_filename
import pandas as pd
from openpyxl import load_workbook
from CodefyDataValidator import validate_excel_file

# Add the current directory to the Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the enhanced analyzer
from CodefyExcelAnalyzer_V11.3.1 import CodefyAnalyzer, SettingsManager

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

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Basic analysis endpoint using the enhanced analyzer."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only Excel files are allowed.'}), 400
        
        # Save the uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        # Initialize the enhanced analyzer
        settings_manager = SettingsManager()
        analyzer = CodefyAnalyzer(temp_path, settings=settings_manager)
        
        # Run the analysis
        report, fixes = analyzer.run()
        
        # Format the response
        response = {
            'status': 'success',
            'summary': analyzer.get_analysis_summary(),
            'issues': analyzer._all_issues(),
            'fixes': fixes,
            'report': report
        }
        
        # Clean up temporary file
        try:
            os.remove(temp_path)
        except:
            pass
        
        return jsonify(response)
        
    except Exception as e:
        app.logger.error(f"Error in analyze: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/deep_analyze', methods=['POST'])
def deep_analyze():
    """
    Enhanced analysis endpoint with advanced features like shift engine and time control
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only Excel files are allowed.'}), 400
        
        # Save the uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        # Get analysis options from request
        options = request.form.get('options', '{}')
        try:
            options = json.loads(options)
        except:
            options = {}
        
        # Initialize the enhanced analyzer with custom settings
        settings_manager = SettingsManager()
        
        # Update settings based on request options
        if 'shift_engine_enabled' in options:
            settings_manager.shift_engine_enabled = options['shift_engine_enabled']
        if 'time_conflict_enabled' in options:
            settings_manager.time_conflict_enabled = options['time_conflict_enabled']
        if 'time_conflict_offset' in options:
            settings_manager.time_conflict_offset = options['time_conflict_offset']
        
        analyzer = CodefyAnalyzer(temp_path, settings=settings_manager)
        
        # Run the deep analysis
        report, fixes = analyzer.run()
        
        # Format the response with enhanced data
        response = {
            'status': 'success',
            'summary': analyzer.get_analysis_summary(),
            'issues': analyzer._all_issues(),
            'fixes': fixes,
            'report': report,
            'analyzer_details': {
                'shift_engine_enabled': settings_manager.shift_engine_enabled,
                'time_conflict_enabled': settings_manager.time_conflict_enabled,
                'time_conflict_offset': settings_manager.time_conflict_offset
            }
        }
        
        # Clean up temporary file
        try:
            os.remove(temp_path)
        except:
            pass
        
        return jsonify(response)
        
    except Exception as e:
        app.logger.error(f"Error in deep_analyze: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Deep analysis failed: {str(e)}'}), 500

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

@app.route('/api/validate_sheet_structure', methods=['POST'])
def validate_sheet_structure():
    """
    Validate the structure of the Excel sheet against expected column names
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only Excel files are allowed.'}), 400
        
        # Save the uploaded file temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        # Load the workbook to inspect structure
        wb = load_workbook(temp_path, read_only=True)
        structure_analysis = {}
        
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            
            # Get the first few rows to identify headers
            headers = []
            for row in ws.iter_rows(min_row=1, max_row=5, values_only=True):
                # Look for the actual header row (skip empty rows)
                non_empty_values = [cell for cell in row if cell is not None and str(cell).strip() != '']
                if len(non_empty_values) > 2:  # If we have at least 3 non-empty cells, consider as potential header
                    headers = [str(cell) if cell is not None else '' for cell in row]
                    break
            
            # Analyze the data structure
            data_rows = 0
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                if any(cell is not None and str(cell).strip() != '' for cell in row):
                    data_rows += 1
                    if data_rows >= 10:  # Just sample first 10 data rows
                        break
            
            structure_analysis[sheet_name] = {
                'headers': headers,
                'total_rows': ws.max_row,
                'total_columns': ws.max_column,
                'data_rows_sample': data_rows,
                'has_headers': len([h for h in headers if h.strip() != '']) > 0
            }
        
        # Clean up temporary file
        try:
            os.remove(temp_path)
        except:
            pass
        
        return jsonify({
            'status': 'success',
            'structure': structure_analysis
        })
        
    except Exception as e:
        app.logger.error(f"Error in validate_sheet_structure: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Sheet structure validation failed: {str(e)}'}), 500

@app.route('/api/get_supported_columns', methods=['GET'])
def get_supported_columns():
    """
    Return the list of supported column names for ERP integration
    """
    # Define supported columns for Egyptian ERP system
    supported_columns = {
        'driver_info': [
            'driver_name', 'driver_phone', 'driver_license', 'driver_national_id'
        ],
        'supplier_info': [
            'supplier_name', 'supplier_phone', 'company_name', 'company_phone', 
            'company_address', 'company_email', 'contact_person', 'tax_id', 
            'bank_account', 'credit_limit', 'payment_terms', 'supplier_category',
            'delivery_time', 'min_order_value', 'discount_rate'
        ],
        'vehicle_info': [
            'plate_number', 'vehicle_type', 'capacity', 'fuel_type', 
            'vehicle_status', 'insurance_expiry', 'maintenance_date', 'last_inspection'
        ],
        'shift_schedule': [
            'shift', 'schedule', 'route', 'pickup_arrival', 'pickup_departure',
            'dropoff_arrival', 'dropoff_time', 'working_days', 'direction',
            'start_date', 'end_date', 'service_type'
        ],
        'operation_info': [
            'service_date', 'customer_name', 'customer_phone', 'pickup_location',
            'dropoff_location', 'passenger_count', 'special_requirements'
        ]
    }
    
    return jsonify({
        'status': 'success',
        'supported_columns': supported_columns
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    response = jsonify({
        'status': 'healthy', 
        'service': 'CodefyERP Data Validator API',
        'timestamp': datetime.now().isoformat()
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)