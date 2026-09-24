/**
 * Simple local server for CodefyERP Data Validation System
 * This server serves the static files and provides a proxy to the Python API
 */

const express = require('express');
const path = require('path');
const cors = require('cors');
const multer = require('multer');
const fs = require('fs');
const os = require('os');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = 3000;
const API_PORT = 5000;

// Setup multer for file uploads
const upload = multer({ dest: os.tmpdir() });

// Rate limiting (optional in local dev)
try {
  const rateLimit = require('express-rate-limit');
  const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
    message: 'Too many requests from this IP, please try again after 15 minutes'
  });
  app.use(limiter);
} catch (e) {
  // express-rate-limit not installed, proceed without it
}

// Session configuration (optional in local dev)
try {
  const session = require('express-session');
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
} catch (e) {
  // express-session not installed, proceed without it
}

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
app.use('/Statics', express.static(path.join(__dirname, 'Statics')));
app.use('/Temp', express.static(path.join(__dirname, 'Temp')));
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use(express.static(__dirname));

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

app.listen(PORT, () => {
  console.log(`CodefyERP Data Validation System Server running at http://localhost:${PORT}`);
  console.log(`\nTo use the full validation features:`);
  console.log(`1. Make sure Python and required packages are installed`);
  console.log(`2. Open your browser and go to http://localhost:${PORT}`);
  console.log(`\nExcel Analyzer API available at http://localhost:${PORT}/api/excel-analyzer`);
  console.log(`Python analyzer capabilities now integrated with enhanced routing!`);
});