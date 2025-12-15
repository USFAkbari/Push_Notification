<script>
  import { onMount } from 'svelte';
  import Register from './Register.svelte';
  import Login from './Login.svelte';
  import Dashboard from './Dashboard.svelte';
  import { isAuthenticated } from './services/api.js';
  
  let currentRoute = 'login';
  
  function handleHashChange() {
    const hash = window.location.hash.slice(1) || '/login';
    currentRoute = hash.replace('/', '') || 'login';
  }
  
  onMount(() => {
    // Register service worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/service-worker.js')
        .then(registration => {
          console.log('Service Worker registered:', registration);
        })
        .catch(error => {
          console.error('Service Worker registration failed:', error);
        });
    }
    
    // Handle routing
    handleHashChange();
    window.addEventListener('hashchange', handleHashChange);
    
    // Check if user is authenticated and redirect
    if (isAuthenticated() && currentRoute === 'login') {
      window.location.hash = '#/dashboard';
    } else if (!isAuthenticated() && currentRoute === 'dashboard') {
      window.location.hash = '#/login';
    }
  });
</script>

<main>
  {#if currentRoute === 'register'}
    <Register />
  {:else if currentRoute === 'login'}
    <Login />
  {:else if currentRoute === 'dashboard'}
    <Dashboard />
  {:else}
    <Login />
  {/if}
</main>

<style>
  :global(body) {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  }
</style>

