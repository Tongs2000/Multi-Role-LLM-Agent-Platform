import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = async (username, password) => {
  try {
    const response = await api.post('/login', { username, password });
    localStorage.setItem('token', response.data.access_token);
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

export const register = async (username, email, password) => {
  try {
    const response = await api.post('/register', { username, email, password });
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

export const getArticles = async () => {
  const response = await api.get('/articles');
  return response.data;
};

export const getArticle = async (slug) => {
  const response = await api.get(`/articles/${slug}`);
  return response.data;
};

export const getAdminArticles = async () => {
  const response = await api.get('/admin/articles');
  return response.data;
};

export const createArticle = async (articleData) => {
  const response = await api.post('/admin/articles', articleData);
  return response.data;
};

export const updateArticle = async (id, articleData) => {
  const response = await api.put(`/admin/articles/${id}`, articleData);
  return response.data;
};

export const deleteArticle = async (id) => {
  const response = await api.delete(`/admin/articles/${id}`);
  return response.data;
};