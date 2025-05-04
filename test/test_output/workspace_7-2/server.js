const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3001;

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = './uploads';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir);
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    cb(null, `${Date.now()}-${file.originalname}`);
  },
});

const upload = multer({ storage });

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Mock API endpoints
app.post('/api/upload', upload.single('image'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }
  res.json({ path: req.file.path });
});

app.post('/api/process', (req, res) => {
  const { imagePath, edits } = req.body;
  if (!imagePath || !edits) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  // Simulate processing delay
  setTimeout(() => {
    res.json({ processedPath: imagePath });
  }, 1000);
});

app.post('/api/apply-filter', (req, res) => {
  const { imagePath, filterConfig } = req.body;
  if (!imagePath || !filterConfig) {
    return res.status(400).json({ error: 'Missing required fields' });
  }
  // Simulate filter application
  setTimeout(() => {
    res.json({ filteredPath: imagePath });
  }, 1000);
});

app.get('/api/presets', (req, res) => {
  const presets = [
    { id: 1, name: 'Vintage', config: { brightness: 70, contrast: 30 } },
    { id: 2, name: 'Monochrome', config: { saturation: 0 } },
  ];
  res.json(presets);
});

app.post('/api/save', (req, res) => {
  const { imagePath } = req.body;
  if (!imagePath) {
    return res.status(400).json({ error: 'Missing image path' });
  }
  // Simulate saving delay
  setTimeout(() => {
    res.json({ saved: true, path: imagePath });
  }, 1000);
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});