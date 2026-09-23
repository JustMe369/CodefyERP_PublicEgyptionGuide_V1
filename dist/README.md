# CodefyERP Data Validation System

This repository contains the CodefyERP system with an integrated data validation tool for Excel files before import.

## Overview

The CodefyERP Data Validation System is an advanced Excel data validation tool designed specifically for Egyptian business operations. It provides comprehensive validation, analysis, and data quality improvement capabilities with a focus on Egyptian business requirements.

## Features

### Core Validation Features
- **Egyptian Phone Number Validation**: Validates Egyptian mobile numbers (010, 011, 012, 015 prefixes)
- **Date Format Validation**: Supports multiple date formats with automatic conversion to standard format
- **Data Quality Scoring**: Assigns quality scores (0-100) based on various validation criteria
- **Issue Detection**: Identifies and categorizes issues as critical, warning, or informational
- **Automated Fixes**: Applies automatic corrections for common issues with audit trails

### Advanced Features

#### 1. Shift Engine
- **Shift Pattern Recognition**: Identifies shift types (Morning, Evening, Night, Day, Special)
- **Ordinal Processing**: Handles shift ordinals (Primary, Secondary, Tertiary, Express, VIP)
- **Conflict Detection**: Identifies conflicts between scheduled times and shift assignments
- **Automatic Improvement Suggestions**: Enhances shift descriptions with proper formatting

#### 2. Time Control Center
- **Time Range Validation**: Ensures times fall within specified ranges
- **Duration Calculation**: Computes work durations automatically
- **Overtime Tracking**: Monitors overtime hours and compliance
- **Attendance Recording**: Manages employee attendance records

#### 3. Main Suppliers Form
- **Egyptian Tax ID Validation**: Validates 14-digit Egyptian tax IDs
- **Supplier Category Management**: Organizes suppliers by category (Raw Materials, Services, Equipment, etc.)
- **Payment Terms Support**: Handles various payment terms (Cash, Credit, Net 7/15/30/60)
- **Credit Limit Management**: Tracks and validates credit limits
- **Delivery Time Monitoring**: Manages expected delivery times

#### 4. Vehicle and Capacity Management
- **Capacity Validation**: Ensures vehicle capacity aligns with vehicle type
- **Insurance Expiry Tracking**: Monitors insurance expiry dates
- **Maintenance Scheduling**: Tracks maintenance schedules
- **Status Management**: Manages vehicle operational status

#### 5. Working Days Normalization
- **Arabic Day Support**: Recognizes Arabic day names and abbreviations
- **Custom Day Separators**: Handles various separator formats
- **Order Normalization**: Orders days according to Egyptian work week

## Deployment Options

### Option 1: Local Development (Full Functionality)

1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Start the API server:
   ```
   cd Statics/PY
   python api_server.py
   ```

4. Open the main index.html file in your browser

### Option 2: Vercel Deployment (Frontend Only with Simulated API)

1. Push the codebase to a Git repository (GitHub, GitLab, or Bitbucket)
2. Import the repository into Vercel
3. The system will automatically deploy with simulated API functionality
4. For full Python-powered validation, run the local API server separately

See [README.VERCEL.md](README.VERCEL.md) for detailed Vercel deployment instructions.

## Usage

### Running the Validation Tool
1. Start the API server:
   ```
   cd Statics/PY
   python api_server.py
   ```

2. Open the main index.html file in your browser
3. Navigate to the "Bulk Import" section
4. Select the "Validation" tab
5. Upload your Excel file
6. Review the analysis results
7. Download the cleaned file if needed
8. Proceed with the import to CodefyERP

### Using Advanced Features
- **Shift Engine**: Access through the dedicated tab in the validation interface
- **Time Control**: Available in the time management section
- **Supplier Management**: Use the suppliers form for managing supplier data

## API Endpoints

### Local Development Server
- `GET /api/health`: Health check endpoint
- `POST /api/validate`: Validate uploaded Excel file
- `POST /api/download-cleaned`: Download cleaned version of file

### Vercel Serverless Functions (Simulated)
- `GET /api/health`: Health check endpoint
- `POST /api/validate`: Validate uploaded Excel file (simulated)
- `POST /api/download-cleaned`: Download cleaned version of file (simulated)

## File Structure

```
CodefyERP/
├── Temp/
│   ├── index.html              # Main application page
│   └── section-data-validation.html  # Dedicated validation interface
├── Statics/
│   ├── PY/
│   │   ├── CodefyDataValidator.py  # Core validation engine
│   │   ├── api_server.py       # Flask API server
│   │   └── start_api.py        # API startup script
│   └── JS/
│       ├── scripts.js          # Main JavaScript functionality
│       └── validation-tool.js  # Validation-specific scripts
├── api/
│   └── serverless-api.js      # Vercel-compatible API
├── requirements.txt            # Python dependencies
├── start_server.bat           # Windows startup script
├── start_server.sh            # Linux/Mac startup script
├── vercel.json                # Vercel configuration
└── package.json               # NPM configuration

## Configuration

The system is pre-configured for Egyptian business operations. Customization options include:
- Adding new validation rules in CodefyDataValidator.py
- Modifying column specifications in the ERP_COLUMN_SPEC dictionary
- Extending the shift pattern recognition in SHIFT_BASE_PATTERNS



## License

This project is licensed under the MIT License - see the LICENSE file for details.