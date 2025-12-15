<script>
  import { login } from './services/api.js';
  
  let username = '';
  let password = '';
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
      errors.username = 'Username or email is required';
      return;
    }
    if (!password) {
      errors.password = 'Password is required';
      return;
    }
    
    try {
      isLoading = true;
      
      // Login
      const result = await login(username.trim(), password);
      
      message = 'Login successful! Redirecting...';
      messageType = 'success';
      
      // Redirect to dashboard after 1 second
      setTimeout(() => {
        window.location.hash = '#/dashboard';
      }, 1000);
      
    } catch (error) {
      console.error('Login error:', error);
      if (error.response?.data?.detail) {
        message = error.response.data.detail;
      } else {
        message = 'Login failed. Please check your credentials.';
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
      <h2 class="card-title text-2xl mb-4">Login</h2>
      
      {#if message}
        <div class="alert alert-{messageType === 'error' ? 'error' : messageType === 'success' ? 'success' : 'info'}">
          <span>{message}</span>
        </div>
      {/if}
      
      <form on:submit|preventDefault={handleSubmit}>
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text">Username or Email</span>
          </label>
          <input 
            type="text" 
            placeholder="Enter username or email" 
            class="input input-bordered {errors.username ? 'input-error' : ''}"
            bind:value={username}
            disabled={isLoading}
          />
          {#if errors.username}
            <label class="label">
              <span class="label-text-alt text-error">{errors.username}</span>
            </label>
          {/if}
        </div>
        
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text">Password</span>
          </label>
          <input 
            type="password" 
            placeholder="Enter password" 
            class="input input-bordered {errors.password ? 'input-error' : ''}"
            bind:value={password}
            disabled={isLoading}
          />
          {#if errors.password}
            <label class="label">
              <span class="label-text-alt text-error">{errors.password}</span>
            </label>
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
              Logging in...
            {:else}
              Login
            {/if}
          </button>
        </div>
      </form>
      
      <div class="text-center mt-4">
        <a href="#/register" class="link link-primary">Don't have an account? Register</a>
      </div>
    </div>
  </div>
</div>

