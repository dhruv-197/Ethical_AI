import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log('🚀 API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API endpoints
export const apiService = {
  // Health check
  healthCheck: () => api.get('/health'),
  
  // User operations
  getUserInfo: (username,max_tweets) => api.post('/user/get-info', { username,max_tweets }),
  
  // User profiles - NEW
  getUserProfiles: (params = {}) => api.get('/profiles', { params }),
  // In services/api.js
  deleteUserProfile: (username) => {
    return api.delete(`/profile/${username}`);
  },
  
  // Get specific user profile WITH tweets - NEW METHOD
  getUserProfile: (username) => api.get(`/profile/${username}`),
  
  
  // Tweet operations
  getUserTweets: (username, maxTweets = 50) => 
    api.post('/user/get-tweets', { username, max_tweets: maxTweets }),
  
  // Post operations
  getUserPosts: (username, maxPosts = 20) => 
    api.post('/user/get-posts', { username, max_posts: maxPosts }),
  
  // User profile analysis
analyzeUserProfile: (username, image_model = 'clip', text_model = 'xlnet', fusion_technique = 'weighted_average', alpha = 0.5) =>
  api.post(`/user/${username}/analyze`, {
    image_model,
    text_model,
    fusion_technique,
    alpha
  }),
  // User data refresh
  refreshUserData: (username) => api.post(`/user/${username}/refresh`),
  
  // Get user tweets with pagination
  getUserTweetsPaginated: (username, page = 1, perPage = 20) => 
    api.get(`/user/${username}/tweets`, { params: { page, per_page: perPage } }),
  
  // Get user posts with pagination
  getUserPostsPaginated: (username, page = 1, perPage = 20) => 
    api.get(`/user/${username}/posts`, { params: { page, per_page: perPage } }),
  
  // Analysis history and management
  getAnalysisHistory: () => api.get('/analysis/history'),
  
  // Single prediction endpoints (if needed)
  predictText: (text) => api.post('/predict/text', { text }),
  
  predictImage: (imageFile) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    return api.post('/predict/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  
  // Batch operations
  batchAnalyze: (usernames) => api.post('/analysis/batch', { usernames }),
  
  // Export results
  exportAnalysis: (username, format = 'json') => 
    api.get(`/analysis/${username}/export`, { params: { format } }),
  
  // Delete analysis
  deleteAnalysis: (username) => api.delete(`/analysis/${username}`),
};

export default api;