#!/bin/bash
set -e

# Workaround for npm v11 "Invalid Version" bug
# Install npm 10.9.2 locally and use it explicitly
npm install npm@10.9.2 --prefix .npm-local 2>/dev/null || true

# Use the locally installed npm 10 explicitly
./.npm-local/node_modules/.bin/npm ci --legacy-peer-deps