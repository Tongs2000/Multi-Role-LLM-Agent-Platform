const Article = require('../models/Article');
const { publishToPlatforms } = require('../utils/cms');

exports.publishArticle = async (req, res) => {
  try {
    const { articleId, platforms } = req.body;
    const article = await Article.findByPk(articleId);
    if (!article) {
      return res.status(404).json({ error: 'Article not found' });
    }

    // Publish to specified platforms
    const result = await publishToPlatforms(article, platforms);
    res.status(200).json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.getArticleVersions = async (req, res) => {
  try {
    const { articleId } = req.params;
    const article = await Article.findByPk(articleId);
    if (!article) {
      return res.status(404).json({ error: 'Article not found' });
    }

    res.status(200).json({
      platforms: article.platforms,
      versions: article.versions || [],
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};