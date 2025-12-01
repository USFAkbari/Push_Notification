import App from './App.svelte';
import Admin from './Admin.svelte';
import axios from 'axios';

// Configure Axios base URL
// In Docker: use relative paths with /api-v1 prefix (nginx will proxy to backend)
// In development: use explicit backend URL with /api-v1 prefix
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
if (API_BASE_URL) {
  axios.defaults.baseURL = API_BASE_URL;
} else {
  // Default: use /api-v1 prefix (works with nginx proxy in Docker)
  // For local development, set VITE_API_BASE_URL=http://localhost:8000/api-v1
  axios.defaults.baseURL = '/api-v1';
}

// Register service worker (only for main app at /app route)
if ('serviceWorker' in navigator && window.location.pathname.startsWith('/app')) {
  window.addEventListener('load', async () => {
    try {
      const registration = await navigator.serviceWorker.register('/service-worker.js');
      console.log('Service Worker registered:', registration);
    } catch (error) {
      console.error('Service Worker registration failed:', error);
    }
  });
}

// Routing: Admin is default (/), public app is at /app
const isPublicApp = window.location.pathname.startsWith('/app');

// Initialize appropriate Svelte app
const app = isPublicApp 
  ? new App({ target: document.getElementById('app') })
  : new Admin({ target: document.getElementById('app') });

export default app;

