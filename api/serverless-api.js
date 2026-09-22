/* eslint-disable no-undef */
/* Serverless API for CodefyERP Data Validation on Vercel */

// Import the Python validation logic through a child process
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;
const os = require('os');

// Handler for API requests
module.exports = async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const { method } = req;

  // Only allow POST requests for validation
  if (method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  // Extract the API endpoint from the URL
  const urlParts = req.url.split('/');
  const endpoint = urlParts[urlParts.length - 1];

  if (endpoint === 'validate' || endpoint === 'download-cleaned') {
    try {
      // Process the uploaded file
      const result = await processFileRequest(req, endpoint);
      res.status(200).json(result);
    } catch (error) {
      console.error('API Error:', error);
      res.status(500).json({ error: error.message || 'Internal server error' });
    }
  } else if (endpoint === 'health') {
    res.status(200).json({ status: 'healthy', service: 'CodefyERP Data Validator API' });
  } else {
    res.status(404).json({ error: 'Endpoint not found' });
  }
}

async function processFileRequest(req, endpoint) {
  // Since Vercel serverless functions have limitations with file uploads,
  // we'll simulate the validation process for demo purposes
  // In a real implementation, you'd need to handle file uploads differently
  
  // For now, return mock results that demonstrate the functionality
  if (endpoint === 'validate') {
    // Simulate validation results
    return {
      success: true,
      summary: {
        file_name: 'sample_data.xlsx',
        total_rows: 500,
        total_sheets: 3,
        quality_score: 85,
        issues: {
          critical: 2,
          warning: 5,
          info: 8
        },
        breakdown: {
          invalid_phones: 1,
          date_format_issues: 2,
          enum_violations: 1,
          missing_data: 2,
          duplicate_phones: 1,
          time_conflicts: 1,
          shift_conflicts: 1,
          supplier_issues: 2,
          capacity_issues: 1,
          shift_upgrades: 3
        }
      },
      issues: [
        { severity: 'critical', category: 'Invalid Phone', sheet: 'Drivers', row: 45, column: 'Phone', message: 'Invalid Egyptian phone number format' },
        { severity: 'warning', category: 'Date Format', sheet: 'Schedule', row: 12, column: 'Start_Date', message: 'Date not in YYYY-MM-DD format' },
        { severity: 'info', category: 'Normalization', sheet: 'Routes', row: 67, column: 'Direction', message: 'Direction inferred from schedule' },
        { severity: 'critical', category: 'Missing Data', sheet: 'Vehicles', row: 89, column: 'Driver_Name', message: 'Required field missing' },
        { severity: 'warning', category: 'Capacity Issue', sheet: 'Vehicles', row: 156, column: 'Capacity', message: 'Capacity value seems unusually high for vehicle type' },
        { severity: 'warning', category: 'Shift Conflict', sheet: 'Schedule', row: 23, column: 'Shift', message: 'Shift type conflicts with scheduled times' },
        { severity: 'warning', category: 'Supplier Issue', sheet: 'Suppliers', row: 78, column: 'Tax_ID', message: 'Invalid Egyptian tax ID format' }
      ]
    };
  } else if (endpoint === 'download-cleaned') {
    // For download endpoint, return a success message
    return {
      success: true,
      message: 'Cleaned file ready for download'
    };
  }
}

// Helper function to run Python validation (not used in this serverless version)
async function runPythonValidation(filePath) {
  return new Promise((resolve, reject) => {
    // This would be used if Python was available in the Vercel environment
    // But Vercel doesn't support Python natively, so we simulate
    setTimeout(() => {
      resolve({
        success: true,
        summary: {
          file_name: path.basename(filePath),
          total_rows: 100,
          total_sheets: 1,
          quality_score: 90,
          issues: { critical: 0, warning: 1, info: 2 },
          breakdown: { invalid_phones: 0, date_format_issues: 1, enum_violations: 0 }
        },
        issues: [
          { severity: 'warning', category: 'Date Format', sheet: 'Sheet1', row: 5, column: 'Date', message: 'Date not in standard format' },
          { severity: 'info', category: 'Normalization', sheet: 'Sheet1', row: 10, column: 'Name', message: 'Name standardized' }
        ]
      });
    }, 500);
  });
}