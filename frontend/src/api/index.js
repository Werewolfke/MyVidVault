import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// 1. Create a central Axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// 2. Add a request interceptor to automatically add the token
apiClient.interceptors.request.use(
  (config) => {
    const access = localStorage.getItem('access');
    if (access) {
      config.headers['Authorization'] = `Bearer ${access}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 3. Add a response interceptor to handle 401 errors globally
apiClient.interceptors.response.use(
  (response) => response, // Simply return the response if it's successful
  (error) => {
    // Check if the error is a 401 Unauthorized
    if (error.response && error.response.status === 401) {
      // Clear the invalid tokens
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      localStorage.removeItem('username'); // Also clear username
      
      // Redirect to the login page
      // We use window.location to force a full page reload, which clears any reactive state.
      window.location.href = '/login';
    }
    // For all other errors, just pass them along
    return Promise.reject(error);
  }
);


// --- Refactored API Functions ---

// JWT login
export const login = async (username, password) => {
  const response = await apiClient.post(`/token/`, { username, password });
  localStorage.setItem('access', response.data.access);
  localStorage.setItem('refresh', response.data.refresh);
  return response.data;
};

// Registration
export const register = async (username, email, password, password2) => {
  const response = await apiClient.post(
    `/auth/register/`,
    { username, email, password, password2 }
  );
  return response.data;
};

// Fetch videos (public)
export const fetchVideos = async (params = {}) => {
  const response = await apiClient.get(`/videos/`, { params });
  return response.data;
};

// Fetch bookmark detail (public)
export const fetchBookmarkDetail = async (id) => {
  const response = await apiClient.get(`/bookmarks/${id}/`);
  return response.data;
};

// Logout
export const logout = async () => {
  localStorage.removeItem('access');
  localStorage.removeItem('refresh');
  localStorage.removeItem('username');
};

// Refresh JWT token
export const scrapeUrlMetadata = async (url) => {
  const response = await apiClient.post(`/scrape-metadata/`, { url });
  return response.data;
};

export const refreshToken = async () => {
  const refresh = localStorage.getItem('refresh');
  const response = await apiClient.post(`/token/refresh/`, { refresh });
  localStorage.setItem('access', response.data.access);
  return response.data;
};

// Create manual bookmark (protected - token is added by interceptor)
export const createManualBookmark = async (payload) => {
  const response = await apiClient.post(
    `/bookmarks/manual-create/`,
    payload
  );
  return response.data;
};

// Search bookmarks (public)
export const searchBookmarks = async (query, params = {}) => {
  const response = await apiClient.get(`/bookmarks/`, {
    params: { q: query, ...params }
  });
  return response.data;
};

// Fetch user profile (public)
export const fetchUserProfile = async (username) => {
  const response = await apiClient.get(`/profile/${username}/`);
  return response.data;
};

// Fetch my profile (protected - token is added by interceptor)
export const fetchMyProfile = async () => {
  const response = await apiClient.get(`/profile/me/`);
  return response.data;
};

// Update my profile (protected - token is added by interceptor)
export const updateMyProfile = async (formData) => {
  const response = await apiClient.patch(
    `/profile/me/`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

export const requestPasswordReset = async (email) => {
  return apiClient.post(`/auth/password-reset/`, { email });
};

export const confirmPasswordReset = async ({ uidb64, token, new_password1, new_password2 }) => {
  return apiClient.post(`/auth/password-reset-confirm/`, {
    uidb64, token, new_password1, new_password2
  });
};
