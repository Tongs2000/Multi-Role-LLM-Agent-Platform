const express = require('express');
const multer = require('multer');
const sharp = require('sharp');
const mongoose = require('mongoose');
const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Initialize Express app
const app = express();
app.use(express.json());

// Multer configuration for file uploads
const upload = multer({ dest: 'uploads/' });

// MongoDB connection
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

// Image Schema
const ImageSchema = new mongoose.Schema({
  originalPath: String,
  editedPath: String,
  metadata: {
    width: Number,
    height: Number,
    format: String,
  },
});

// Filter Preset Schema
const FilterPresetSchema = new mongoose.Schema({
  name: String,
  config: Object,
});

const Image = mongoose.model('Image', ImageSchema);
const FilterPreset = mongoose.model('FilterPreset', FilterPresetSchema);

// API Endpoints
app.post('/api/upload', upload.single('image'), async (req, res) => {
  try {
    const { file } = req;
    if (!file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const metadata = await sharp(file.path).metadata();
    const image = new Image({
      originalPath: file.path,
      metadata: {
        width: metadata.width,
        height: metadata.height,
        format: metadata.format,
      },
    });

    await image.save();
    res.status(201).json({ id: image._id, metadata: image.metadata });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/process', async (req, res) => {
  try {
    const { id, operations } = req.body;
    const image = await Image.findById(id);
    if (!image) {
      return res.status(404).json({ error: 'Image not found' });
    }

    let processedImage = sharp(image.originalPath);

    // Apply operations
    if (operations.crop) {
      processedImage = processedImage.extract(operations.crop);
    }
    if (operations.rotate) {
      processedImage = processedImage.rotate(operations.rotate);
    }

    const outputPath = `processed_${id}.${image.metadata.format}`;
    await processedImage.toFile(outputPath);
    image.editedPath = outputPath;
    await image.save();

    res.status(200).json({ editedPath: image.editedPath });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/apply-filter', async (req, res) => {
  try {
    const { id, filterConfig } = req.body;
    const image = await Image.findById(id);
    if (!image) {
      return res.status(404).json({ error: 'Image not found' });
    }

    let processedImage = sharp(image.originalPath);

    // Apply custom filter
    if (filterConfig.kernel) {
      processedImage = processedImage.convolve(filterConfig.kernel);
    }
    if (filterConfig.brightness) {
      processedImage = processedImage.modulate({
        brightness: filterConfig.brightness,
      });
    }

    const outputPath = `filtered_${id}.${image.metadata.format}`;
    await processedImage.toFile(outputPath);
    image.editedPath = outputPath;
    await image.save();

    res.status(200).json({ editedPath: image.editedPath });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/presets', async (req, res) => {
  try {
    const presets = await FilterPreset.find();
    res.status(200).json(presets);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/save', async (req, res) => {
  try {
    const { id } = req.body;
    const image = await Image.findById(id);
    if (!image || !image.editedPath) {
      return res.status(404).json({ error: 'Edited image not found' });
    }

    const finalPath = `saved_${id}.${image.metadata.format}`;
    fs.renameSync(image.editedPath, finalPath);
    image.editedPath = finalPath;
    await image.save();

    res.status(200).json({ savedPath: image.editedPath });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});