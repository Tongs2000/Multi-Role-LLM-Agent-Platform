const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = 3000;
const SCORES_FILE = path.join(__dirname, 'scores.json');

// Middleware
app.use(cors());
app.use(express.json());

// Load or initialize scores file
if (!fs.existsSync(SCORES_FILE)) {
    fs.writeFileSync(SCORES_FILE, JSON.stringify([]));
}

// Save a new score
app.post('/score', (req, res) => {
    const { player, score } = req.body;
    const scores = JSON.parse(fs.readFileSync(SCORES_FILE));
    scores.push({ player, score, date: new Date().toISOString() });
    fs.writeFileSync(SCORES_FILE, JSON.stringify(scores, null, 2));
    res.status(201).send('Score saved');
});

// Fetch all scores
app.get('/scores', (req, res) => {
    const scores = JSON.parse(fs.readFileSync(SCORES_FILE));
    res.json(scores);
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});