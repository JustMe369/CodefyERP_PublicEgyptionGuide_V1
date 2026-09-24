/**
 * Excel Analyzer API Route Module
 * Handles Excel file analysis requests
 */

const express = require('express');
const router = express.Router();
const multer = require('multer');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Setup multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, os.tmpdir());
  },
  filename: (req, file, cb) => {
    cb(null, `excel-${Date.now()}${path.extname(file.originalname)}`);
  }
});

const upload = multer({ 
  storage: storage,
  limits: { fileSize: 50 * 1024 * 1024 } // 50MB file size limit
});

// POST /api/excel-analyzer/analyze
router.post('/analyze', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ 
      success: false,
      error: 'No file uploaded' 
    });
  }

  // Path to the Python analyzer script
  const pythonScriptPath = path.join(__dirname, '..', 'Statics', 'PY', 'CodefyExcelAnalyzer_V11.3.1.py');
  
  // Execute the Python analyzer with the uploaded file
  const pythonProcess = spawn('python', [pythonScriptPath, '--analyze', req.file.path]);

  let stdout = '';
  let stderr = '';

  pythonProcess.stdout.on('data', (data) => {
    stdout += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    stderr += data.toString();
  });

  pythonProcess.on('close', (code) => {
    // Clean up the uploaded file
    fs.unlinkSync(req.file.path);

    if (code !== 0) {
      console.error('Python process exited with code:', code);
      console.error('Error output:', stderr);
      return res.status(500).json({
        success: false,
        error: `Python analyzer failed with code ${code}`,
        details: stderr
      });
    }

    try {
      // Parse the output from the Python script
      const result = JSON.parse(stdout);
      res.status(200).json(result);
    } catch (parseError) {
      // If parsing fails, return an error
      console.error('Failed to parse Python output:', parseError);
      res.status(500).json({
        success: false,
        error: 'Failed to parse analyzer output',
        details: stdout
      });
    }
  });
});

// Health check endpoint
router.get('/health', (req, res) => {
  res.status(200).json({ 
    status: 'healthy',
    message: 'Excel analyzer service is running'
  });
});

module.exports = router;
/*
 * Simple local server for CodefyERP Data Validation System
 * This server serves the static files and provides a proxy to the Python API
 */

const express = require('express');
const path = require('path');
const cors = require('cors');
const multer = require('multer');
const fs = require('fs');
const os = require('os');

const app = express();
const PORT = 3000;
const API_PORT = 5000;

// Setup multer for file uploads
const upload = multer({ dest: os.tmpdir() });

// Rate limiting
const rateLimit = require('express-rate-limit');
const session = require('express-session');

// Rate limiting middleware
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again after 15 minutes'
});
app.use(limiter);

// Session configuration
app.use(session({
  secret: 'codefy_erp_secret_key', // In production, this should be in an environment variable
  resave: false,
  saveUninitialized: false,
  cookie: { 
    secure: false, // Set to true if using HTTPS
    httpOnly: true,
    maxAge: 24 * 60 * 60 * 1000 // 24 hours
  }
}));

// Middleware
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Import API routes
const excelAnalyzerRoutes = require('./api/excel-analyzer-express'); // Changed to the Express route file

// Middleware for API routes
app.use('/api/excel-analyzer', excelAnalyzerRoutes);

// Proxy other API requests to the Python server
app.use('/api', createProxyMiddleware({
  target: `http://localhost:${API_PORT}`,
  changeOrigin: true,
  pathRewrite: {
    '^/api': '/api', // Remove the /api prefix when forwarding
  },
  onProxyReq: (proxyReq, req, res) => {
    console.log(`Proxying request: ${req.method} ${req.url} -> http://localhost:${API_PORT}${req.url}`);
  },
  onProxyRes: (proxyRes, req, res) => {
    console.log(`Response status: ${proxyRes.statusCode}`);
    // Add CORS headers to proxied responses
    proxyRes.headers['Access-Control-Allow-Origin'] = '*';
    proxyRes.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS';
    proxyRes.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization';
  }
}));

// Serve main page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'Temp', 'index.html'));
});

// Serve section templates
app.get('/section/:name', (req, res) => {
  const section = req.params.name;
  const sectionPath = path.join(__dirname, 'Temp', 'sections', `${section}.html`);
  
  fs.access(sectionPath, fs.constants.F_OK, (err) => {
    if (err) {
      res.status(404).send('Section not found');
    } else {
      res.sendFile(sectionPath);
    }
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ 
    success: false,
    error: 'Internal server error',
    message: err.message
  });
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`CodefyERP Data Validation System Server running at http://localhost:${PORT}`);
  console.log(`\nTo use the full validation features:`);
  console.log(`1. Make sure Python and required packages are installed`);
  console.log(`2. Open your browser and go to http://localhost:${PORT}`);
  console.log(`\nExcel Analyzer API available at http://localhost:${PORT}/api/excel-analyzer`);
  console.log(`Python analyzer capabilities now integrated with enhanced routing!`);
});