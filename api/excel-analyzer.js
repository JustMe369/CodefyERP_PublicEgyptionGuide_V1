/* eslint-disable no-undef */
/* Vercel Serverless API - Excel Analyzer Endpoint */
/* Handles Excel file validation through Python API */

import path from 'path';
import os from 'os';
import { promises as fsPromises } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';
import formidable from 'formidable';
import FormData from 'form-data'; // Add form-data for Node.js compatibility
import { createReadStream } from 'fs';
import { Buffer } from 'buffer';

export default async function handler(req, res) {
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
  
  // Create uploads directory if it doesn't exist
  const uploadDir = join(process.cwd(), 'uploads');
  try {
    await fsPromises.access(uploadDir);
  } catch {
    await fsPromises.mkdir(uploadDir, { recursive: true });
  }

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

    const file = Array.isArray(files.file) ? files.file[0] : files.file;
    
    // Check if this is a download request
    if (isDownloadRequest) {
      // Directly serve the uploaded file for download
      res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
      res.setHeader('Content-Disposition', `attachment; filename="${file.originalFilename}"`);
      
      const fileStream = createReadStream(file.filepath);
      fileStream.pipe(res);
      return;
    }
    
    // Determine the Python API endpoint
    const pythonApiUrl = process.env.PYTHON_API_URL || 'http://localhost:5000';
    const validateEndpoint = `${pythonApiUrl}/api/validate-excel`;
    
    // Read the uploaded file
    const fileData = await fsPromises.readFile(file.filepath);
    
    // Create a temporary file path
    const tempDir = tmpdir();
    const tempFileName = `temp_excel_analysis_${Date.now()}${path.extname(file.originalFilename || '')}`;
    const tempFilePath = join(tempDir, tempFileName);
    
    // Write the file to temporary location
    await fsPromises.writeFile(tempFilePath, fileData);
    
    // Create a new form data for the Python API request
    const formData = new FormData();
    
    // Append the file to form data using a file stream
    formData.append('file', createReadStream(tempFilePath), {
      filename: file.originalFilename || tempFileName,
      contentType: file.mimetype || 'application/octet-stream'
    });
    
    // Call the Python API using Node.js compatible form data
    const response = await fetch(validateEndpoint, {
      method: 'POST',
      body: formData,
      headers: formData.getHeaders() // Add proper headers for form data
    });
    
    if (!response.ok) {
      throw new Error(`Python API responded with status ${response.status}`);
    }
    
    // Check if response is JSON or binary (for file download)
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')) {
      // This is a file download response - get the binary content
      const buffer = Buffer.from(await response.buffer());
      
      // Set proper headers for Excel file download
      res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
      res.setHeader('Content-Disposition', `attachment; filename="fixed_${file.originalFilename || 'file.xlsx'}"`);
      res.setHeader('Content-Length', buffer.length);
      
      // Send the binary Excel file
      res.send(buffer);
    } else {
      // This is a JSON response
      const result = await response.json();
      
      // Clean up the temporary file
      await fsPromises.unlink(tempFilePath);
      
      // Return the result to the client
      res.status(200).json(result);
    }
  } catch (error) {
    console.error('Excel Analyzer API Error:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error',
      message: 'Error during Excel validation'
    });
  }
}

