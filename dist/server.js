/*
 * Simple local server for CodefyERP Data Validation System
 * This server serves the static files and provides a proxy to the Python API
 */

const express = require('express');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');

const app = express();
const PORT = 3000;
const API_PORT = 5000;

// Enable CORS for all routes
app.use(cors());

// Serve static files from the root directory
app.use(express.static(path.join(__dirname)));

// Proxy API requests to the Python server
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

// Route to serve the main page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'Temp', 'index.html'));
});

// Handle all other routes by serving index.html (for client-side routing)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'Temp', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`CodefyERP Data Validation System Server running at http://localhost:${PORT}`);
  console.log(`\nTo use the full validation features:`);
  console.log(`1. Make sure the Python API server is running on port ${API_PORT}`);
  console.log(`2. Open your browser and go to http://localhost:${PORT}`);
  console.log(`\nTo start the Python API server:`);
  console.log(`   cd Statics/PY`);
  console.log(`   python api_server.py`);
});