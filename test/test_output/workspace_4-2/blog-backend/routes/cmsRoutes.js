const express = require('express');
const router = express.Router();
const { publishArticle, getArticleVersions } = require('../controllers/cmsController');

// Publish article to multiple platforms
router.post('/publish', publishArticle);

// Fetch article versions for different platforms
router.get('/versions/:articleId', getArticleVersions);

module.exports = router;