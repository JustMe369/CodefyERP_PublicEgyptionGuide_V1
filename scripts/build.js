// scripts/build.js
const fs = require('fs-extra');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = process.cwd();
const DIST = path.join(ROOT, 'dist');

function log(msg) { console.log(`[build] ${msg}`); }
function warn(msg) { console.warn(`[build] ⚠️  ${msg}`); }

log('Cleaning dist/...');
fs.rmSync(DIST, { recursive: true, force: true });
fs.mkdirSync(DIST, { recursive: true });

// Required static directories
const requiredDirs = ['Statics', 'Temp'];
for (const dir of requiredDirs) {
  const src = path.join(ROOT, dir);
  if (!fs.existsSync(src)) {
    warn(`Missing required directory: ${dir} — creating empty dist copy`);
    fs.mkdirSync(path.join(DIST, dir), { recursive: true });
    continue;
  }
  log(`Copying ${dir}/...`);
  fs.copySync(src, path.join(DIST, dir));
}

// Optional root files
const rootFiles = ['README.md', 'vercel.json'];
for (const file of rootFiles) {
  const src = path.join(ROOT, file);
  if (!fs.existsSync(src)) {
    warn(`Missing optional file: ${file} — skipping`);
    continue;
  }
  log(`Copying ${file}...`);
  fs.copySync(src, path.join(DIST, file));
}

// Bundle API serverless functions with ncc (zero dependencies on Vercel)
log('Bundling API functions with ncc...');
const apiDir = path.join(ROOT, 'api');
const distApiDir = path.join(DIST, 'api-functions');
fs.mkdirSync(distApiDir, { recursive: true });

const apiFiles = [
  'validate.js',
  'download-cleaned.js',
  'excel-analyzer.js',
  'serverless-api.js',
  'excel-analyzer-express.js'
];

for (const file of apiFiles) {
  const src = path.join(apiDir, file);
  if (!fs.existsSync(src)) {
    warn(`Missing API file: api/${file} — skipping`);
    continue;
  }
  const name = path.basename(file, '.js');
  const outDir = path.join(distApiDir, name);
  try {
    log(`Bundling api/${file}...`);
    execSync(`ncc build "${src}" -o "${outDir}"`, { stdio: 'inherit', cwd: ROOT });
  } catch (e) {
    warn(`Failed to bundle api/${file}: ${e.message}`);
    // Fallback: copy source file (will need npm install on Vercel)
    fs.copySync(src, path.join(distApiDir, file));
  }
}

log('Build completed successfully.');