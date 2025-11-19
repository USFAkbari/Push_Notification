import App from './App.svelte';
import axios from 'axios';

// Configure Axios base URL
// In Docker: use relative paths (nginx will proxy to backend)
// In development: use explicit backend URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
if (API_BASE_URL) {
  axios.defaults.baseURL = API_BASE_URL;
} else {
  // Default: use relative paths (works with nginx proxy in Docker)
  // For local development, set VITE_API_BASE_URL=http://localhost:8000
  axios.defaults.baseURL = '';
}

// Register service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {
      const registration = await navigator.serviceWorker.register('/service-worker.js');
      console.log('Service Worker registered:', registration);
    } catch (error) {
      console.error('Service Worker registration failed:', error);
    }
  });
}

// Initialize Svelte app
const app = new App({
  target: document.getElementById('app'),
});

export default app;

