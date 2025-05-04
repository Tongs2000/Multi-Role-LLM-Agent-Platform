const express = require('express');
const router = express.Router();
const { uploadChunk, getUploadStatus } = require('../controllers/uploadController');
const multer = require('multer');

// Configure Multer for chunked uploads
const upload = multer({ storage: multer.memoryStorage() });

// Handle chunked uploads
router.post('/upload-chunk', upload.single('chunk'), uploadChunk);

// Check upload status
router.get('/upload-status/:id', getUploadStatus);

module.exports = router;