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
  let activeTab = 'applications'; // applications, users, push

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
  let filterAppId = '';
  let filterUserId = '';
  let filterCreatedFrom = '';
  let filterCreatedTo = '';
  let selectedUser = null;

  // Push notification state
  let pushTitle = '';
  let pushBody = '';
  let pushIcon = '';
  let pushBadge = '';
  let pushRecipientType = 'single'; // single, all, application, list
  let pushSelectedUserId = '';
  let pushSelectedAppId = '';
  let pushUserIds = ''; // comma-separated list
  let pushResult = null;
  let allUsersForSelection = [];

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
      await loadAllUsersForSelection();
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

  // Load all users for selection (for push notifications)
  async function loadAllUsersForSelection() {
    try {
      // Load first 1000 users for selection
      const response = await axios.get('/admin/users', { params: { limit: 1000, offset: 0 } });
      allUsersForSelection = response.data.users.filter(u => u.user_id).map(u => ({
        id: u.user_id,
        label: `${u.user_id}${u.application_name ? ` (${u.application_name})` : ''}`
      }));
    } catch (error) {
      console.error('Failed to load users for selection:', error);
    }
  }

  // Load users with filters
  async function loadUsers() {
    try {
      const offset = (currentPage - 1) * limit;
      const params = { limit, offset };
      
      if (filterAppName) {
        params.application_name = filterAppName;
      }
      if (filterAppId) {
        params.application_id = filterAppId;
      }
      if (filterUserId) {
        params.user_id = filterUserId;
      }
      if (filterCreatedFrom) {
        params.created_from = new Date(filterCreatedFrom).toISOString();
      }
      if (filterCreatedTo) {
        params.created_to = new Date(filterCreatedTo).toISOString();
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

  // Filter users
  function filterUsers() {
    currentPage = 1;
    loadUsers();
  }

  // Reset filters
  function resetFilters() {
    filterAppName = '';
    filterAppId = '';
    filterUserId = '';
    filterCreatedFrom = '';
    filterCreatedTo = '';
    currentPage = 1;
    loadUsers();
  }

  // Pagination
  function goToPage(page) {
    currentPage = page;
    loadUsers();
  }

  // Send push notification
  async function sendPushNotification() {
    if (!pushTitle || !pushBody) {
      showMessage('Title and body are required', 'error');
      return;
    }

    try {
      isLoading = true;
      pushResult = null;

      const payload = {
        title: pushTitle,
        body: pushBody,
        icon: pushIcon || null,
        badge: pushBadge || null
      };

      let response;
      
      if (pushRecipientType === 'single') {
        if (!pushSelectedUserId) {
          showMessage('Please select a user', 'error');
          return;
        }
        response = await axios.post(`/admin/push/single/${pushSelectedUserId}`, payload);
      } else if (pushRecipientType === 'all') {
        response = await axios.post('/admin/push/broadcast', payload);
      } else if (pushRecipientType === 'application') {
        if (!pushSelectedAppId) {
          showMessage('Please select an application', 'error');
          return;
        }
        response = await axios.post(`/admin/push/application/${pushSelectedAppId}`, payload);
      } else if (pushRecipientType === 'list') {
        if (!pushUserIds) {
          showMessage('Please enter user IDs', 'error');
          return;
        }
        const userIdsList = pushUserIds.split(',').map(id => id.trim()).filter(id => id);
        if (userIdsList.length === 0) {
          showMessage('Please enter at least one user ID', 'error');
          return;
        }
        response = await axios.post('/admin/push/users', {
          user_ids: userIdsList,
          payload: payload
        });
      }

      pushResult = response.data;
      showMessage(
        `Push sent! Success: ${pushResult.success_count}, Failed: ${pushResult.failed_count}`,
        pushResult.success_count > 0 ? 'success' : 'error'
      );
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to send push notification', 'error');
      pushResult = null;
    } finally {
      isLoading = false;
    }
  }

  // Reset push form
  function resetPushForm() {
    pushTitle = '';
    pushBody = '';
    pushIcon = '';
    pushBadge = '';
    pushRecipientType = 'single';
    pushSelectedUserId = '';
    pushSelectedAppId = '';
    pushUserIds = '';
    pushResult = null;
  }

  const totalPages = Math.ceil(totalUsers / limit);

  onMount(() => {
    if (token) {
      setAuthHeader();
      loadApplications();
      loadUsers();
      loadAllUsersForSelection();
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

          <!-- Tabs -->
          <div class="tabs tabs-boxed mb-6">
            <button 
              class="tab {activeTab === 'applications' ? 'tab-active' : ''}"
              on:click={() => activeTab = 'applications'}
            >
              Applications
            </button>
            <button 
              class="tab {activeTab === 'users' ? 'tab-active' : ''}"
              on:click={() => activeTab = 'users'}
            >
              Users
            </button>
            <button 
              class="tab {activeTab === 'push' ? 'tab-active' : ''}"
              on:click={() => activeTab = 'push'}
            >
              Push Notifications
            </button>
          </div>

          <!-- Applications Tab -->
          {#if activeTab === 'applications'}
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
          {/if}

          <!-- Users Tab -->
          {#if activeTab === 'users'}
            <div class="card bg-base-200">
              <div class="card-body">
                <h2 class="card-title text-2xl mb-4">Users</h2>

                <!-- Enhanced Filters -->
                <div class="card bg-base-100 mb-4">
                  <div class="card-body">
                    <h3 class="card-title text-lg mb-4">Filters</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div class="form-control">
                        <label class="label">
                          <span class="label-text">Application Name</span>
                        </label>
                        <input 
                          type="text" 
                          placeholder="Filter by application name" 
                          class="input input-bordered w-full"
                          bind:value={filterAppName}
                        />
                      </div>
                      <div class="form-control">
                        <label class="label">
                          <span class="label-text">Application ID</span>
                        </label>
                        <select class="select select-bordered w-full" bind:value={filterAppId}>
                          <option value="">All Applications</option>
                          {#each applications as app}
                            <option value={app.id}>{app.name}</option>
                          {/each}
                        </select>
                      </div>
                      <div class="form-control">
                        <label class="label">
                          <span class="label-text">User ID</span>
                        </label>
                        <input 
                          type="text" 
                          placeholder="Search user ID" 
                          class="input input-bordered w-full"
                          bind:value={filterUserId}
                        />
                      </div>
                      <div class="form-control">
                        <label class="label">
                          <span class="label-text">Created From</span>
                        </label>
                        <input 
                          type="date" 
                          class="input input-bordered w-full"
                          bind:value={filterCreatedFrom}
                        />
                      </div>
                      <div class="form-control">
                        <label class="label">
                          <span class="label-text">Created To</span>
                        </label>
                        <input 
                          type="date" 
                          class="input input-bordered w-full"
                          bind:value={filterCreatedTo}
                        />
                      </div>
                    </div>
                    <div class="flex gap-2 mt-4">
                      <button class="btn btn-primary" on:click={filterUsers}>Apply Filters</button>
                      <button class="btn btn-ghost" on:click={resetFilters}>Reset Filters</button>
                    </div>
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
          {/if}

          <!-- Push Notifications Tab -->
          {#if activeTab === 'push'}
            <div class="card bg-base-200">
              <div class="card-body">
                <h2 class="card-title text-2xl mb-4">Send Push Notification</h2>

                <div class="card bg-base-100 mb-4">
                  <div class="card-body">
                    <!-- Notification Content -->
                    <div class="form-control mb-4">
                      <label class="label">
                        <span class="label-text">Title *</span>
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
                        <span class="label-text">Body *</span>
                      </label>
                      <textarea 
                        placeholder="Notification body" 
                        class="textarea textarea-bordered w-full"
                        bind:value={pushBody}
                      ></textarea>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div class="form-control">
                        <label class="label">
                          <span class="label-text">Icon URL (optional)</span>
                        </label>
                        <input 
                          type="text" 
                          placeholder="https://example.com/icon.png" 
                          class="input input-bordered w-full"
                          bind:value={pushIcon}
                        />
                      </div>
                      <div class="form-control">
                        <label class="label">
                          <span class="label-text">Badge URL (optional)</span>
                        </label>
                        <input 
                          type="text" 
                          placeholder="https://example.com/badge.png" 
                          class="input input-bordered w-full"
                          bind:value={pushBadge}
                        />
                      </div>
                    </div>

                    <!-- Recipient Selection -->
                    <div class="form-control mb-4">
                      <label class="label">
                        <span class="label-text">Send To</span>
                      </label>
                      <div class="flex gap-4 mb-4">
                        <label class="label cursor-pointer">
                          <input 
                            type="radio" 
                            name="recipient" 
                            class="radio radio-primary" 
                            value="single"
                            bind:group={pushRecipientType}
                          />
                          <span class="label-text ml-2">Single User</span>
                        </label>
                        <label class="label cursor-pointer">
                          <input 
                            type="radio" 
                            name="recipient" 
                            class="radio radio-primary" 
                            value="all"
                            bind:group={pushRecipientType}
                          />
                          <span class="label-text ml-2">All Users</span>
                        </label>
                        <label class="label cursor-pointer">
                          <input 
                            type="radio" 
                            name="recipient" 
                            class="radio radio-primary" 
                            value="application"
                            bind:group={pushRecipientType}
                          />
                          <span class="label-text ml-2">Application Users</span>
                        </label>
                        <label class="label cursor-pointer">
                          <input 
                            type="radio" 
                            name="recipient" 
                            class="radio radio-primary" 
                            value="list"
                            bind:group={pushRecipientType}
                          />
                          <span class="label-text ml-2">List of Users</span>
                        </label>
                      </div>

                      <!-- Dynamic fields based on recipient type -->
                      {#if pushRecipientType === 'single'}
                        <select class="select select-bordered w-full" bind:value={pushSelectedUserId}>
                          <option value="">Select User</option>
                          {#each allUsersForSelection as user}
                            <option value={user.id}>{user.label}</option>
                          {/each}
                        </select>
                      {:else if pushRecipientType === 'application'}
                        <select class="select select-bordered w-full" bind:value={pushSelectedAppId}>
                          <option value="">Select Application</option>
                          {#each applications as app}
                            <option value={app.id}>{app.name}</option>
                          {/each}
                        </select>
                      {:else if pushRecipientType === 'list'}
                        <textarea 
                          placeholder="Enter user IDs separated by commas (e.g., user1, user2, user3)" 
                          class="textarea textarea-bordered w-full"
                          bind:value={pushUserIds}
                        ></textarea>
                      {/if}
                    </div>

                    <!-- Action Buttons -->
                    <div class="flex gap-2">
                      <button 
                        class="btn btn-primary" 
                        on:click={sendPushNotification} 
                        disabled={isLoading || !pushTitle || !pushBody}
                      >
                        {isLoading ? 'Sending...' : 'Send Notification'}
                      </button>
                      <button class="btn btn-ghost" on:click={resetPushForm}>Reset Form</button>
                    </div>

                    <!-- Result Display -->
                    {#if pushResult}
                      <div class="alert alert-{pushResult.success_count > 0 ? 'success' : 'error'} mt-4">
                        <div>
                          <h3 class="font-bold">Push Notification Result</h3>
                          <div class="text-sm">
                            <p>Success: {pushResult.success_count}</p>
                            <p>Failed: {pushResult.failed_count}</p>
                            <p>Total: {pushResult.total}</p>
                            <p class="mt-2">{pushResult.message}</p>
                          </div>
                        </div>
                      </div>
                    {/if}
                  </div>
                </div>
              </div>
            </div>
          {/if}

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
