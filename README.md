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



## Administration and PostgreSQL (PHP guide)

The PHP guide includes a PostgreSQL-backed administration area at `/admin/`. Administrators can manage the site identity and home-page copy, create and order sections, edit their titles, descriptions, icons, accent colors and publication status, and build page bodies with a structured visual composer (headings, paragraphs, lists, steps, callouts, images, tables, code, Mermaid diagrams, links and dividers). Existing chapter pages retain their interactive PHP widgets in **Built-in template** mode; switching a page to **Visual editor** replaces that chapter body with its authored blocks and can be reversed in the section editor. New sections use the visual editor and receive a database-backed public URL. The admin area also manages administrator/editor accounts and keeps an audit trail.

### Local setup with XAMPP on Windows

1. Provision your existing local PostgreSQL service and create the database/schema:
   ```powershell
   .\scripts\setup-postgres.ps1
   ```
   It securely prompts for the PostgreSQL `postgres` password, creates `codefy_guide` plus the restricted `codefy_app` role, applies the migration, and writes generated credentials to the ignored `.env` file. It stops if a Codefy database or role already exists.
   If provisioning succeeded but migration application failed, the generated roles and `.env` are already in place. Resume safely with:
   ```powershell
   .\scripts\migrate-postgres.ps1
   ```
   The migration runner forces UTF-8 client encoding for the Arabic seed data and can be rerun after a failed transaction.
2. Restart Apache so XAMPP loads the enabled `pdo_pgsql` extension.
3. Create the first administrator:
   ```powershell
   .\scripts\create-admin.ps1
   ```
   The helper prompts for email, display name, role, and password using a secure password prompt. Use a unique password of at least 14 characters and no more than 72 UTF-8 bytes. Account creation requires the migration and `.env` connection. There is no public account-registration endpoint.
4. Open `http://localhost/CaodefyERPGuide/app/admin/` (adjust the URL to match your Apache setup).

The repository also includes `compose.yaml` and `.env.example` for an isolated Docker database. In that setup, start `postgres`, run `database-setup`, then apply the migration from the mounted `/database` directory.

### Production database

Set `CODEFY_DATABASE_DSN` (or `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, and `PGPASSWORD`) in the PHP runtime's secret environment. Use the application role named `codefy_app` with managed PostgreSQL/TLS, and run migrations as a separate owner account. If TLS terminates at a reverse proxy, set `CODEFY_SECURE_COOKIE=true`. Apply migration files in version order. Database credentials are never sent to browser JavaScript. If PostgreSQL is temporarily unavailable, public guide pages fall back to their PHP defaults; the admin panel requires the database.

### Supabase setup

The Supabase project already provides its `postgres` database; the setup below creates the Codefy schema and restricted runtime role inside it. Rotate any database password shared in chat before connecting. From PowerShell, run:

```powershell
.\scripts\setup-supabase.ps1
```

The script securely prompts for the rotated database password, uses TLS with the supplied IPv4 transaction pooler, applies migrations in order, verifies the migration records, creates a non-superuser `codefy_app` login, verifies it through Supavisor with the required `codefy_app.<project-ref>` username, and updates the ignored `.env` only after success. Supabase's transaction pooler does not support prepared statements, so the PHP app enables emulated PDO prepares. Create an administrator afterward with `.\scripts\create-admin.ps1`. Never put the database password in frontend JavaScript, a committed file, or a public environment variable.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
