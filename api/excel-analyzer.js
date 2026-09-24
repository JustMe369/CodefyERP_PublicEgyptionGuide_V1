/* eslint-disable no-undef */
/* Vercel Serverless API - Excel Analyzer Endpoint */
/* Handles Excel file validation through Python API */

const path = require('path');
const os = require('os');
const { promises: fsPromises, createReadStream } = require('fs');
const { join } = require('path');
const formidable = require('formidable');
const FormData = require('form-data');
const { Buffer } = require('buffer');
const fetch = (...args) => import('node-fetch').then(({ default: nodeFetch }) => nodeFetch(...args));

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

  if (req.method !== 'POST') {
    res.status(405).json({ error: `Method ${req.method} not allowed` });
    return;
  }

  // Check if this is a download request
  const isDownloadRequest = req.query.download === 'true';
  
  const uploadDir = await fsPromises.mkdtemp(join(os.tmpdir(), 'codefy-upload-'));
  let uploadedFile;
  let tempFilePath;

  // Parse the incoming form data
  const form = formidable({
    uploadDir,
    keepExtensions: true,
    maxFiles: 1,
    maxFileSize: 10 * 1024 * 1024, // 10 MB
    filter: (part) => {
      const allowedTypes = /xlsx|xls|csv/;
      const extname = allowedTypes.test(path.extname(part.originalFilename || '').toLowerCase());
      const mimetype = allowedTypes.test(part.mimetype || '');
      
      return extname && mimetype;
    }
  });

  try {
    // Parse the request to get the file
    const [fields, files] = await form.parse(req);
    
    if (!files.file || files.file.length === 0) {
      res.status(400).json({ error: 'No file uploaded' });
      return;
    }

    uploadedFile = Array.isArray(files.file) ? files.file[0] : files.file;
    
    // Check if this is a download request
    if (isDownloadRequest) {
      // Directly serve the uploaded file for download
      res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
      const downloadName = path.basename(uploadedFile.originalFilename || 'uploaded-file.xlsx').replace(/"/g, '');
      res.setHeader('Content-Disposition', `attachment; filename="${downloadName}"`);
      
      const fileStream = createReadStream(uploadedFile.filepath);
      fileStream.pipe(res);
      return;
    }
    
    const pythonApiUrl = process.env.PYTHON_API_URL;
    if (!pythonApiUrl) {
      res.status(503).json({
        success: false,
        error: 'Excel analyzer service is not configured',
        message: 'Set PYTHON_API_URL to a deployed Python analyzer service.'
      });
      return;
    }

    const validateEndpoint = `${pythonApiUrl}/api/validate-excel`;
    
    // Read the uploaded file
    const fileData = await fsPromises.readFile(uploadedFile.filepath);
    
    // Create a temporary file path
    const tempFileName = `temp_excel_analysis_${Date.now()}${path.extname(uploadedFile.originalFilename || '')}`;
    tempFilePath = join(uploadDir, tempFileName);
    
    // Write the file to temporary location
    await fsPromises.writeFile(tempFilePath, fileData);
    
    // Create a new form data for the Python API request
    const formData = new FormData();
    
    // Append the file to form data using a file stream
    formData.append('file', createReadStream(tempFilePath), {
      filename: uploadedFile.originalFilename || tempFileName,
      contentType: uploadedFile.mimetype || 'application/octet-stream'
    });
    
    // Call the Python API using Node.js compatible form data
    const response = await fetch(validateEndpoint, {
      method: 'POST',
      body: formData,
      headers: formData.getHeaders(),
      signal: AbortSignal.timeout(30000)
    });
    
    if (!response.ok) {
      throw new Error(`Python API responded with status ${response.status}`);
    }
    
    // Check if response is JSON or binary (for file download)
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')) {
      // This is a file download response - get the binary content
      const buffer = Buffer.from(await response.arrayBuffer());
      
      // Set proper headers for Excel file download
      res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
      res.setHeader('Content-Disposition', `attachment; filename="fixed_${path.basename(uploadedFile.originalFilename || 'file.xlsx')}"`);
      res.setHeader('Content-Length', buffer.length);
      
      // Send the binary Excel file
      res.send(buffer);
    } else {
      // This is a JSON response
      const result = await response.json();
      
      // Clean up the temporary file
      // Return the result to the client
      res.status(200).json(result);
    }
  } catch (error) {
    console.error('Excel Analyzer API Error:', error);
    res.status(error.name === 'TimeoutError' ? 504 : 500).json({
      success: false,
      error: error.message || 'Internal server error',
      message: 'Error during Excel validation'
    });
  } finally {
    await Promise.allSettled([
      uploadedFile?.filepath ? fsPromises.rm(uploadedFile.filepath, { force: true }) : Promise.resolve(),
      tempFilePath ? fsPromises.rm(tempFilePath, { force: true }) : Promise.resolve(),
      fsPromises.rm(uploadDir, { recursive: true, force: true })
    ]);
  }
}

