<script>
  import axios from 'axios';
  import { onMount } from 'svelte';

  let isAuthenticated = false;
  let username = '';
  let password = '';
  let token = localStorage.getItem('admin_token') || '';
  let isLoading = false;
  let message = '';
  let messageType = 'info'; // info, success, error

  // Applications state
  let applications = [];
  let showAppForm = false;
  let appFormData = { name: '', store_fingerprint: '' };
  let editingApp = null;

  // Users state
  let users = [];
  let totalUsers = 0;
  let currentPage = 1;
  let limit = 10;
  let filterAppName = '';
  let selectedUser = null;

  // Set axios default auth header
  function setAuthHeader() {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      isAuthenticated = true;
    }
  }

  // Login function
  async function login() {
    if (!username || !password) {
      showMessage('Please enter username and password', 'error');
      return;
    }

    try {
      isLoading = true;
      const response = await axios.post('/admin/login', { username, password });
      token = response.data.access_token;
      localStorage.setItem('admin_token', token);
      setAuthHeader();
      isAuthenticated = true;
      showMessage('Login successful', 'success');
      username = '';
      password = '';
      await loadApplications();
      await loadUsers();
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Login failed', 'error');
    } finally {
      isLoading = false;
    }
  }

  // Logout function
  function logout() {
    token = '';
    localStorage.removeItem('admin_token');
    delete axios.defaults.headers.common['Authorization'];
    isAuthenticated = false;
    applications = [];
    users = [];
    showMessage('Logged out successfully', 'success');
  }

  // Show message
  function showMessage(msg, type = 'info') {
    message = msg;
    messageType = type;
    setTimeout(() => {
      message = '';
    }, 5000);
  }

  // Load applications
  async function loadApplications() {
    try {
      const response = await axios.get('/admin/applications');
      applications = response.data;
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to load applications', 'error');
    }
  }

  // Create application
  async function createApplication() {
    if (!appFormData.name) {
      showMessage('Application name is required', 'error');
      return;
    }

    try {
      isLoading = true;
      const response = await axios.post('/admin/applications', {
        name: appFormData.name,
        store_fingerprint: appFormData.store_fingerprint || null
      });
      
      showMessage(`Application created! Secret: ${response.data.secret}`, 'success');
      appFormData = { name: '', store_fingerprint: '' };
      showAppForm = false;
      await loadApplications();
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to create application', 'error');
    } finally {
      isLoading = false;
    }
  }

  // Reset application secret
  async function resetSecret(appId) {
    if (!confirm('Are you sure you want to reset the secret? The old secret will no longer work.')) {
      return;
    }

    try {
      isLoading = true;
      const response = await axios.post(`/admin/applications/${appId}/reset-secret`);
      showMessage(`Secret reset! New secret: ${response.data.secret}`, 'success');
      await loadApplications();
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to reset secret', 'error');
    } finally {
      isLoading = false;
    }
  }

  // Load users
  async function loadUsers() {
    try {
      const offset = (currentPage - 1) * limit;
      const params = { limit, offset };
      if (filterAppName) {
        params.application_name = filterAppName;
      }
      
      const response = await axios.get('/admin/users', { params });
      users = response.data.users;
      totalUsers = response.data.total;
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to load users', 'error');
    }
  }

  // Get user details
  async function getUserDetails(userId) {
    try {
      const response = await axios.get(`/admin/users/${userId}`);
      selectedUser = response.data;
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to load user details', 'error');
    }
  }

  // Filter users by application
  function filterUsers() {
    currentPage = 1;
    loadUsers();
  }

  // Pagination
  function goToPage(page) {
    currentPage = page;
    loadUsers();
  }

  const totalPages = Math.ceil(totalUsers / limit);

  onMount(() => {
    if (token) {
      setAuthHeader();
      loadApplications();
      loadUsers();
    }
  });
</script>

<div class="min-h-screen bg-base-200 p-4">
  <div class="max-w-7xl mx-auto">
    {#if !isAuthenticated}
      <!-- Login Form -->
      <div class="card bg-base-100 shadow-xl max-w-md mx-auto">
        <div class="card-body">
          <h1 class="card-title text-3xl mb-4">Admin Login</h1>
          
          {#if message}
            <div class="alert alert-{messageType === 'error' ? 'error' : 'success'} mb-4">
              <span>{message}</span>
            </div>
          {/if}

          <div class="form-control mb-4">
            <label class="label">
              <span class="label-text">Username</span>
            </label>
            <input 
              type="text" 
              placeholder="Enter username" 
              class="input input-bordered w-full"
              bind:value={username}
              on:keydown={(e) => e.key === 'Enter' && login()}
            />
          </div>

          <div class="form-control mb-4">
            <label class="label">
              <span class="label-text">Password</span>
            </label>
            <input 
              type="password" 
              placeholder="Enter password" 
              class="input input-bordered w-full"
              bind:value={password}
              on:keydown={(e) => e.key === 'Enter' && login()}
            />
          </div>

          <button class="btn btn-primary w-full" on:click={login} disabled={isLoading}>
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </div>
      </div>
    {:else}
      <!-- Dashboard -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <div class="flex justify-between items-center mb-4">
            <h1 class="card-title text-3xl">Admin Dashboard</h1>
            <button class="btn btn-error" on:click={logout}>Logout</button>
          </div>

          {#if message}
            <div class="alert alert-{messageType === 'error' ? 'error' : messageType === 'success' ? 'success' : 'info'} mb-4">
              <span>{message}</span>
            </div>
          {/if}

          <!-- Applications Section -->
          <div class="card bg-base-200 mb-6">
            <div class="card-body">
              <div class="flex justify-between items-center mb-4">
                <h2 class="card-title text-2xl">Applications</h2>
                <button class="btn btn-primary" on:click={() => { showAppForm = !showAppForm; editingApp = null; appFormData = { name: '', store_fingerprint: '' }; }}>
                  {showAppForm ? 'Cancel' : 'Create Application'}
                </button>
              </div>

              {#if showAppForm}
                <div class="card bg-base-100 mb-4">
                  <div class="card-body">
                    <h3 class="card-title">Create New Application</h3>
                    <div class="form-control mb-4">
                      <label class="label">
                        <span class="label-text">Application Name *</span>
                      </label>
                      <input 
                        type="text" 
                        placeholder="Enter application name" 
                        class="input input-bordered w-full"
                        bind:value={appFormData.name}
                      />
                    </div>
                    <div class="form-control mb-4">
                      <label class="label">
                        <span class="label-text">Store Fingerprint (optional)</span>
                      </label>
                      <input 
                        type="text" 
                        placeholder="Enter store fingerprint" 
                        class="input input-bordered w-full"
                        bind:value={appFormData.store_fingerprint}
                      />
                    </div>
                    <button class="btn btn-success" on:click={createApplication} disabled={isLoading}>
                      {isLoading ? 'Creating...' : 'Create'}
                    </button>
                  </div>
                </div>
              {/if}

              {#if applications.length === 0}
                <p class="text-center text-gray-500">No applications found. Create one to get started.</p>
              {:else}
                <div class="overflow-x-auto">
                  <table class="table table-zebra w-full">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Store Fingerprint</th>
                        <th>Created At</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {#each applications as app}
                        <tr>
                          <td>{app.name}</td>
                          <td>{app.store_fingerprint || '-'}</td>
                          <td>{new Date(app.created_at).toLocaleString()}</td>
                          <td>
                            <button class="btn btn-sm btn-warning" on:click={() => resetSecret(app.id)} disabled={isLoading}>
                              Reset Secret
                            </button>
                          </td>
                        </tr>
                      {/each}
                    </tbody>
                  </table>
                </div>
              {/if}
            </div>
          </div>

          <!-- Users Section -->
          <div class="card bg-base-200">
            <div class="card-body">
              <h2 class="card-title text-2xl mb-4">Users</h2>

              <!-- Filter -->
              <div class="form-control mb-4">
                <div class="flex gap-2">
                  <input 
                    type="text" 
                    placeholder="Filter by application name" 
                    class="input input-bordered flex-1"
                    bind:value={filterAppName}
                    on:keydown={(e) => e.key === 'Enter' && filterUsers()}
                  />
                  <button class="btn btn-primary" on:click={filterUsers}>Filter</button>
                  {#if filterAppName}
                    <button class="btn btn-ghost" on:click={() => { filterAppName = ''; filterUsers(); }}>Clear</button>
                  {/if}
                </div>
              </div>

              {#if users.length === 0}
                <p class="text-center text-gray-500">No users found.</p>
              {:else}
                <div class="overflow-x-auto mb-4">
                  <table class="table table-zebra w-full">
                    <thead>
                      <tr>
                        <th>User ID</th>
                        <th>Application</th>
                        <th>Endpoint</th>
                        <th>Created At</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {#each users as user}
                        <tr>
                          <td>{user.user_id || '-'}</td>
                          <td>{user.application_name || '-'}</td>
                          <td class="max-w-xs truncate">{user.endpoint}</td>
                          <td>{new Date(user.created_at).toLocaleString()}</td>
                          <td>
                            <button class="btn btn-sm btn-info" on:click={() => getUserDetails(user.id)}>View Details</button>
                          </td>
                        </tr>
                      {/each}
                    </tbody>
                  </table>
                </div>

                <!-- Pagination -->
                <div class="flex justify-center items-center gap-2">
                  <button class="btn btn-sm" on:click={() => goToPage(currentPage - 1)} disabled={currentPage === 1}>
                    Previous
                  </button>
                  <span class="text-sm">Page {currentPage} of {totalPages} (Total: {totalUsers})</span>
                  <button class="btn btn-sm" on:click={() => goToPage(currentPage + 1)} disabled={currentPage >= totalPages}>
                    Next
                  </button>
                </div>
              {/if}
            </div>
          </div>

          <!-- User Details Modal -->
          {#if selectedUser}
            <div class="modal modal-open">
              <div class="modal-box">
                <h3 class="font-bold text-lg mb-4">User Details</h3>
                <div class="space-y-2">
                  <p><strong>ID:</strong> {selectedUser.id}</p>
                  <p><strong>User ID:</strong> {selectedUser.user_id || '-'}</p>
                  <p><strong>Application:</strong> {selectedUser.application_name || '-'}</p>
                  <p><strong>Endpoint:</strong> <span class="text-xs break-all">{selectedUser.endpoint}</span></p>
                  <p><strong>Created At:</strong> {new Date(selectedUser.created_at).toLocaleString()}</p>
                </div>
                <div class="modal-action">
                  <button class="btn" on:click={() => selectedUser = null}>Close</button>
                </div>
              </div>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>

