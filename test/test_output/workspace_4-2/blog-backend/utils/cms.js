const publishToPlatforms = async (article, platforms) => {
  // Simulate publishing to each platform
  const results = platforms.map(platform => {
    return {
      platform,
      status: 'published',
      url: `https://${platform}.example.com/articles/${article.id}`,
    };
  });

  // Update the article's platforms field
  article.platforms = [...new Set([...article.platforms, ...platforms])];
  await article.save();

  return results;
};

module.exports = { publishToPlatforms };