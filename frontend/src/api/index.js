import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// JWT login
export const login = async (username, password) => {
  const response = await axios.post(`${API_BASE_URL}/token/`, { username, password });
  localStorage.setItem('access', response.data.access);
  localStorage.setItem('refresh', response.data.refresh);
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

// Fetch videos (public)
export const fetchVideos = async (params = {}) => {
  const response = await axios.get(`${API_BASE_URL}/videos/`, { params });
  return response.data;
};

// Fetch bookmark detail (public)
export const fetchBookmarkDetail = async (id) => {
  const response = await axios.get(`${API_BASE_URL}/bookmarks/${id}/`);
  return response.data;
};



// Logout (JWT: just remove tokens client-side)
export const logout = async () => {
  localStorage.removeItem('access');
  localStorage.removeItem('refresh');
};

// Refresh JWT token
export const refreshToken = async () => {
  const refresh = localStorage.getItem('refresh');
  const response = await axios.post(`${API_BASE_URL}/token/refresh/`, { refresh });
  localStorage.setItem('access', response.data.access);
  return response.data;
};

export const createManualBookmark = async (payload) => {
  const access = localStorage.getItem('access');
  const response = await axios.post(
    `${API_BASE_URL}/videos/bookmarks/manual-create/`,
    payload,
    { headers: { Authorization: `Bearer ${access}` } }
  );
  return response.data;
};

export const searchBookmarks = async (query, params = {}) => {
  const response = await axios.get(`${API_BASE_URL}/bookmarks/`, {
    params: { q: query, ...params }
  });
  return response.data;
};

// Fetch user profile (public)
export const fetchUserProfile = async (username) => {
  const response = await axios.get(`${API_BASE_URL}/profile/${username}/`);
  return response.data;
};

// Fetch my profile (protected)
export const fetchMyProfile = async () => {
  const access = localStorage.getItem('access');
  const response = await axios.get(`${API_BASE_URL}/profile/me/`, {
    headers: { Authorization: `Bearer ${access}` }
  });
  return response.data;
};

export const updateMyProfile = async (formData) => {
  const access = localStorage.getItem('access');
  const response = await axios.patch(
    `${API_BASE_URL}/profile/me/`,
    formData,
    {
      headers: {
        Authorization: `Bearer ${access}`,
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

