const File = require('../models/File');
const fs = require('fs');
const path = require('path');
const redis = require('redis');
const { v4: uuidv4 } = require('uuid');

// Initialize Redis client
const redisClient = redis.createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379',
});
redisClient.connect().catch(console.error);

// Temporary directory for chunks
const TEMP_DIR = path.join(__dirname, '../../temp');
if (!fs.existsSync(TEMP_DIR)) {
  fs.mkdirSync(TEMP_DIR, { recursive: true });
}

// Upload directory for final files
const UPLOAD_DIR = path.join(__dirname, '../../uploads');
if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

exports.uploadChunk = async (req, res) => {
  try {
    const { fileId = uuidv4(), chunkIndex, totalChunks } = req.body;
    const chunkData = req.file.buffer;

    // Save chunk to temporary directory
    const chunkPath = path.join(TEMP_DIR, `${fileId}_${chunkIndex}`);
    fs.writeFileSync(chunkPath, chunkData);

    // Update Redis with chunk upload status
    await redisClient.hSet(`upload:${fileId}`, `chunk_${chunkIndex}`, 'uploaded');

    // Check if all chunks are uploaded
    const uploadedChunks = await redisClient.hLen(`upload:${fileId}`);
    if (uploadedChunks === parseInt(totalChunks)) {
      // Reassemble file
      const filePath = path.join(UPLOAD_DIR, fileId);
      const writeStream = fs.createWriteStream(filePath);

      for (let i = 0; i < totalChunks; i++) {
        const chunkPath = path.join(TEMP_DIR, `${fileId}_${i}`);
        const chunkData = fs.readFileSync(chunkPath);
        writeStream.write(chunkData);
        fs.unlinkSync(chunkPath); // Clean up chunk
      }

      writeStream.end();

      // Save file metadata to database
      const file = await File.create({
        id: fileId,
        name: req.file.originalname,
        size: req.file.size,
        type: req.file.mimetype,
        path: filePath,
        chunkCount: totalChunks,
        chunksUploaded: totalChunks,
      });

      res.status(200).json({ file });
    } else {
      res.status(200).json({ message: 'Chunk uploaded successfully' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.getUploadStatus = async (req, res) => {
  try {
    const { id } = req.params;
    const status = await redisClient.hGetAll(`upload:${id}`);
    res.status(200).json({ status });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};