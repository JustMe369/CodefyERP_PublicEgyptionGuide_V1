/* eslint-disable no-undef */
/* Vercel Serverless API - Download Cleaned File Endpoint */
/* Handles POST /api/download-cleaned for cleaned Excel file download */

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

  try {
    res.status(200).json({
      success: true,
      message: 'Cleaned file ready for download',
      download_url: '/api/download-csv'
    });
  } catch (error) {
    console.error('Download Cleaned API Error:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
}
