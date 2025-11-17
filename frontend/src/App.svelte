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
    if (!checkSupport() || !vapidPublicKey) {
      message = 'Push notifications not supported or VAPID key not loaded';
      return;
    }

    if (subscriptionStatus !== 'granted') {
      await requestPermission();
      if (subscriptionStatus !== 'granted') {
        return;
      }
    }

    try {
      isLoading = true;
      const registration = await navigator.serviceWorker.ready;
      
      const pushSubscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
      });

      const subscriptionData = {
        endpoint: pushSubscription.endpoint,
        keys: {
          p256dh: arrayBufferToBase64(pushSubscription.getKey('p256dh')),
          auth: arrayBufferToBase64(pushSubscription.getKey('auth'))
        },
        user_id: userId || null
      };

      await axios.post('/subscribe', subscriptionData);
      
      subscription = pushSubscription;
      subscriptionStatus = 'subscribed';
      message = 'Successfully subscribed to push notifications';
    } catch (error) {
      console.error('Error subscribing:', error);
      message = 'Failed to subscribe to push notifications';
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
  function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
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

