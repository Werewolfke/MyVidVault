import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// JWT login
export const login = async (username, password) => {
  const response = await axios.post(`${API_BASE_URL}/token/`, { username, password });
  return response.data;
};

// Registration (assuming your backend register endpoint does not require CSRF for JWT)
export const register = async (username, email, password, password2) => {
  const response = await axios.post(
    `${API_BASE_URL}/auth/register/`,
    { username, email, password, password2 }
  );
  return response.data;
};

// Logout (JWT: blacklist refresh token)
export const logout = async () => {
  // Token blacklisting is handled in the auth store
  return Promise.resolve();
};

// Refresh JWT token
export const refreshToken = async () => {
  const refresh = localStorage.getItem('refresh');
  if (!refresh) {
    throw new Error('No refresh token available');
  }
  const response = await axios.post(`${API_BASE_URL}/token/refresh/`, { refresh });
  return response.data;
};

// Create a default axios instance with authentication
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Track if we're currently refreshing to prevent multiple simultaneous requests
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  
  failedQueue = [];
};

// Add request interceptor to automatically include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If we're already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const response = await refreshToken();
        const newToken = response.access;
        
        // Update localStorage
        localStorage.setItem('access', newToken);
        if (response.refresh) {
          localStorage.setItem('refresh', response.refresh);
        }
        
        // Update token expiry
        const expiry = new Date();
        expiry.setDate(expiry.getDate() + 7);
        localStorage.setItem('token_expiry', expiry.toISOString());
        
        // Process queued requests
        processQueue(null, newToken);
        
        // Retry original request
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect
        processQueue(refreshError, null);
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('user');
        localStorage.removeItem('token_expiry');
        
        // Only redirect if we're not already on login page
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    
    return Promise.reject(error);
  }
);

// Public API functions
export const fetchVideos = async (params = {}) => {
  const response = await axios.get(`${API_BASE_URL}/videos/`, { params });
  return response.data;
};

// Simple cache for bookmark details (5 minute TTL)
const bookmarkCache = new Map()
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

export const fetchBookmarkDetail = async (id) => {
  // Check cache first
  const cacheKey = `bookmark_${id}`
  const cached = bookmarkCache.get(cacheKey)
  
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data
  }
  
  const response = await axios.get(`${API_BASE_URL}/bookmarks/${id}/`);
  
  // Cache the result
  bookmarkCache.set(cacheKey, {
    data: response.data,
    timestamp: Date.now()
  })
  
  return response.data;
};

export const searchBookmarks = async (query, params = {}) => {
  const response = await axios.get(`${API_BASE_URL}/bookmarks/`, {
    params: { q: query, ...params }
  });
  return response.data;
};

export const fetchUserProfile = async (username) => {
  const response = await axios.get(`${API_BASE_URL}/profile/${username}/`);
  return response.data;
};

export const requestPasswordReset = async (email) => {
  return axios.post(`${API_BASE_URL}/auth/password-reset/`, { email });
};

export const confirmPasswordReset = async ({ uidb64, token, new_password1, new_password2 }) => {
  return axios.post(`${API_BASE_URL}/auth/password-reset-confirm/`, {
    uidb64, token, new_password1, new_password2
  });
};

// Protected API functions (use api instance with interceptors)
export const createManualBookmark = async (payload) => {
  const response = await api.post('/bookmarks/manual-create/', payload);
  return response.data;
};

export const extractVideoMetadata = async (url) => {
  const response = await api.post('/bookmarks/extract-metadata/', { url });
  return response.data;
};

// Fetch current user's profile using their username
export const fetchMyProfile = async (username) => {
  const response = await api.get(`/profile/${username}/`);
  return response.data;
};

// Update current user's profile using their username
export const updateMyProfile = async (username, formData) => {
  const response = await api.patch(`/profile/${username}/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Follow/Unfollow functionality
export const toggleFollow = async (userId) => {
  const response = await api.post(`/users/${userId}/toggle-follow/`);
  return response.data;
};

export const checkFollowStatus = async (userId) => {
  const response = await api.get(`/users/${userId}/follow-status/`);
  return response.data;
};

export const getFollowersList = async (userId) => {
  const response = await api.get(`/users/${userId}/followers/`);
  return response.data;
};

export const getFollowingList = async (userId) => {
  const response = await api.get(`/users/${userId}/following/`);
  return response.data;
};

export default api;

