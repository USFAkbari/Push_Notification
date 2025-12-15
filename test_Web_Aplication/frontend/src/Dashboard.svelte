<script>
  import { onMount } from 'svelte';
<<<<<<< HEAD
  import { getCurrentUser, subscribeToPush, logout, isAuthenticated } from './services/api.js';
=======
  import { getCurrentUser, subscribeToPush, sendPush, logout, isAuthenticated } from './services/api.js';
  import { getFingerprint } from './services/fingerprint.js';
>>>>>>> 02675bc (After Deploy Shamim)
  
  const PUSH_SERVICE_URL = import.meta.env.VITE_PUSH_SERVICE_URL || 'http://localhost:8000/api-v1';
  
  let user = null;
  let subscriptionStatus = 'not-supported';
  let subscription = null;
  let vapidPublicKey = null;
  let isLoading = false;
  let message = '';
  let messageType = 'info';
<<<<<<< HEAD
  let autoSubscribing = false;
  let supportErrorType = null; // 'browser', 'https', 'incognito'
  
  // Detect Incognito/Private mode
  async function detectIncognitoMode() {
    try {
      // Method 1: Check storage quota (works in Chrome/Edge)
      if ('storage' in navigator && 'estimate' in navigator.storage) {
        const estimate = await navigator.storage.estimate();
        // In Incognito mode, quota is typically very limited (around 120MB)
        if (estimate.quota && estimate.quota < 120000000) {
          return true;
        }
      }
      
      // Method 2: Try to write to localStorage (works in some browsers)
      try {
        localStorage.setItem('__incognito_test__', 'test');
        localStorage.removeItem('__incognito_test__');
      } catch (e) {
        // If we can't write to localStorage, might be Incognito
        return true;
      }
      
      // Method 3: Check for service worker limitations in Incognito
      // Service workers are disabled in Incognito mode in some browsers
      if ('serviceWorker' in navigator) {
        try {
          const registration = await navigator.serviceWorker.getRegistration();
          // If we can't get registration and it's not a secure context issue, might be Incognito
        } catch (e) {
          // Could be Incognito, but also could be other issues
        }
      }
      
      return false;
    } catch (error) {
      console.warn('Could not detect Incognito mode:', error);
      return false;
    }
  }
  
  // Check if push notifications are supported
  async function checkSupport() {
    // Check for service worker support
    if (!('serviceWorker' in navigator)) {
      subscriptionStatus = 'not-supported';
      supportErrorType = 'browser';
      console.warn('Service Worker is not supported in this browser');
      message = 'Service Worker is not supported in this browser. Please use a modern browser.';
      messageType = 'error';
      return false;
    }
    
    // Check for Push Manager support
    if (!('PushManager' in window)) {
      subscriptionStatus = 'not-supported';
      supportErrorType = 'browser';
      console.warn('Push Manager is not supported in this browser');
      message = 'Push Manager is not supported in this browser. Please use a modern browser.';
      messageType = 'error';
      return false;
    }
    
    // Check for Notification API support
    if (!('Notification' in window)) {
      subscriptionStatus = 'not-supported';
      supportErrorType = 'browser';
      console.warn('Notifications API is not supported in this browser');
      message = 'Notifications API is not supported in this browser. Please use a modern browser.';
      messageType = 'error';
      return false;
    }
    
    // Check if we're on HTTPS or localhost (required for push notifications)
    // Allow 0.0.0.0 for development
    const isSecureContext = window.isSecureContext || 
                            location.protocol === 'https:' || 
                            location.hostname === 'localhost' || 
                            location.hostname === '127.0.0.1' ||
                            location.hostname === '0.0.0.0';
    
    if (!isSecureContext) {
      subscriptionStatus = 'not-supported';
      supportErrorType = 'https';
      console.warn('Push notifications require HTTPS or localhost');
      message = 'Push notifications require HTTPS or localhost. Please access this site using localhost:3001 instead of 0.0.0.0:3001, or use HTTPS.';
      messageType = 'error';
      return false;
    }
    
    // Check for Incognito mode
    const isIncognito = await detectIncognitoMode();
    if (isIncognito) {
      subscriptionStatus = 'not-supported';
      supportErrorType = 'incognito';
      console.warn('Push notifications are not available in Incognito/Private mode');
      message = 'Push notifications are not available in Incognito/Private browsing mode. Please use a regular browser window.';
      messageType = 'error';
      return false;
    }
    
=======
  
  // Push notification form
  let pushTitle = '';
  let pushBody = '';
  
  // Check if push notifications are supported
  function checkSupport() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
      subscriptionStatus = 'not-supported';
      return false;
    }
>>>>>>> 02675bc (After Deploy Shamim)
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
<<<<<<< HEAD
    const isSupported = await checkSupport();
    if (!isSupported) {
      // Error message already set by checkSupport()
      return false;
    }
    
    try {
=======
    if (!checkSupport()) {
      message = 'Push notifications are not supported in this browser';
      return;
    }
    
    try {
      isLoading = true;
>>>>>>> 02675bc (After Deploy Shamim)
      const permission = await Notification.requestPermission();
      
      if (permission === 'granted') {
        subscriptionStatus = 'granted';
<<<<<<< HEAD
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
=======
        message = 'Notification permission granted';
        messageType = 'success';
      } else if (permission === 'denied') {
        subscriptionStatus = 'denied';
        message = 'Notification permission denied';
        messageType = 'error';
      } else {
        subscriptionStatus = 'default';
        message = 'Notification permission default';
        messageType = 'info';
>>>>>>> 02675bc (After Deploy Shamim)
      }
    } catch (error) {
      console.error('Error requesting permission:', error);
      message = 'Error requesting notification permission';
<<<<<<< HEAD
      messageType = 'error';
      return false;
=======
    } finally {
      isLoading = false;
>>>>>>> 02675bc (After Deploy Shamim)
    }
  }
  
  // Subscribe to push notifications
<<<<<<< HEAD
  async function subscribe(silent = false) {
    const isSupported = await checkSupport();
    if (!isSupported) {
      // Error message already set by checkSupport()
      if (silent) {
        message = '';
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
=======
  async function subscribe() {
    if (!checkSupport()) {
      message = 'Push notifications are not supported in this browser';
      return;
    }
    
    if (!vapidPublicKey) {
      message = 'VAPID key not loaded. Please refresh the page.';
      return;
    }
    
    if (subscriptionStatus !== 'granted') {
      await requestPermission();
      if (subscriptionStatus !== 'granted') {
        message = 'Notification permission is required to subscribe.';
        return;
>>>>>>> 02675bc (After Deploy Shamim)
      }
    }
    
    try {
      isLoading = true;
<<<<<<< HEAD
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
=======
      message = 'Registering service worker...';
      
      // Register service worker
      const registration = await navigator.serviceWorker.register('/service-worker.js');
      await navigator.serviceWorker.ready;
      
      message = 'Creating push subscription...';
      
      // Create push subscription
      const applicationServerKey = urlBase64ToUint8Array(vapidPublicKey);
      const pushSubscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: applicationServerKey
      });
      
      message = 'Saving subscription...';
>>>>>>> 02675bc (After Deploy Shamim)
      
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
<<<<<<< HEAD
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
=======
        message = 'Successfully subscribed to push notifications!';
        messageType = 'success';
      } else {
        message = 'Failed to subscribe: ' + (result.message || 'Unknown error');
        messageType = 'error';
      }
    } catch (error) {
      console.error('Subscription error:', error);
      message = `Failed to subscribe: ${error.message || 'Unknown error'}`;
      messageType = 'error';
    } finally {
      isLoading = false;
    }
  }
  
  // Send test push notification
  async function sendTestPush() {
    if (!pushTitle.trim() || !pushBody.trim()) {
      message = 'Please fill in title and body';
      messageType = 'error';
      return;
    }
    
    try {
      isLoading = true;
      message = 'Sending push notification...';
      
      const result = await sendPush({
        title: pushTitle.trim(),
        body: pushBody.trim()
      });
      
      if (result.success) {
        message = 'Push notification sent successfully!';
        messageType = 'success';
        pushTitle = '';
        pushBody = '';
      } else {
        message = 'Failed to send push: ' + (result.message || 'Unknown error');
        messageType = 'error';
      }
    } catch (error) {
      console.error('Send push error:', error);
      message = `Failed to send push: ${error.response?.data?.detail || error.message || 'Unknown error'}`;
      messageType = 'error';
    } finally {
      isLoading = false;
>>>>>>> 02675bc (After Deploy Shamim)
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
<<<<<<< HEAD
    const isSupported = await checkSupport();
    if (!isSupported) {
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
=======
    if (!checkSupport()) {
      return;
    }
    
    try {
      const registration = await navigator.serviceWorker.ready;
>>>>>>> 02675bc (After Deploy Shamim)
      const existingSubscription = await registration.pushManager.getSubscription();
      
      if (existingSubscription) {
        subscription = existingSubscription;
        subscriptionStatus = 'subscribed';
<<<<<<< HEAD
        return true;
=======
>>>>>>> 02675bc (After Deploy Shamim)
      } else {
        const permission = Notification.permission;
        if (permission === 'granted') {
          subscriptionStatus = 'granted';
        } else if (permission === 'denied') {
          subscriptionStatus = 'denied';
        } else {
          subscriptionStatus = 'default';
        }
<<<<<<< HEAD
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
  
=======
      }
    } catch (error) {
      console.error('Error checking subscription:', error);
    }
  }
  
>>>>>>> 02675bc (After Deploy Shamim)
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
<<<<<<< HEAD
    await checkSupport();
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
=======
    checkSupport();
    await fetchVapidPublicKey();
    await checkExistingSubscription();
>>>>>>> 02675bc (After Deploy Shamim)
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
<<<<<<< HEAD
          <div class="flex justify-between items-center mb-4">
            <h2 class="card-title">Push Notifications</h2>
            {#if subscriptionStatus === 'subscribed'}
              <div class="badge badge-success badge-lg">Subscribed</div>
            {:else if subscriptionStatus === 'granted'}
              <div class="badge badge-warning badge-lg">Permission Granted</div>
            {:else if subscriptionStatus === 'denied'}
              <div class="badge badge-error badge-lg">Permission Denied</div>
            {:else if subscriptionStatus === 'not-supported'}
              <div class="badge badge-error badge-lg">Not Supported</div>
            {:else}
              <div class="badge badge-info badge-lg">Not Subscribed</div>
            {/if}
          </div>
          
          {#if subscriptionStatus === 'not-supported'}
            <div class="alert alert-error mb-4">
              <div class="flex flex-col gap-2">
                <span class="font-bold">Push notifications are not available:</span>
                {#if supportErrorType === 'incognito'}
                  <div class="ml-4">
                    <p class="mb-2">• You are using Incognito/Private browsing mode</p>
                    <p class="text-sm opacity-90">Solution: Please exit Incognito mode and use a regular browser window. Push notifications require a regular browsing session.</p>
                  </div>
                {:else if supportErrorType === 'https'}
                  <div class="ml-4">
                    <p class="mb-2">• Connection is not secure (HTTP instead of HTTPS)</p>
                    <p class="text-sm opacity-90">Solution: Access the site using <code class="bg-base-300 px-1 rounded">localhost:3001</code> instead of <code class="bg-base-300 px-1 rounded">0.0.0.0:3001</code>, or use HTTPS in production.</p>
                  </div>
                {:else if supportErrorType === 'browser'}
                  <div class="ml-4">
                    <p class="mb-2">• Browser does not support required features</p>
                    <p class="text-sm opacity-90">Solution: Please use a modern browser like Chrome, Firefox, Edge, or Safari with the latest version.</p>
                  </div>
                {:else}
                  <div class="ml-4">
                    <p class="mb-2">• Push notifications are not supported in this environment</p>
                    <p class="text-sm opacity-90">Please ensure you're using a modern browser, accessing via localhost or HTTPS, and not in Incognito mode.</p>
                  </div>
                {/if}
              </div>
            </div>
          {:else}
            {#if isLoading && autoSubscribing}
              <div class="alert alert-info mb-4">
                <span class="loading loading-spinner loading-sm"></span>
                <span class="ml-2">Setting up push notifications automatically...</span>
              </div>
            {:else if subscriptionStatus === 'subscribed'}
              <div class="alert alert-success mb-4">
                <span>✓ You are subscribed to push notifications! You will receive notifications sent by administrators.</span>
              </div>
            {:else if subscriptionStatus === 'denied'}
              <div class="alert alert-error mb-4">
                <span>Notification permission was denied. Please enable notifications in your browser settings to receive push notifications.</span>
              </div>
            {:else if subscriptionStatus === 'default'}
              <div class="alert alert-warning mb-4">
                <span>Notification permission is required. Click the Subscribe button below to enable push notifications.</span>
              </div>
            {:else if subscriptionStatus === 'granted'}
              <div class="alert alert-info mb-4">
                <span>Permission granted. Click Subscribe to complete the subscription process.</span>
              </div>
            {/if}
            
            <!-- Subscribe Button - Always visible when supported and not loading -->
            {#if subscriptionStatus !== 'not-supported'}
              <div class="flex gap-2">
                {#if subscriptionStatus === 'subscribed'}
                  <button 
                    class="btn btn-primary btn-lg flex-1" 
                    on:click={() => subscribe(false)}
                    disabled={isLoading}
                    title="Re-subscribe to push notifications"
                  >
                    {#if isLoading}
                      <span class="loading loading-spinner loading-sm"></span>
                      Subscribing...
                    {:else}
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                      </svg>
                      Re-subscribe
                    {/if}
                  </button>
                {:else}
                  <button 
                    class="btn btn-primary btn-lg flex-1" 
                    on:click={() => subscribe(false)}
                    disabled={isLoading}
                  >
                    {#if isLoading}
                      <span class="loading loading-spinner loading-sm"></span>
                      Subscribing...
                    {:else}
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                      </svg>
                      Subscribe to Push Notifications
                    {/if}
                  </button>
                {/if}
              </div>
=======
          <h2 class="card-title">Push Notifications</h2>
          
          {#if subscriptionStatus === 'not-supported'}
            <div class="alert alert-error">
              <span>Push notifications are not supported in this browser</span>
            </div>
          {:else}
            <div class="mb-4">
              <div class="badge badge-lg {subscriptionStatus === 'subscribed' ? 'badge-success' : subscriptionStatus === 'granted' ? 'badge-warning' : 'badge-error'}">
                {subscriptionStatus === 'subscribed' ? 'Subscribed' : subscriptionStatus === 'granted' ? 'Permission Granted' : subscriptionStatus === 'denied' ? 'Permission Denied' : 'Not Subscribed'}
              </div>
            </div>
            
            {#if subscriptionStatus !== 'subscribed'}
              <button 
                class="btn btn-primary" 
                on:click={subscribe}
                disabled={isLoading}
              >
                {#if isLoading}
                  <span class="loading loading-spinner"></span>
                  Subscribing...
                {:else}
                  Subscribe to Push Notifications
                {/if}
              </button>
            {:else}
              <p class="text-success">You are subscribed to push notifications!</p>
>>>>>>> 02675bc (After Deploy Shamim)
            {/if}
          {/if}
        </div>
      </div>
<<<<<<< HEAD
=======
      
      <!-- Send Test Push -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Send Test Push Notification</h2>
          <p class="text-sm text-gray-600 mb-4">Send a test push notification to yourself</p>
          
          <div class="form-control mb-4">
            <label class="label">
              <span class="label-text">Title</span>
            </label>
            <input 
              type="text" 
              placeholder="Notification title" 
              class="input input-bordered"
              bind:value={pushTitle}
              disabled={isLoading}
            />
          </div>
          
          <div class="form-control mb-4">
            <label class="label">
              <span class="label-text">Body</span>
            </label>
            <textarea 
              placeholder="Notification body" 
              class="textarea textarea-bordered"
              bind:value={pushBody}
              disabled={isLoading}
            ></textarea>
          </div>
          
          <div class="form-control">
            <button 
              class="btn btn-success" 
              on:click={sendTestPush}
              disabled={isLoading || !pushTitle.trim() || !pushBody.trim()}
            >
              {#if isLoading}
                <span class="loading loading-spinner"></span>
                Sending...
              {:else}
                Send Push Notification
              {/if}
            </button>
          </div>
        </div>
      </div>
>>>>>>> 02675bc (After Deploy Shamim)
    {/if}
  </div>
</div>

