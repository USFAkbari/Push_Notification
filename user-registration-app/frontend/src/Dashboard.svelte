<script>
  import { onMount } from 'svelte';
  import { getCurrentUser, subscribeToPush, sendPush, logout, isAuthenticated } from './services/api.js';
  import { getFingerprint } from './services/fingerprint.js';
  
  const PUSH_SERVICE_URL = import.meta.env.VITE_PUSH_SERVICE_URL || 'http://localhost:8000/api-v1';
  
  let user = null;
  let subscriptionStatus = 'not-supported';
  let subscription = null;
  let vapidPublicKey = null;
  let isLoading = false;
  let message = '';
  let messageType = 'info';
  
  // Push notification form
  let pushTitle = '';
  let pushBody = '';
  
  // Check if push notifications are supported
  function checkSupport() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
      subscriptionStatus = 'not-supported';
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
      return;
    }
    
    try {
      isLoading = true;
      const permission = await Notification.requestPermission();
      
      if (permission === 'granted') {
        subscriptionStatus = 'granted';
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
      }
    } catch (error) {
      console.error('Error requesting permission:', error);
      message = 'Error requesting notification permission';
    } finally {
      isLoading = false;
    }
  }
  
  // Subscribe to push notifications
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
      }
    }
    
    try {
      isLoading = true;
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
      return;
    }
    
    try {
      const registration = await navigator.serviceWorker.ready;
      const existingSubscription = await registration.pushManager.getSubscription();
      
      if (existingSubscription) {
        subscription = existingSubscription;
        subscriptionStatus = 'subscribed';
      } else {
        const permission = Notification.permission;
        if (permission === 'granted') {
          subscriptionStatus = 'granted';
        } else if (permission === 'denied') {
          subscriptionStatus = 'denied';
        } else {
          subscriptionStatus = 'default';
        }
      }
    } catch (error) {
      console.error('Error checking subscription:', error);
    }
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
    await checkExistingSubscription();
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
            {/if}
          {/if}
        </div>
      </div>
      
      <!-- Send Test Push -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Send Test Push Notification</h2>
          <p class="text-sm text-gray-600 mb-4">Send a test push notification to yourself</p>
          
          <div class="form-control mb-4">
            <label class="label" for="dashboard-push-title">
              <span class="label-text">Title</span>
            </label>
            <input 
              id="dashboard-push-title"
              type="text" 
              placeholder="Notification title" 
              class="input input-bordered"
              bind:value={pushTitle}
              disabled={isLoading}
            />
          </div>
          
          <div class="form-control mb-4">
            <label class="label" for="dashboard-push-body">
              <span class="label-text">Body</span>
            </label>
            <textarea 
              id="dashboard-push-body"
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
    {/if}
  </div>
</div>

