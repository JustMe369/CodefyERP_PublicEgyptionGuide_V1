# CodefyERP Excel Analyzer Integration

## Overview

This integration brings the full power of the **CodefyExcelAnalyzer_V11.3.1** Python script into the web-based validation tab. The system now supports comprehensive Excel/CSV analysis, validation, and repair with Egyptian fleet data capabilities.

## 🌊 Core Features Integrated

### 1. 📥 Advanced File Loading
- Supports `.xlsx`, `.xlsm`, `.csv`, `.tsv`, `.txt` files
- Automatic encoding detection (UTF-8, CP1256, ISO-8859-6, Latin1)
- Automatic delimiter detection for CSV files
- Preserves leading zeros in phone numbers
- Converts numeric strings to appropriate data types

### 2. 🎯 Bilingual Header Detection
- Scans first 35 rows to find header rows
- Supports Arabic and English column aliases (~200+ mappings)
- Normalizes Arabic text (diacritics removal, character unification)
- Maps to canonical ERP column names

### 3. 📞 Egyptian Phone Validation
- Validates Egyptian phone numbers (11 digits, prefixes: 010/011/012/015)
- 6 validation statuses: empty, ok, fixable, invalid, short, arabic
- Auto-fixes recoverable cases (12/14 digit numbers, Arabic digits, etc.)

### 4. 📅 Date Validation with Arabic Support
- Handles 25+ date formats including Arabic month names
- Supports both Arabic and English month names
- Validates Egyptian date formats
- Normalizes to standard YYYY-MM-DD format

### 5. 🌊 Shift Engine
- Merges shift base patterns with ordinal suffixes
- Supports Arabic shift names and ordinals
- Standardizes to canonical shift names

### 6. ⏰ Time Conflict Resolution
- Detects time conflicts between pickup/dropoff times
- Auto-resolves with configurable offsets
- Supports 12/24 hour format conversion

### 7. 🔁 Duplicate & Conflict Detection
- Phone → multiple drivers conflicts
- Driver → multiple phones conflicts
- Duplicate phone detection
- Unique shift name validation

### 8. 🏢 Supplier Normalization
- Internal supplier identification (e.g., "الجودة", "الجوده")
- Automatically clears supplier fields for internal suppliers
- Sets employment type to "employee"

### 9. 📆 Working Days Normalization
- Converts Arabic/English day names to canonical format
- Supports mixed separators and conjunctions
- Maintains standard day ordering (sun→sat)

### 10. 🧭 Direction Inference
- Infers schedule direction from schedule names
- Supports Arabic direction keywords ("ذهاب", "عودة")
- Auto-fixes conflicting directions

### 11. 🎯 ERP Compatibility Check
- Validates required columns existence
- Checks enum values against allowed lists
- Identifies and removes rejected columns

### 12. ⏳ Expiry Alerts
- Monitors license and vehicle expiry dates
- Flags expired items as critical
- Warns about items expiring within 90 days

### 13. ❓ Missing Data Detection
- Flags empty cells in critical columns
- Provides detailed missing data reports

### 14. 🚩 Red Flag System
- Identifies cells that cannot be safely auto-fixed
- Highlights problematic cells in exports
- Preserves original values while logging issues

### 15. 🎯 Supplier-Based Row Reordering
- Groups rows by supplier
- Supports pinning suppliers to top/bottom
- Maintains data integrity during reordering

## 📊 Quality Scoring System

The system calculates a quality score (0-100) based on various factors:
- Invalid phones: -3 pts each (max -24)
- Short phones: -2 pts each (max -15) 
- Driver conflicts: -4 pts each (max -12)
- Phone conflicts (hard): -7 pts each (max -16)
- Phone conflicts (soft): -1 pt each (max -6)
- Duplicate phones (hard): -5 pts each (max -10)
- Enum violations: -1 pt each (max -6)
- ERP issues: -2 pts each (max -7)
- Time conflicts: -2 pts each (max -18)
- Unparseable dates: -4 pts each (max -18)
- Fixable dates: -2 pts each (max -12)

**Grades:** ≥90 EXCELLENT, ≥75 GOOD, ≥60 FAIR, ≥40 POOR, <40 CRITICAL

## 🏗️ System Architecture

### Frontend Components
- **Validation Tab** (`Temp/sections/bulk-import.html`): User interface for file upload and results display
- **JavaScript Handler** (`Statics/JS/scripts.js`): Manages file uploads and displays results
- **Real-time Updates**: Shows progress, scores, and issues

### Backend Components
- **Node.js API** (`api/excel-analyzer.js`): Handles file uploads and forwards to Python
- **Python API Server** (`Statics/PY/api_server.py`): Runs the analyzer and returns results
- **Core Analyzer** (`api/excel_analyzer_core.py`): Streamlined validation engine

### Communication Flow
1. User uploads file via frontend validation tab
2. File sent to Node.js API endpoint `/api/excel-analyzer/validate`
3. Node.js forwards file to Python API server at `http://localhost:5000/api/validate-excel`
4. Python analyzer processes file and returns JSON results
5. Results displayed in frontend with detailed breakdown

## 🚀 Getting Started

### Prerequisites
```bash
# Install Python dependencies
pip install pandas openpyxl numpy chardet flask python-dateutil

# Install Node.js dependencies
npm install
```

### Running the System
1. Start the Python API server:
   ```bash
   cd Statics/PY
   python api_server.py
   ```

2. Start the main Node.js server:
   ```bash
   npm start
   ```

3. Access the validation tab at `http://localhost:3000/#validation`

### Using the Validation Tab
1. Navigate to the "Validation" tab
2. Upload an Excel/CSV file containing fleet data
3. View the analysis results including:
   - Quality score
   - Issue breakdown by severity
   - Detailed issue list
   - Applied fixes
   - Red flags
4. Download fixed file or detailed reports as needed

## 🛡️ Safety Features

- **Non-destructive**: Never modifies source files
- **Full audit trail**: Every change logged in audit sheet
- **Phone protection**: Numbers <10 digits never changed
- **Arabic text preservation**: Never deleted, only flagged
- **Forward compatibility**: Settings load with defaults
- **Export guard**: Blocks export with unresolved critical issues

## 📤 Export Formats Available

- **Fixed Excel**: Corrected file with audit log sheet
- **Fixed CSV**: UTF-8-SIG CSV format
- **HTML Report**: Standalone dark-themed report
- **Issues Excel**: Multi-sheet issue breakdown
- **Issues CSV**: Flat CSV of all issues
- **JSON Output**: Machine-readable results
- **TXT Reports**: Plain text versions

## 🌍 Egyptian Data Support

The system is specifically designed for Egyptian fleet operations:
- **Phone validation**: Egyptian 11-digit format
- **Arabic month names**: Full support for Arabic months
- **Working days**: Arabic day name recognition
- **Supplier names**: Common Egyptian supplier names
- **Direction keywords**: Arabic direction indicators
- **Shift names**: Arabic shift nomenclature

## 📋 API Endpoints

- `POST /api/excel-analyzer/validate` - Validate uploaded file
- `POST /api/excel-analyzer/validate-and-fix` - Validate and fix file

## 🚀 Performance

The system is optimized for:
- Large Excel files (tested with thousands of rows)
- Fast validation (typically under 30 seconds)
- Memory efficiency
- Responsive UI during processing
- Concurrent processing capability

## 📞 Support

For issues or questions about the Excel analyzer integration, please contact the development team.