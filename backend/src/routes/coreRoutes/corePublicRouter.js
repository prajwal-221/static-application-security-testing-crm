const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs');
const { isPathInside } = require('../../utils/is-path-inside');

// Health check endpoint
router.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'idurar-backend',
    version: process.env.npm_package_version || '1.0.0'
  });
});

router.get('/xss', (req, res) => {
  const q = req.query.q ?? '';
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  return res.status(200).send(`<html><body>${q}</body></html>`);
});

router.get('/vuln-file', (req, res) => {
  const rootDir = path.join(__dirname, '../../public');
  const p = req.query.path ?? '';
  const target = path.join(rootDir, p);
  try {
    const data = fs.readFileSync(target);
    res.setHeader('Content-Type', 'application/octet-stream');
    return res.status(200).send(data);
  } catch (e) {
    return res.status(404).json({
      success: false,
      result: null,
      message: 'File not found',
    });
  }
});

router.route('/:subPath/:directory/:file').get(function (req, res) {
  try {
    const { subPath, directory, file } = req.params;

    // Decode each parameter separately
    const decodedSubPath = decodeURIComponent(subPath);
    const decodedDirectory = decodeURIComponent(directory);
    const decodedFile = decodeURIComponent(file);

    // Define the trusted root directory
    const rootDir = path.join(__dirname, '../../public');

    // Safely join the decoded path segments
    const relativePath = path.join(decodedSubPath, decodedDirectory, decodedFile);
    const absolutePath = path.join(rootDir, relativePath);

    // Check if the resulting path stays inside rootDir
    if (!isPathInside(absolutePath, rootDir)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid filepath',
      });
    }

    return res.sendFile(absolutePath, (error) => {
      if (error) {
        return res.status(404).json({
          success: false,
          result: null,
          message: 'we could not find : ' + file,
        });
      }
    });
  } catch (error) {
    return res.status(503).json({
      success: false,
      result: null,
      message: error.message,
      error: error,
    });
  }
});

module.exports = router;
