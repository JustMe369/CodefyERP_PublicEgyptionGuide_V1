# CodefyERP Data Validation System - Vercel Deployment

## Overview
The CodefyERP Data Validation System deployed on Vercel for Egyptian business operations. This system provides comprehensive validation, analysis, and data quality improvement capabilities with a focus on Egyptian business requirements.

## Deployment on Vercel

### Prerequisites
- A Vercel account
- Git repository with this codebase
- Node.js (for local development)

### Deployment Steps

1. **Prepare Your Repository**
   - Push this codebase to a Git repository (GitHub, GitLab, or Bitbucket)

2. **Deploy to Vercel**
   - Go to [Vercel](https://vercel.com)
   - Sign in and import your repository
   - Vercel will automatically detect this as a static site and deploy it
   - The API endpoints will be handled by the serverless functions in the `/api` directory

3. **Environment Configuration**
   - No special environment variables are needed for basic operation
   - The system will work with simulated data in the Vercel environment

### Local Development

For full functionality with Python backend:

1. Clone the repository:
   ```bash
   git clone <your-repository-url>
   cd codefyerp-data-validation
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the Python API server separately:
   ```bash
   cd Statics/PY
   pip install -r ../../requirements.txt
   python api_server.py
   ```

4. Open `index.html` in your browser (the system will automatically connect to the local API)

### Production Deployment Notes

- The Vercel deployment includes a simulated API that demonstrates the functionality
- For full Python-powered validation, you'll need to run the Python API server separately
- The system detects whether it's running locally or on Vercel and adjusts API endpoints accordingly
- All features (Shift Engine, Time Control Center, Suppliers Form) are available in the deployed version

## Features

### Core Validation Features
- **Egyptian Phone Number Validation**: Validates Egyptian mobile numbers (010, 011, 012, 015 prefixes)
- **Date Format Validation**: Supports multiple date formats with automatic conversion to standard format
- **Data Quality Scoring**: Assigns quality scores (0-100) based on various validation criteria
- **Issue Detection**: Identifies and categorizes issues as critical, warning, or informational

### Advanced Features

#### 1. Shift Engine
- **Shift Pattern Recognition**: Identifies shift types (Morning, Evening, Night, Day, Special)
- **Ordinal Processing**: Handles shift ordinals (Primary, Secondary, Tertiary, Express, VIP)
- **Conflict Detection**: Identifies conflicts between scheduled times and shift assignments

#### 2. Time Control Center
- **Time Range Validation**: Ensures times fall within specified ranges
- **Duration Calculation**: Computes work durations automatically
- **Attendance Recording**: Manages employee attendance records

#### 3. Main Suppliers Form
- **Egyptian Tax ID Validation**: Validates 14-digit Egyptian tax IDs
- **Supplier Category Management**: Organizes suppliers by category
- **Payment Terms Support**: Handles various payment terms

## API Endpoints (Simulated in Vercel)

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
│   │   └── api_server.py       # Flask API server
│   └── JS/
│       └── scripts.js          # Main JavaScript functionality
├── api/
│   └── serverless-api.js      # Vercel-compatible API
├── requirements.txt            # Python dependencies
└── vercel.json               # Vercel configuration
```

## Troubleshooting

- If you see "خطأ في الاتصال بالخادم" on Vercel, this is expected - the system will use simulated data
- For full Python-powered validation, run the local API server as described above
- The system automatically detects the environment and adjusts accordingly

## Support

For support with the Vercel deployment, please contact the development team.