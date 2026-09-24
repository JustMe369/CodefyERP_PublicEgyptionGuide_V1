const express = require('express');
const multer = require('multer');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const FormData = require('form-data'); // Add form-data for Node.js

const router = express.Router();

// Set up multer for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const uploadDir = 'uploads/';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage: storage,
  fileFilter: (req, file, cb) => {
    const allowedTypes = /xlsx|xls|csv/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);

    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Only Excel and CSV files are allowed'));
    }
  }
});

// Endpoint to validate Excel/CSV files using Python analyzer
router.post('/validate', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const filePath = req.file.path;

  try {
    // Call the Python analyzer via HTTP request to the Python API server
    const pythonApiUrl = process.env.PYTHON_API_URL || 'http://localhost:5000';
    const validateEndpoint = `${pythonApiUrl}/api/validate-excel`;
    
    // Use node-fetch to make HTTP request to Python server
    const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));
    
    // Create form data for file upload
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    
    const response = await fetch(validateEndpoint, {
      method: 'POST',
      body: form
    });
    
    if (!response.ok) {
      throw new Error(`Python API responded with status ${response.status}`);
    }
    
    const result = await response.json();
    res.json(result);
  } catch (error) {
    console.error('Error in Excel validation:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message,
      message: 'Error during Excel validation'
    });
  } finally {
    // Clean up uploaded file
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }
  }
});

// Endpoint to validate and fix Excel/CSV files
router.post('/validate-and-fix', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const filePath = req.file.path;
  const autoFix = req.body.autoFix !== undefined ? req.body.autoFix : true;

  try {
    // Call the Python analyzer via HTTP request to the Python API server
    const pythonApiUrl = process.env.PYTHON_API_URL || 'http://localhost:5000';
    const validateEndpoint = `${pythonApiUrl}/api/validate-and-fix`;
    
    // Use node-fetch to make HTTP request to Python server
    const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));
    
    // Create form data for file upload
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    form.append('auto_fix', autoFix.toString());
    
    const response = await fetch(validateEndpoint, {
      method: 'POST',
      body: form
    });
    
    if (!response.ok) {
      throw new Error(`Python API responded with status ${response.status}`);
    }
    
    const result = await response.json();
    res.json(result);
  } catch (error) {
    console.error('Error in Excel validation and fixing:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message,
      message: 'Error during Excel validation and fixing'
    });
  } finally {
    // Clean up uploaded file
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }
  }
});

module.exports = router;