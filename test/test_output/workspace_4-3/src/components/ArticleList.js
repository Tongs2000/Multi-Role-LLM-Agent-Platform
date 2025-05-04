import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getArticles, getAdminArticles } from '../services/api';

const ArticleList = ({ isAdmin = false }) => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const data = isAdmin ? await getAdminArticles() : await getArticles();
        setArticles(data);
      } catch (error) {
        console.error('Error fetching articles:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchArticles();
  }, [isAdmin]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="article-list">
      {articles.map((article) => (
        <div key={article.id} className="article-card">
          <h3>
            <Link to={`/articles/${article.slug}`}>{article.title}</Link>
          </h3>
          <p className="excerpt">{article.excerpt}</p>
          <div className="meta">
            <span>{new Date(article.created_at).toLocaleDateString()}</span>
            {isAdmin && (
              <span>
                <Link to={`/admin/edit/${article.id}`}>Edit</Link>
                <button onClick={() => handleDelete(article.id)}>Delete</button>
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ArticleList;