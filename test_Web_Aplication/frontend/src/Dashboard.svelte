<script>
  import { onMount } from 'svelte';
  import { getCurrentUser, subscribeToPush, logout, isAuthenticated } from './services/api.js';
  
  const PUSH_SERVICE_URL = import.meta.env.VITE_PUSH_SERVICE_URL || 'http://localhost:8000/api-v1';
  
  let user = null;
  let subscriptionStatus = 'not-supported';
  let subscription = null;
  let vapidPublicKey = null;
  let isLoading = false;
  let message = '';
  let messageType = 'info';
  let autoSubscribing = false;
  
  // Check if push notifications are supported
  function checkSupport() {
    // Check for service worker support
    if (!('serviceWorker' in navigator)) {
      subscriptionStatus = 'not-supported';
      console.warn('Service Worker is not supported in this browser');
      return false;
    }
    
    // Check for Push Manager support
    if (!('PushManager' in window)) {
      subscriptionStatus = 'not-supported';
      console.warn('Push Manager is not supported in this browser');
      return false;
    }
    
    // Check for Notification API support
    if (!('Notification' in window)) {
      subscriptionStatus = 'not-supported';
      console.warn('Notifications API is not supported in this browser');
      return false;
    }
    
    // Check if we're on HTTPS or localhost (required for push notifications)
    const isSecureContext = window.isSecureContext || 
                            location.protocol === 'https:' || 
                            location.hostname === 'localhost' || 
                            location.hostname === '127.0.0.1';
    
    if (!isSecureContext) {
      subscriptionStatus = 'not-supported';
      console.warn('Push notifications require HTTPS or localhost');
      message = 'Push notifications require HTTPS. Please access this site over HTTPS.';
      messageType = 'error';
      return false;
    }
    
    return true;
  }
  
  // Get VAPID public key from Push service
  async function fetchVapidPublicKey() {
    try {
      const response = await fetch(`${PUSH_SERVICE_URL}/vapid-public-key`);
      const data = await response.json();
      vapidPublicKey = data.publicKey;
    } catch (error) {
      console.error('Error fetching VAPID public key:', error);
      message = 'Failed to fetch VAPID public key';
      messageType = 'error';
    }
  }
  
  // Request notification permission
  async function requestPermission() {
    if (!checkSupport()) {
      message = 'Push notifications are not supported in this browser';
      messageType = 'error';
      return false;
    }
    
    try {
      const permission = await Notification.requestPermission();
      
      if (permission === 'granted') {
        subscriptionStatus = 'granted';
        return true;
      } else if (permission === 'denied') {
        subscriptionStatus = 'denied';
        message = 'Notification permission denied. Please enable notifications in browser settings.';
        messageType = 'error';
        return false;
      } else {
        subscriptionStatus = 'default';
        message = 'Notification permission not granted. Please allow notifications when prompted.';
        messageType = 'info';
        return false;
      }
    } catch (error) {
      console.error('Error requesting permission:', error);
      message = 'Error requesting notification permission';
      messageType = 'error';
      return false;
    }
  }
  
  // Subscribe to push notifications
  async function subscribe(silent = false) {
    if (!checkSupport()) {
      if (!silent) {
        message = 'Push notifications are not supported in this browser';
        messageType = 'error';
      }
      return false;
    }
    
    if (!vapidPublicKey) {
      if (!silent) {
        message = 'VAPID key not loaded. Please refresh the page.';
        messageType = 'error';
      }
      return false;
    }
    
    if (!user || !user.id) {
      if (!silent) {
        message = 'User information not available. Please refresh the page.';
        messageType = 'error';
      }
      return false;
    }
    
    // Request permission if not already granted
    if (subscriptionStatus !== 'granted' && subscriptionStatus !== 'subscribed') {
      const permissionGranted = await requestPermission();
      if (!permissionGranted) {
        return false;
      }
    }
    
    try {
      isLoading = true;
      autoSubscribing = true;
      
      if (!silent) {
        message = 'Registering service worker...';
      }
      
      // Register service worker if not already registered
      let registration;
      try {
        registration = await navigator.serviceWorker.ready;
      } catch (error) {
        // Service worker not ready, register it
        registration = await navigator.serviceWorker.register('/service-worker.js');
        await navigator.serviceWorker.ready;
      }
      
      if (!silent) {
        message = 'Creating push subscription...';
      }
      
      // Check if subscription already exists
      let pushSubscription = await registration.pushManager.getSubscription();
      
      if (!pushSubscription) {
        // Create new push subscription
        const applicationServerKey = urlBase64ToUint8Array(vapidPublicKey);
        pushSubscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: applicationServerKey
        });
      }
      
      if (!silent) {
        message = 'Saving subscription...';
      }
      
      // Prepare subscription data
      const subscriptionData = {
        endpoint: pushSubscription.endpoint,
        keys: {
          p256dh: arrayBufferToBase64(pushSubscription.getKey('p256dh')),
          auth: arrayBufferToBase64(pushSubscription.getKey('auth'))
        },
        user_id: user.id
      };
      
      // Send to backend
      const result = await subscribeToPush(subscriptionData);
      
      if (result.success) {
        subscription = pushSubscription;
        subscriptionStatus = 'subscribed';
        if (!silent) {
          message = 'Successfully subscribed to push notifications!';
          messageType = 'success';
        } else {
          // Clear message for auto-subscription
          message = '';
        }
        return true;
      } else {
        if (!silent) {
          message = 'Failed to subscribe: ' + (result.message || 'Unknown error');
          messageType = 'error';
        }
        return false;
      }
    } catch (error) {
      console.error('Subscription error:', error);
      if (!silent) {
        if (error.name === 'NotAllowedError') {
          message = 'Notification permission denied. Please enable notifications in browser settings.';
        } else if (error.name === 'NotSupportedError') {
          message = 'Push notifications not supported. Try a different browser.';
        } else {
          message = `Failed to subscribe: ${error.message || 'Unknown error'}`;
        }
        messageType = 'error';
      }
      return false;
    } finally {
      isLoading = false;
      autoSubscribing = false;
    }
  }
  
  // Utility functions
  function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');
    
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(65);
    outputArray[0] = 0x04;
    
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i + 1] = rawData.charCodeAt(i);
    }
    
    return outputArray;
  }
  
  function arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  }
  
  // Check existing subscription
  async function checkExistingSubscription() {
    if (!checkSupport()) {
      return false;
    }
    
    try {
      // Ensure service worker is registered first
      let registration;
      try {
        registration = await navigator.serviceWorker.ready;
      } catch (error) {
        // Service worker not ready, try to register it
        console.log('Service worker not ready, registering...');
        try {
          registration = await navigator.serviceWorker.register('/service-worker.js');
          await navigator.serviceWorker.ready;
        } catch (regError) {
          console.error('Failed to register service worker:', regError);
          return false;
        }
      }
      
      // Check for existing subscription
      const existingSubscription = await registration.pushManager.getSubscription();
      
      if (existingSubscription) {
        subscription = existingSubscription;
        subscriptionStatus = 'subscribed';
        return true;
      } else {
        const permission = Notification.permission;
        if (permission === 'granted') {
          subscriptionStatus = 'granted';
        } else if (permission === 'denied') {
          subscriptionStatus = 'denied';
        } else {
          subscriptionStatus = 'default';
        }
        return false;
      }
    } catch (error) {
      console.error('Error checking subscription:', error);
      return false;
    }
  }
  
  // Auto-subscribe function
  async function autoSubscribe() {
    if (!user || !user.id) {
      return;
    }
    
    // Check if already subscribed
    const isSubscribed = await checkExistingSubscription();
    if (isSubscribed) {
      return;
    }
    
    // Wait a bit for VAPID key to be fetched
    if (!vapidPublicKey) {
      await fetchVapidPublicKey();
    }
    
    // Auto-subscribe silently (no user messages)
    await subscribe(true);
  }
  
  // Handle logout
  function handleLogout() {
    logout();
    window.location.hash = '#/login';
  }
  
  onMount(async () => {
    // Check authentication
    if (!isAuthenticated()) {
      window.location.hash = '#/login';
      return;
    }
    
    // Load user data
    try {
      user = await getCurrentUser();
    } catch (error) {
      console.error('Error loading user:', error);
      window.location.hash = '#/login';
      return;
    }
    
    // Initialize push notifications
    checkSupport();
    await fetchVapidPublicKey();
    
    // Check existing subscription first
    const isSubscribed = await checkExistingSubscription();
    
    // If not subscribed, automatically subscribe
    if (!isSubscribed) {
      // Small delay to ensure service worker is ready
      setTimeout(async () => {
        await autoSubscribe();
      }, 500);
    }
  });
</script>

<div class="min-h-screen bg-base-200 p-4">
  <div class="max-w-4xl mx-auto">
    <!-- Header -->
    <div class="card bg-base-100 shadow-xl mb-4">
      <div class="card-body">
        <div class="flex justify-between items-center">
          <h1 class="card-title text-3xl">Dashboard</h1>
          <button class="btn btn-outline btn-error" on:click={handleLogout}>
            Logout
          </button>
        </div>
      </div>
    </div>
    
    {#if message}
      <div class="alert alert-{messageType === 'error' ? 'error' : messageType === 'success' ? 'success' : 'info'} mb-4">
        <span>{message}</span>
      </div>
    {/if}
    
    {#if user}
      <!-- User Info -->
      <div class="card bg-base-100 shadow-xl mb-4">
        <div class="card-body">
          <h2 class="card-title">User Information</h2>
          <div class="space-y-2">
            <p><strong>Username:</strong> {user.username}</p>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>User ID:</strong> {user.id}</p>
          </div>
        </div>
      </div>
      
      <!-- Push Notification Subscription -->
      <div class="card bg-base-100 shadow-xl mb-4">
        <div class="card-body">
          <h2 class="card-title">Push Notifications</h2>
          
          {#if subscriptionStatus === 'not-supported'}
            <div class="alert alert-error">
              <span>Push notifications are not supported in this browser</span>
            </div>
          {:else}
            <div class="mb-4">
              <div class="badge badge-lg {subscriptionStatus === 'subscribed' ? 'badge-success' : subscriptionStatus === 'granted' ? 'badge-warning' : subscriptionStatus === 'denied' ? 'badge-error' : 'badge-info'}">
                {subscriptionStatus === 'subscribed' ? 'Subscribed' : subscriptionStatus === 'granted' ? 'Permission Granted' : subscriptionStatus === 'denied' ? 'Permission Denied' : 'Setting up...'}
              </div>
            </div>
            
            {#if isLoading && autoSubscribing}
              <div class="alert alert-info">
                <span class="loading loading-spinner loading-sm"></span>
                <span class="ml-2">Setting up push notifications...</span>
              </div>
            {:else if subscriptionStatus === 'subscribed'}
              <div class="alert alert-success">
                <span>✓ You are subscribed to push notifications! You will receive notifications sent by administrators.</span>
              </div>
            {:else if subscriptionStatus === 'denied'}
              <div class="alert alert-error">
                <span>Notification permission was denied. Please enable notifications in your browser settings to receive push notifications.</span>
              </div>
            {:else if subscriptionStatus === 'default'}
              <div class="alert alert-warning">
                <span>Notification permission is required. Please allow notifications when prompted.</span>
              </div>
            {/if}
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>

