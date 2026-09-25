// scripts/build.js
const fs = require('fs-extra');
const path = require('path');

const ROOT = process.cwd();
const DIST = path.join(ROOT, 'dist');

function log(msg) { console.log(`[build] ${msg}`); }
function warn(msg) { console.warn(`[build] ⚠️  ${msg}`); }

log('Cleaning dist/...');
fs.rmSync(DIST, { recursive: true, force: true });
fs.mkdirSync(DIST, { recursive: true });

// Required static directories ONLY (no api/ to avoid Vercel serverless function detection)
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
const rootFiles = ['README.md'];
for (const file of rootFiles) {
  const src = path.join(ROOT, file);
  if (!fs.existsSync(src)) {
    warn(`Missing optional file: ${file} — skipping`);
    continue;
  }
  log(`Copying ${file}...`);
  fs.copySync(src, path.join(DIST, file));
}

log('Build completed successfully - static only.');