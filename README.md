# CodefyERP Data Validation Tool

This repository contains the CodefyERP system with an integrated data validation tool for Excel files before import.

## Overview

The CodefyERP Data Validation Tool provides comprehensive analysis and validation of Excel files before they are imported into the CodefyERP system. It includes:

- Advanced validation for Egyptian phone numbers
- Date format validation and correction
- Data quality scoring
- Issue detection and reporting
- Automated fixes for common issues
- Pre-upload validation to prevent import errors

## Features

### Data Validation
- Egyptian phone number validation with proper carrier prefixes (010, 011, 012, 015)
- Date format validation and automatic conversion to standard format
- Missing data detection for critical fields
- Enum value validation against allowed sets
- Time conflict detection and resolution

### Automated Corrections
- Phone number formatting fixes
- Date format standardization
- Time format normalization
- Schedule direction inference
- Working day normalization

### Quality Assessment
- Overall quality scoring (0-100)
- Detailed issue categorization (critical, warning, info)
- Summary statistics for quick assessment
- Export of cleaned files with applied fixes

## Components

### Frontend
- Located in the bulk import section of index.html
- Drag-and-drop file upload interface
- Real-time analysis results display
- Issue visualization with severity indicators
- Download cleaned file functionality

### Backend
- Python-based validation engine (`CodefyDataValidator.py`)
- Flask API server (`api_server.py`) for handling requests
- Comprehensive data analysis algorithms
- Excel file processing capabilities

## Setup Instructions

1. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Start the API server:
   ```
   cd Statics/PY
   python start_api.py
   ```

3. Access the validation tool through the bulk import section of the main application

## API Endpoints

- `POST /api/validate` - Validate an uploaded Excel file
- `POST /api/download-cleaned` - Generate and download a cleaned version of the file
- `GET /api/health` - Health check endpoint

## Usage

1. Navigate to the Bulk Import section in the application
2. Use the validation tool to upload and analyze your Excel file
3. Review the analysis results and identified issues
4. Download the cleaned file if needed
5. Proceed with the import to CodefyERP

## Supported File Formats

- `.xlsx` (Excel Workbook)
- `.xls` (Excel 97-2003 Workbook)

## Validation Rules

### Phone Numbers
- Must be 11 digits
- Must start with valid Egyptian carrier prefixes (010, 011, 012, 015)
- Supports conversion from various formats (with country codes, missing leading zeros)

### Dates
- Standard format: YYYY-MM-DD
- Automatic conversion from common alternative formats
- Recognition of date-like values in text form

### Critical Fields
- Driver name
- Driver phone
- Plate number
- Shift
- Route
- All must be present for valid records

## Quality Scoring

The tool calculates a quality score from 0-100 based on:
- Number and severity of issues found
- Completeness of required data
- Consistency of data formats
- Adherence to business rules

## Troubleshooting

If the API server fails to start:
1. Ensure all dependencies are installed
2. Check that the required ports are available
3. Verify file permissions

For validation issues:
1. Check that Excel files follow the expected format
2. Ensure required columns are present
3. Verify data types match expected formats

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.