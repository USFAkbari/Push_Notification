<script>
  import { getFingerprint } from './services/fingerprint.js';
  import { register } from './services/api.js';
  
  let username = '';
  let email = '';
  let password = '';
  let confirmPassword = '';
  let isLoading = false;
  let message = '';
  let messageType = 'info';
  let errors = {};
  
  async function handleSubmit() {
    // Reset errors
    errors = {};
    message = '';
    
    // Validation
    if (!username.trim()) {
      errors.username = 'Username is required';
      return;
    }
    if (!email.trim()) {
      errors.email = 'Email is required';
      return;
    }
    if (!email.includes('@')) {
      errors.email = 'Invalid email format';
      return;
    }
    if (!password) {
      errors.password = 'Password is required';
      return;
    }
    if (password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
      return;
    }
    if (password !== confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
      return;
    }
    
    try {
      isLoading = true;
      message = 'Generating device fingerprint...';
      
      // Get fingerprint
      const fingerprintData = await getFingerprint();
      const fingerprint = typeof fingerprintData === 'string' 
        ? fingerprintData 
        : fingerprintData.fingerprint;
      const deviceInfo = typeof fingerprintData === 'object' 
        ? fingerprintData.deviceInfo 
        : null;
      
      message = 'Registering...';
      
      // Register user
      const result = await register({
        username: username.trim(),
        email: email.trim(),
        password,
        fingerprint,
        device_info: deviceInfo
      });
      
      message = 'Registration successful! Redirecting to login...';
      messageType = 'success';
      
      // Redirect to login after 2 seconds
      setTimeout(() => {
        window.location.hash = '#/login';
      }, 2000);
      
    } catch (error) {
      console.error('Registration error:', error);
      if (error.response?.data?.detail) {
        message = error.response.data.detail;
      } else {
        message = 'Registration failed. Please try again.';
      }
      messageType = 'error';
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="min-h-screen bg-base-200 flex items-center justify-center p-4">
  <div class="card bg-base-100 shadow-xl w-full max-w-md">
    <div class="card-body">
      <h2 class="card-title text-2xl mb-4">Register</h2>
      
      {#if message}
        <div class="alert alert-{messageType === 'error' ? 'error' : messageType === 'success' ? 'success' : 'info'}">
          <span>{message}</span>
        </div>
      {/if}
      
      <form on:submit|preventDefault={handleSubmit}>
        <div class="form-control mb-4">
          <label class="label" for="register-username">
            <span class="label-text">Username</span>
          </label>
          <input 
            id="register-username"
            type="text" 
            placeholder="Enter username" 
            class="input input-bordered {errors.username ? 'input-error' : ''}"
            bind:value={username}
            disabled={isLoading}
          />
          {#if errors.username}
            <div class="label">
              <span class="label-text-alt text-error">{errors.username}</span>
            </div>
          {/if}
        </div>
        
        <div class="form-control mb-4">
          <label class="label" for="register-email">
            <span class="label-text">Email</span>
          </label>
          <input 
            id="register-email"
            type="email" 
            placeholder="Enter email" 
            class="input input-bordered {errors.email ? 'input-error' : ''}"
            bind:value={email}
            disabled={isLoading}
          />
          {#if errors.email}
            <div class="label">
              <span class="label-text-alt text-error">{errors.email}</span>
            </div>
          {/if}
        </div>
        
        <div class="form-control mb-4">
          <label class="label" for="register-password">
            <span class="label-text">Password</span>
          </label>
          <input 
            id="register-password"
            type="password" 
            placeholder="Enter password" 
            class="input input-bordered {errors.password ? 'input-error' : ''}"
            bind:value={password}
            disabled={isLoading}
          />
          {#if errors.password}
            <div class="label">
              <span class="label-text-alt text-error">{errors.password}</span>
            </div>
          {/if}
        </div>
        
        <div class="form-control mb-4">
          <label class="label" for="register-confirm-password">
            <span class="label-text">Confirm Password</span>
          </label>
          <input 
            id="register-confirm-password"
            type="password" 
            placeholder="Confirm password" 
            class="input input-bordered {errors.confirmPassword ? 'input-error' : ''}"
            bind:value={confirmPassword}
            disabled={isLoading}
          />
          {#if errors.confirmPassword}
            <div class="label">
              <span class="label-text-alt text-error">{errors.confirmPassword}</span>
            </div>
          {/if}
        </div>
        
        <div class="form-control mt-6">
          <button 
            class="btn btn-primary" 
            type="submit"
            disabled={isLoading}
          >
            {#if isLoading}
              <span class="loading loading-spinner"></span>
              Registering...
            {:else}
              Register
            {/if}
          </button>
        </div>
      </form>
      
      <div class="text-center mt-4">
        <a href="#/login" class="link link-primary">Already have an account? Login</a>
      </div>
    </div>
  </div>
</div>

