import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
      // Redirect to login (handled by component)
    }
    return Promise.reject(error);
  }
);

/**
 * User registration
 */
export async function register(userData) {
  const response = await api.post('/register', userData);
  return response.data;
}

/**
 * User login
 */
export async function login(username, password) {
  const response = await api.post('/login', { username, password });
  
  // Store token and user data
  if (response.data.access_token) {
    localStorage.setItem('auth_token', response.data.access_token);
    localStorage.setItem('user_data', JSON.stringify({
      user_id: response.data.user_id,
      username: response.data.username,
      email: response.data.email
    }));
  }
  
  return response.data;
}

/**
 * Get current user info
 */
export async function getCurrentUser() {
  const response = await api.get('/user/me');
  return response.data;
}

/**
 * Update fingerprint
 */
export async function updateFingerprint(fingerprint, deviceInfo) {
  const response = await api.post('/user/fingerprint', {
    fingerprint,
    device_info: deviceInfo
  });
  return response.data;
}

/**
 * Subscribe to push notifications
 */
export async function subscribeToPush(subscriptionData) {
  const response = await api.post('/push/subscribe', subscriptionData);
  return response.data;
}

/**
 * Send push notification (to current user)
 */
export async function sendPush(pushData) {
  const response = await api.post('/push/send', pushData);
  return response.data;
}

/**
 * Send broadcast push notification
 */
export async function sendBroadcastPush(pushData) {
  const response = await api.post('/push/broadcast', pushData);
  return response.data;
}

/**
 * Logout
 */
export function logout() {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user_data');
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated() {
  return !!localStorage.getItem('auth_token');
}

/**
 * Get stored user data
 */
export function getStoredUserData() {
  const data = localStorage.getItem('user_data');
  return data ? JSON.parse(data) : null;
}

export default api;

