<script>
  import axios from 'axios';
  import { onMount } from 'svelte';

  let subscriptionStatus = 'not-supported';
  let subscription = null;
  let vapidPublicKey = null;
  let userId = '';
  let pushTitle = 'Test Notification';
  let pushBody = 'This is a test push notification';
  let isLoading = false;
  let message = '';

  // Check if push notifications are supported
  function checkSupport() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
      subscriptionStatus = 'not-supported';
      return false;
    }
    return true;
  }

  // Get VAPID public key from server
  async function fetchVapidPublicKey() {
    try {
      const response = await axios.get('/vapid-public-key');
      vapidPublicKey = response.data.publicKey;
    } catch (error) {
      console.error('Error fetching VAPID public key:', error);
      message = 'Failed to fetch VAPID public key';
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
      } else if (permission === 'denied') {
        subscriptionStatus = 'denied';
        message = 'Notification permission denied';
      } else {
        subscriptionStatus = 'default';
        message = 'Notification permission default';
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
      message = 'VAPID key not loaded. Please refresh the page or check backend connection.';
      console.error('VAPID key is null. Backend may not be responding.');
      return;
    }

    if (subscriptionStatus !== 'granted') {
      await requestPermission();
      if (subscriptionStatus !== 'granted') {
        message = 'Notification permission is required to subscribe. Please grant permission first.';
        return;
      }
    }

    try {
      isLoading = true;
      message = 'Registering service worker...';
      
      // Wait for service worker to be ready
      let registration;
      try {
        registration = await navigator.serviceWorker.ready;
        console.log('Service worker ready:', registration);
      } catch (error) {
        console.error('Service worker not ready:', error);
        message = 'Service worker not ready. Please refresh the page and try again.';
        return;
      }

      message = 'Creating push subscription...';
      
      // Create push subscription
      let pushSubscription;
      try {
        const applicationServerKey = urlBase64ToUint8Array(vapidPublicKey);
        console.log('VAPID key length:', vapidPublicKey.length);
        console.log('Application server key array length:', applicationServerKey.length);
        
        pushSubscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: applicationServerKey
        });
        console.log('Push subscription created:', pushSubscription);
      } catch (error) {
        console.error('Push subscription error:', error);
        if (error.name === 'NotAllowedError') {
          message = 'Notification permission denied. Please enable notifications in browser settings.';
        } else if (error.name === 'NotSupportedError') {
          message = 'Push notifications not supported. Try a different browser.';
        } else if (error.message?.includes('Invalid key')) {
          message = 'Invalid VAPID key format. Please check backend configuration.';
        } else {
          message = `Failed to create push subscription: ${error.message || error.name || 'Unknown error'}`;
        }
        return;
      }

      message = 'Saving subscription to server...';
      
      // Prepare subscription data
      const subscriptionData = {
        endpoint: pushSubscription.endpoint,
        keys: {
          p256dh: arrayBufferToBase64(pushSubscription.getKey('p256dh')),
          auth: arrayBufferToBase64(pushSubscription.getKey('auth'))
        },
        user_id: userId || null
      };
      console.log('Subscription data prepared:', {
        endpoint: subscriptionData.endpoint,
        user_id: subscriptionData.user_id,
        has_keys: !!subscriptionData.keys.p256dh && !!subscriptionData.keys.auth
      });

      // Send to backend
      try {
        const response = await axios.post('/subscribe', subscriptionData);
        console.log('Subscription saved to backend:', response.data);
      } catch (error) {
        console.error('Backend subscription error:', error);
        if (error.response) {
          message = `Backend error: ${error.response.data?.detail || error.response.statusText} (${error.response.status})`;
        } else if (error.request) {
          message = 'Cannot connect to backend. Check if backend is running.';
        } else {
          message = `Error saving subscription: ${error.message}`;
        }
        return;
      }
      
      subscription = pushSubscription;
      subscriptionStatus = 'subscribed';
      message = 'Successfully subscribed to push notifications!';
    } catch (error) {
      console.error('Unexpected error during subscription:', error);
      message = `Failed to subscribe: ${error.message || 'Unknown error'}`;
    } finally {
      isLoading = false;
    }
  }

  // Unsubscribe from push notifications
  async function unsubscribe() {
    if (!subscription) {
      message = 'No active subscription';
      return;
    }

    try {
      isLoading = true;
      const success = await subscription.unsubscribe();
      
      if (success) {
        subscription = null;
        subscriptionStatus = 'granted';
        message = 'Successfully unsubscribed from push notifications';
      } else {
        message = 'Failed to unsubscribe';
      }
    } catch (error) {
      console.error('Error unsubscribing:', error);
      message = 'Error unsubscribing from push notifications';
    } finally {
      isLoading = false;
    }
  }

  // Send test push to single user
  async function sendSinglePush() {
    if (!userId) {
      message = 'Please enter a user ID';
      return;
    }

    try {
      isLoading = true;
      const payload = {
        title: pushTitle,
        body: pushBody,
        data: { timestamp: new Date().toISOString() }
      };

      await axios.post(`/push/single/${userId}`, payload);
      message = `Push notification sent to user ${userId}`;
    } catch (error) {
      console.error('Error sending push:', error);
      message = error.response?.data?.detail || 'Failed to send push notification';
    } finally {
      isLoading = false;
    }
  }

  // Send broadcast push to all users
  async function sendBroadcastPush() {
    try {
      isLoading = true;
      const payload = {
        title: pushTitle,
        body: pushBody,
        data: { timestamp: new Date().toISOString() }
      };

      const response = await axios.post('/push/broadcast', payload);
      message = `Broadcast sent: ${response.data.success_count} successful, ${response.data.failed_count} failed`;
    } catch (error) {
      console.error('Error sending broadcast:', error);
      message = error.response?.data?.detail || 'Failed to send broadcast';
    } finally {
      isLoading = false;
    }
  }

  // Check existing subscription on mount
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

  // Utility: Convert VAPID key from base64 URL to Uint8Array
  // VAPID keys are stored as 64 bytes (x + y coordinates)
  // But PushManager.subscribe() requires 65 bytes (0x04 + x + y)
  function urlBase64ToUint8Array(base64String) {
    if (!base64String) {
      throw new Error('VAPID key is empty');
    }

    // Add padding if needed (base64 URL-safe doesn't use padding)
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');

    // Decode base64 to binary string
    let rawData;
    try {
      rawData = window.atob(base64);
    } catch (error) {
      throw new Error(`Invalid base64 encoding: ${error.message}`);
    }

    // VAPID public key should be 64 bytes (x + y coordinates)
    // PushManager requires 65 bytes with 0x04 prefix (uncompressed point format)
    if (rawData.length !== 64) {
      throw new Error(`Invalid VAPID key length: expected 64 bytes, got ${rawData.length}`);
    }

    // Create Uint8Array with 65 bytes: 0x04 prefix + 64 bytes of key data
    const outputArray = new Uint8Array(65);
    outputArray[0] = 0x04; // Uncompressed point indicator
    
    // Copy the 64 bytes of key data
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i + 1] = rawData.charCodeAt(i);
    }
    
    return outputArray;
  }

  // Utility: Convert ArrayBuffer to base64
  function arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  }

  onMount(() => {
    checkSupport();
    fetchVapidPublicKey();
    checkExistingSubscription();
  });
</script>

<div class="min-h-screen bg-base-200 p-4">
  <div class="max-w-4xl mx-auto">
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h1 class="card-title text-3xl mb-4">Web Push Notification PWA</h1>
        
        {#if message}
          <div class="alert alert-info mb-4">
            <span>{message}</span>
          </div>
        {/if}

        {#if subscriptionStatus === 'not-supported'}
          <div class="alert alert-error">
            <span>Push notifications are not supported in this browser</span>
          </div>
        {:else}
          <!-- Subscription Status -->
          <div class="card bg-base-200 mb-4">
            <div class="card-body">
              <h2 class="card-title">Subscription Status</h2>
              <div class="badge badge-lg {subscriptionStatus === 'subscribed' ? 'badge-success' : subscriptionStatus === 'granted' ? 'badge-warning' : 'badge-error'}">
                {subscriptionStatus === 'subscribed' ? 'Subscribed' : subscriptionStatus === 'granted' ? 'Permission Granted' : subscriptionStatus === 'denied' ? 'Permission Denied' : 'Not Subscribed'}
              </div>
            </div>
          </div>

          <!-- Permission and Subscription Controls -->
          <div class="card bg-base-200 mb-4">
            <div class="card-body">
              <h2 class="card-title">Permission & Subscription</h2>
              
              <div class="form-control mb-4">
                <label class="label">
                  <span class="label-text">User ID (optional)</span>
                </label>
                <input 
                  type="text" 
                  placeholder="Enter user ID" 
                  class="input input-bordered w-full"
                  bind:value={userId}
                />
              </div>

              <div class="flex gap-2 flex-wrap">
                {#if subscriptionStatus !== 'granted' && subscriptionStatus !== 'subscribed'}
                  <button class="btn btn-primary" on:click={requestPermission} disabled={isLoading}>
                    {isLoading ? 'Loading...' : 'Request Permission'}
                  </button>
                {/if}
                
                {#if subscriptionStatus === 'granted' || subscriptionStatus === 'subscribed'}
                  {#if subscriptionStatus !== 'subscribed'}
                    <button class="btn btn-success" on:click={subscribe} disabled={isLoading}>
                      {isLoading ? 'Loading...' : 'Subscribe'}
                    </button>
                  {/if}
                  
                  {#if subscriptionStatus === 'subscribed'}
                    <button class="btn btn-error" on:click={unsubscribe} disabled={isLoading}>
                      {isLoading ? 'Loading...' : 'Unsubscribe'}
                    </button>
                  {/if}
                {/if}
              </div>
            </div>
          </div>

          <!-- Send Push Notifications -->
          <div class="card bg-base-200 mb-4">
            <div class="card-body">
              <h2 class="card-title">Send Push Notifications</h2>
              
              <div class="form-control mb-4">
                <label class="label">
                  <span class="label-text">Notification Title</span>
                </label>
                <input 
                  type="text" 
                  placeholder="Notification title" 
                  class="input input-bordered w-full"
                  bind:value={pushTitle}
                />
              </div>

              <div class="form-control mb-4">
                <label class="label">
                  <span class="label-text">Notification Body</span>
                </label>
                <textarea 
                  placeholder="Notification body" 
                  class="textarea textarea-bordered w-full"
                  bind:value={pushBody}
                ></textarea>
              </div>

              <div class="flex gap-2 flex-wrap">
                <button class="btn btn-warning" on:click={sendSinglePush} disabled={isLoading || !userId}>
                  {isLoading ? 'Sending...' : 'Send to User'}
                </button>
                <button class="btn btn-info" on:click={sendBroadcastPush} disabled={isLoading}>
                  {isLoading ? 'Sending...' : 'Broadcast to All'}
                </button>
              </div>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>

