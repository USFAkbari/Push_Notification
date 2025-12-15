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
  let activeTab = 'applications'; // applications, users, push, admins
  let currentAdminInfo = null; // Current logged in admin info

  // Applications state
  let applications = [];
  let showAppForm = false;
  let appFormData = { name: '', store_fingerprint: '' };
  let editingApp = null;
  let secretModal = { show: false, secret: '', title: '' };
  let appSecrets = {}; // Store last generated secret per application (temporary, cleared on reload)

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
  let showUserForm = false;
  let userFormData = { user_id: '', endpoint: '', p256dh: '', auth: '', application_id: '' };
  let showAssignModal = false;
  let userToAssign = null;
  let assignApplicationId = '';

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

  // Admins state
  let admins = [];
  let showAdminForm = false;
  let adminFormData = { username: '', password: '', is_super_admin: false, application_ids: [] };
  let editingAdmin = null;
  let showEditAdminModal = false;

  // Settings state
  let showChangePasswordModal = false;
  let changePasswordData = { current_password: '', new_password: '', confirm_password: '' };

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
      await loadCurrentAdminInfo();
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
      
      // Store secret temporarily
      appSecrets[response.data.id] = response.data.secret;
      
      // Show secret in popup
      secretModal = {
        show: true,
        secret: response.data.secret,
        title: `Application Secret: ${response.data.name}`
      };
      
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
      
      // Store secret temporarily
      appSecrets[response.data.id] = response.data.secret;
      
      // Show secret in popup
      secretModal = {
        show: true,
        secret: response.data.secret,
        title: `New Application Secret: ${response.data.name}`
      };
      
      await loadApplications();
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to reset secret', 'error');
    } finally {
      isLoading = false;
    }
  }

  // Copy secret to clipboard
  async function copySecret(secret) {
    try {
      await navigator.clipboard.writeText(secret);
      showMessage('Secret copied to clipboard!', 'success');
    } catch (error) {
      showMessage('Failed to copy secret', 'error');
    }
  }

  // Close secret modal
  function closeSecretModal() {
    secretModal = { show: false, secret: '', title: '' };
  }

  // Show stored secret for application
  function showStoredSecret(appId, appName) {
    if (appSecrets[appId]) {
      secretModal = {
        show: true,
        secret: appSecrets[appId],
        title: `Application Secret: ${appName}`
      };
    } else {
      showMessage('Secret not available. Please reset the secret to generate a new one.', 'error');
    }
  }

  // Delete application
  async function deleteApplication(appId, appName) {
    if (!confirm(`Are you sure you want to delete application "${appName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      isLoading = true;
      await axios.delete(`/admin/applications/${appId}`);
      showMessage(`Application "${appName}" deleted successfully`, 'success');
      await loadApplications();
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to delete application', 'error');
    } finally {
      isLoading = false;
    }
  }

  // Delete user
  async function deleteUser(userId, userIdentifier) {
    const displayName = userIdentifier || userId;
    if (!confirm(`Are you sure you want to delete user "${displayName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      isLoading = true;
      await axios.delete(`/admin/users/${userId}`);
      showMessage(`User "${displayName}" deleted successfully`, 'success');
      await loadUsers();
      await loadAllUsersForSelection();
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to delete user', 'error');
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

  // Create user
  async function createUser() {
    if (!userFormData.user_id || !userFormData.endpoint || !userFormData.p256dh || !userFormData.auth) {
      showMessage('User ID, endpoint, p256dh, and auth keys are required', 'error');
      return;
    }

    try {
      isLoading = true;
      const response = await axios.post('/admin/users', {
        user_id: userFormData.user_id,
        endpoint: userFormData.endpoint,
        keys: {
          p256dh: userFormData.p256dh,
          auth: userFormData.auth
        },
        application_id: userFormData.application_id || null
      });
      
      showMessage('User created successfully', 'success');
      userFormData = { user_id: '', endpoint: '', p256dh: '', auth: '', application_id: '' };
      showUserForm = false;
      await loadUsers();
      await loadAllUsersForSelection();
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to create user', 'error');
    } finally {
      isLoading = false;
    }
  }

  // Open assign modal
  function openAssignModal(user) {
    userToAssign = user;
    assignApplicationId = user.application_id || '';
    showAssignModal = true;
  }

  // Assign user to application
  async function assignUser() {
    if (!userToAssign) return;

    try {
      isLoading = true;
      const response = await axios.put(`/admin/users/${userToAssign.id}/assign`, {
        application_id: assignApplicationId || null
      });
      
      showMessage('User assigned successfully', 'success');
      showAssignModal = false;
      userToAssign = null;
      assignApplicationId = '';
      await loadUsers();
      await loadAllUsersForSelection();
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to assign user', 'error');
    } finally {
      isLoading = false;
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

  // Load current admin info
  async function loadCurrentAdminInfo() {
    try {
      const response = await axios.get('/admin/admins/me');
      currentAdminInfo = response.data;
    } catch (error) {
      console.error('Failed to load current admin info:', error);
    }
  }

  // Load admins
  async function loadAdmins() {
    try {
      const response = await axios.get('/admin/admins');
      admins = response.data;
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to load admins', 'error');
    }
  }

  // Create admin
  async function createAdmin() {
    if (!adminFormData.username || !adminFormData.password) {
      showMessage('Username and password are required', 'error');
      return;
    }

    try {
      isLoading = true;
      const response = await axios.post('/admin/admins', adminFormData);
      showMessage('Admin created successfully', 'success');
      adminFormData = { username: '', password: '', is_super_admin: false, application_ids: [] };
      showAdminForm = false;
      await loadAdmins();
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to create admin', 'error');
    } finally {
      isLoading = false;
    }
  }

  // Open edit admin modal
  function openEditAdminModal(admin) {
    editingAdmin = admin;
    adminFormData = {
      username: admin.username,
      password: '',
      is_super_admin: admin.is_super_admin,
      application_ids: [...admin.application_ids]
    };
    showEditAdminModal = true;
  }

  // Update admin
  async function updateAdmin() {
    if (!adminFormData.username) {
      showMessage('Username is required', 'error');
      return;
    }

    try {
      isLoading = true;
      const updateData = {
        is_super_admin: adminFormData.is_super_admin,
        application_ids: adminFormData.application_ids
      };
      if (adminFormData.password) {
        updateData.password = adminFormData.password;
      }
      const adminId = editingAdmin.id;
      await axios.put(`/admin/admins/${adminId}`, updateData);
      showMessage('Admin updated successfully', 'success');
      showEditAdminModal = false;
      adminFormData = { username: '', password: '', is_super_admin: false, application_ids: [] };
      const wasCurrentAdmin = adminId === currentAdminInfo?.id;
      editingAdmin = null;
      await loadAdmins();
      if (wasCurrentAdmin) {
        await loadCurrentAdminInfo();
      }
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to update admin', 'error');
    } finally {
      isLoading = false;
    }
  }

  // Delete admin
  async function deleteAdmin(adminId, adminUsername) {
    if (!confirm(`Are you sure you want to delete admin "${adminUsername}"? This action cannot be undone.`)) {
      return;
    }

    try {
      isLoading = true;
      await axios.delete(`/admin/admins/${adminId}`);
      showMessage(`Admin "${adminUsername}" deleted successfully`, 'success');
      await loadAdmins();
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to delete admin', 'error');
    } finally {
      isLoading = false;
    }
  }

  // Toggle application in admin form
  function toggleApplication(appId) {
    const index = adminFormData.application_ids.indexOf(appId);
    if (index > -1) {
      adminFormData.application_ids = adminFormData.application_ids.filter(id => id !== appId);
    } else {
      adminFormData.application_ids = [...adminFormData.application_ids, appId];
    }
  }

  // Change password
  async function changePassword() {
    if (!changePasswordData.current_password || !changePasswordData.new_password) {
      showMessage('Please fill all password fields', 'error');
      return;
    }

    if (changePasswordData.new_password !== changePasswordData.confirm_password) {
      showMessage('New passwords do not match', 'error');
      return;
    }

    if (changePasswordData.new_password.length < 6) {
      showMessage('New password must be at least 6 characters long', 'error');
      return;
    }

    try {
      isLoading = true;
      const response = await axios.post('/admin/change-password', {
        current_password: changePasswordData.current_password,
        new_password: changePasswordData.new_password
      });
      showMessage(response.data.message, 'success');
      changePasswordData = { current_password: '', new_password: '', confirm_password: '' };
      showChangePasswordModal = false;
    } catch (error) {
      showMessage(error.response?.data?.detail || 'Failed to change password', 'error');
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    if (token) {
      setAuthHeader();
      loadApplications();
      loadUsers();
      loadAllUsersForSelection();
      loadCurrentAdminInfo();
    }
  });
</script>

<div class="min-h-screen bg-base-200 p-2 md:p-4">
  <div class="max-w-7xl mx-auto">
    {#if !isAuthenticated}
      <!-- Login Form -->
      <div class="card bg-base-100 shadow-xl max-w-md mx-auto">
        <div class="card-body p-4 md:p-6">
          <h1 class="card-title text-2xl md:text-3xl mb-4">Admin Login</h1>
          
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
        <div class="card-body p-2 md:p-6">
          <div class="flex justify-between items-center mb-4 flex-wrap gap-2">
            <h1 class="card-title text-2xl md:text-3xl">Admin Dashboard</h1>
            <div class="flex gap-2">
              <button class="btn btn-secondary btn-sm md:btn-md" on:click={() => { showChangePasswordModal = true; changePasswordData = { current_password: '', new_password: '', confirm_password: '' }; }}>Settings</button>
              <button class="btn btn-error btn-sm md:btn-md" on:click={logout}>Logout</button>
            </div>
          </div>

          {#if message}
            <div class="alert alert-{messageType === 'error' ? 'error' : messageType === 'success' ? 'success' : 'info'} mb-4">
              <span>{message}</span>
            </div>
          {/if}

          <!-- Tabs -->
          <div class="tabs tabs-boxed mb-6 overflow-x-auto">
            <button 
              class="tab {activeTab === 'applications' ? 'tab-active' : ''} whitespace-nowrap"
              on:click={() => activeTab = 'applications'}
            >
              Applications
            </button>
            <button 
              class="tab {activeTab === 'users' ? 'tab-active' : ''} whitespace-nowrap"
              on:click={() => activeTab = 'users'}
            >
              Users
            </button>
            <button 
              class="tab {activeTab === 'push' ? 'tab-active' : ''} whitespace-nowrap"
              on:click={() => activeTab = 'push'}
            >
              Push Notifications
            </button>
            {#if currentAdminInfo?.is_super_admin}
            <button 
              class="tab {activeTab === 'admins' ? 'tab-active' : ''} whitespace-nowrap"
              on:click={() => { activeTab = 'admins'; if (currentAdminInfo?.is_super_admin) loadAdmins(); }}
            >
              Admins
            </button>
            {/if}
          </div>

          <!-- Applications Tab -->
          {#if activeTab === 'applications'}
            <div class="card bg-base-200 mb-6">
              <div class="card-body">
                <div class="flex justify-between items-center mb-4 flex-wrap gap-2">
                  <h2 class="card-title text-xl md:text-2xl">Applications</h2>
                  <button class="btn btn-primary btn-sm md:btn-md" on:click={() => { showAppForm = !showAppForm; editingApp = null; appFormData = { name: '', store_fingerprint: '' }; }}>
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
                  <div class="overflow-x-auto -mx-2 md:mx-0">
                    <table class="table table-zebra w-full text-sm md:text-base">
                      <thead>
                        <tr>
                          <th class="hidden md:table-cell">Name</th>
                          <th class="table-cell md:hidden">App</th>
                          <th class="hidden lg:table-cell">Store Fingerprint</th>
                          <th class="hidden md:table-cell">Created At</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {#each applications as app}
                          <tr>
                            <td class="font-medium">{app.name}</td>
                            <td class="hidden lg:table-cell">{app.store_fingerprint || '-'}</td>
                            <td class="hidden md:table-cell text-xs">{new Date(app.created_at).toLocaleDateString()}</td>
                            <td>
                              <div class="flex flex-wrap gap-1 md:gap-2">
                                {#if appSecrets[app.id]}
                                  <button class="btn btn-xs md:btn-sm btn-info" on:click={() => showStoredSecret(app.id, app.name)}>
                                    <span class="hidden md:inline">View Secret</span>
                                    <span class="md:hidden">Secret</span>
                                  </button>
                                {/if}
                                <button class="btn btn-xs md:btn-sm btn-warning" on:click={() => resetSecret(app.id)} disabled={isLoading}>
                                  <span class="hidden md:inline">Reset Secret</span>
                                  <span class="md:hidden">Reset</span>
                                </button>
                                <button class="btn btn-xs md:btn-sm btn-error" on:click={() => deleteApplication(app.id, app.name)} disabled={isLoading}>
                                  Delete
                                </button>
                              </div>
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
                <div class="flex justify-between items-center mb-4 flex-wrap gap-2">
                  <h2 class="card-title text-xl md:text-2xl">Users</h2>
                  <button class="btn btn-primary btn-sm md:btn-md" on:click={() => { showUserForm = !showUserForm; userFormData = { user_id: '', endpoint: '', p256dh: '', auth: '', application_id: '' }; }}>
                    {showUserForm ? 'Cancel' : 'Create User'}
                  </button>
                </div>

                {#if showUserForm}
                  <div class="card bg-base-100 mb-4">
                    <div class="card-body">
                      <h3 class="card-title">Create New User</h3>
                      <div class="form-control mb-4">
                        <label class="label">
                          <span class="label-text">User ID *</span>
                        </label>
                        <input 
                          type="text" 
                          placeholder="Enter user ID" 
                          class="input input-bordered w-full"
                          bind:value={userFormData.user_id}
                        />
                      </div>
                      <div class="form-control mb-4">
                        <label class="label">
                          <span class="label-text">Endpoint *</span>
                        </label>
                        <input 
                          type="text" 
                          placeholder="Enter endpoint URL" 
                          class="input input-bordered w-full"
                          bind:value={userFormData.endpoint}
                        />
                      </div>
                      <div class="form-control mb-4">
                        <label class="label">
                          <span class="label-text">p256dh Key *</span>
                        </label>
                        <input 
                          type="text" 
                          placeholder="Enter p256dh key" 
                          class="input input-bordered w-full"
                          bind:value={userFormData.p256dh}
                        />
                      </div>
                      <div class="form-control mb-4">
                        <label class="label">
                          <span class="label-text">Auth Key *</span>
                        </label>
                        <input 
                          type="text" 
                          placeholder="Enter auth key" 
                          class="input input-bordered w-full"
                          bind:value={userFormData.auth}
                        />
                      </div>
                      <div class="form-control mb-4">
                        <label class="label">
                          <span class="label-text">Application (optional)</span>
                        </label>
                        <select class="select select-bordered w-full" bind:value={userFormData.application_id}>
                          <option value="">No Application</option>
                          {#each applications as app}
                            <option value={app.id}>{app.name}</option>
                          {/each}
                        </select>
                      </div>
                      <button class="btn btn-success" on:click={createUser} disabled={isLoading}>
                        {isLoading ? 'Creating...' : 'Create User'}
                      </button>
                    </div>
                  </div>
                {/if}

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
                  <div class="overflow-x-auto mb-4 -mx-2 md:mx-0">
                    <table class="table table-zebra w-full text-sm md:text-base">
                      <thead>
                        <tr>
                          <th class="hidden md:table-cell">User ID</th>
                          <th class="table-cell md:hidden">User</th>
                          <th class="hidden lg:table-cell">Application</th>
                          <th class="hidden xl:table-cell">Endpoint</th>
                          <th class="hidden md:table-cell">Created At</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {#each users as user}
                          <tr>
                            <td class="font-medium">{user.user_id || '-'}</td>
                            <td class="hidden lg:table-cell">{user.application_name || '-'}</td>
                            <td class="hidden xl:table-cell max-w-xs truncate text-xs">{user.endpoint}</td>
                            <td class="hidden md:table-cell text-xs">{new Date(user.created_at).toLocaleDateString()}</td>
                            <td>
                              <div class="flex flex-wrap gap-1 md:gap-2">
                                <button class="btn btn-xs md:btn-sm btn-info" on:click={() => getUserDetails(user.id)}>
                                  <span class="hidden md:inline">View</span>
                                  <span class="md:hidden">👁</span>
                                </button>
                                <button class="btn btn-xs md:btn-sm btn-secondary" on:click={() => openAssignModal(user)} disabled={isLoading}>
                                  <span class="hidden md:inline">Assign</span>
                                  <span class="md:hidden">🔗</span>
                                </button>
                                <button class="btn btn-xs md:btn-sm btn-error" on:click={() => deleteUser(user.id, user.user_id)} disabled={isLoading}>
                                  <span class="hidden md:inline">Delete</span>
                                  <span class="md:hidden">🗑</span>
                                </button>
                              </div>
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
                <h2 class="card-title text-xl md:text-2xl mb-4">Send Push Notification</h2>

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
                      <div class="flex flex-wrap gap-2 md:gap-4 mb-4">
                        <label class="label cursor-pointer">
                          <input 
                            type="radio" 
                            name="recipient" 
                            class="radio radio-primary radio-sm md:radio-md" 
                            value="single"
                            bind:group={pushRecipientType}
                          />
                          <span class="label-text ml-2 text-sm md:text-base">Single User</span>
                        </label>
                        <label class="label cursor-pointer">
                          <input 
                            type="radio" 
                            name="recipient" 
                            class="radio radio-primary radio-sm md:radio-md" 
                            value="all"
                            bind:group={pushRecipientType}
                          />
                          <span class="label-text ml-2 text-sm md:text-base">All Users</span>
                        </label>
                        <label class="label cursor-pointer">
                          <input 
                            type="radio" 
                            name="recipient" 
                            class="radio radio-primary radio-sm md:radio-md" 
                            value="application"
                            bind:group={pushRecipientType}
                          />
                          <span class="label-text ml-2 text-sm md:text-base">Application Users</span>
                        </label>
                        <label class="label cursor-pointer">
                          <input 
                            type="radio" 
                            name="recipient" 
                            class="radio radio-primary radio-sm md:radio-md" 
                            value="list"
                            bind:group={pushRecipientType}
                          />
                          <span class="label-text ml-2 text-sm md:text-base">List of Users</span>
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

          <!-- Secret Modal -->
          {#if secretModal.show}
            <div class="modal modal-open">
              <div class="modal-box">
                <h3 class="font-bold text-lg mb-4">{secretModal.title}</h3>
                <div class="alert alert-warning mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <span>Please copy this secret now. You won't be able to see it again!</span>
                </div>
                <div class="form-control mb-4">
                  <label class="label">
                    <span class="label-text">Secret</span>
                  </label>
                  <div class="flex gap-2">
                    <input 
                      type="text" 
                      readonly
                      class="input input-bordered w-full font-mono"
                      value={secretModal.secret}
                      id="secret-input"
                    />
                    <button class="btn btn-primary" on:click={() => copySecret(secretModal.secret)}>
                      Copy
                    </button>
                  </div>
                </div>
                <div class="modal-action">
                  <button class="btn" on:click={closeSecretModal}>Close</button>
                </div>
              </div>
            </div>
          {/if}

          <!-- Admins Tab -->
          {#if activeTab === 'admins' && currentAdminInfo?.is_super_admin}
            <div class="card bg-base-200">
              <div class="card-body">
                <div class="flex justify-between items-center mb-4 flex-wrap gap-2">
                  <h2 class="card-title text-xl md:text-2xl">Admins</h2>
                  <button class="btn btn-primary btn-sm md:btn-md" on:click={() => { showAdminForm = !showAdminForm; editingAdmin = null; adminFormData = { username: '', password: '', is_super_admin: false, application_ids: [] }; }}>
                    {showAdminForm ? 'Cancel' : 'Create Admin'}
                  </button>
                </div>

                {#if showAdminForm}
                  <div class="card bg-base-100 mb-4">
                    <div class="card-body">
                      <h3 class="card-title">Create New Admin</h3>
                      <div class="form-control mb-4">
                        <label class="label">
                          <span class="label-text">Username *</span>
                        </label>
                        <input 
                          type="text" 
                          placeholder="Enter username" 
                          class="input input-bordered w-full"
                          bind:value={adminFormData.username}
                        />
                      </div>
                      <div class="form-control mb-4">
                        <label class="label">
                          <span class="label-text">Password *</span>
                        </label>
                        <input 
                          type="password" 
                          placeholder="Enter password" 
                          class="input input-bordered w-full"
                          bind:value={adminFormData.password}
                        />
                      </div>
                      <div class="form-control mb-4">
                        <label class="label cursor-pointer">
                          <input 
                            type="checkbox" 
                            class="checkbox checkbox-primary"
                            bind:checked={adminFormData.is_super_admin}
                          />
                          <span class="label-text ml-2">Super Admin (Full Access)</span>
                        </label>
                      </div>
                      {#if !adminFormData.is_super_admin}
                        <div class="form-control mb-4">
                          <label class="label">
                            <span class="label-text">Allowed Applications</span>
                          </label>
                          <div class="border rounded-lg p-4 max-h-60 overflow-y-auto">
                            {#each applications as app}
                              <label class="label cursor-pointer justify-start">
                                <input 
                                  type="checkbox" 
                                  class="checkbox checkbox-sm checkbox-primary mr-2"
                                  checked={adminFormData.application_ids.includes(app.id)}
                                  on:change={() => toggleApplication(app.id)}
                                />
                                <span class="label-text">{app.name}</span>
                              </label>
                            {/each}
                          </div>
                        </div>
                      {/if}
                      <button class="btn btn-success" on:click={createAdmin} disabled={isLoading}>
                        {isLoading ? 'Creating...' : 'Create Admin'}
                      </button>
                    </div>
                  </div>
                {/if}

                {#if admins.length === 0}
                  <p class="text-center text-gray-500">No admins found.</p>
                {:else}
                  <div class="overflow-x-auto -mx-2 md:mx-0">
                    <table class="table table-zebra w-full text-sm md:text-base">
                      <thead>
                        <tr>
                          <th>Username</th>
                          <th class="hidden md:table-cell">Super Admin</th>
                          <th class="hidden lg:table-cell">Applications</th>
                          <th class="hidden md:table-cell">Created At</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {#each admins as admin}
                          <tr>
                            <td class="font-medium">{admin.username}</td>
                            <td class="hidden md:table-cell">{admin.is_super_admin ? 'Yes' : 'No'}</td>
                            <td class="hidden lg:table-cell">
                              {#if admin.is_super_admin}
                                <span class="badge badge-primary badge-sm">All</span>
                              {:else if admin.application_ids.length > 0}
                                <div class="flex flex-wrap gap-1">
                                  {#each applications.filter(a => admin.application_ids.includes(a.id)) as app}
                                    <span class="badge badge-secondary badge-sm">{app.name}</span>
                                  {/each}
                                </div>
                              {:else}
                                <span class="text-gray-500 text-xs">None</span>
                              {/if}
                            </td>
                            <td class="hidden md:table-cell text-xs">{new Date(admin.created_at).toLocaleDateString()}</td>
                            <td>
                              <div class="flex flex-wrap gap-1 md:gap-2">
                                <button class="btn btn-xs md:btn-sm btn-warning" on:click={() => openEditAdminModal(admin)} disabled={isLoading}>
                                  Edit
                                </button>
                                {#if admin.id !== currentAdminInfo?.id}
                                  <button class="btn btn-xs md:btn-sm btn-error" on:click={() => deleteAdmin(admin.id, admin.username)} disabled={isLoading}>
                                    Delete
                                  </button>
                                {/if}
                              </div>
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

          <!-- Assign User Modal -->
          {#if showAssignModal && userToAssign}
            <div class="modal modal-open">
              <div class="modal-box">
                <h3 class="font-bold text-lg mb-4">Assign User to Application</h3>
                <div class="space-y-2 mb-4">
                  <p><strong>User ID:</strong> {userToAssign.user_id || '-'}</p>
                  <p><strong>Current Application:</strong> {userToAssign.application_name || 'None'}</p>
                </div>
                <div class="form-control mb-4">
                  <label class="label">
                    <span class="label-text">Application</span>
                  </label>
                  <select class="select select-bordered w-full" bind:value={assignApplicationId}>
                    <option value="">No Application</option>
                    {#each applications as app}
                      <option value={app.id}>{app.name}</option>
                    {/each}
                  </select>
                </div>
                <div class="modal-action">
                  <button class="btn btn-ghost" on:click={() => { showAssignModal = false; userToAssign = null; assignApplicationId = ''; }}>Cancel</button>
                  <button class="btn btn-primary" on:click={assignUser} disabled={isLoading}>
                    {isLoading ? 'Assigning...' : 'Assign'}
                  </button>
                </div>
              </div>
            </div>
          {/if}

          <!-- Edit Admin Modal -->
          {#if showEditAdminModal && editingAdmin}
            <div class="modal modal-open">
              <div class="modal-box">
                <h3 class="font-bold text-lg mb-4">Edit Admin: {editingAdmin.username}</h3>
                <div class="form-control mb-4">
                  <label class="label">
                    <span class="label-text">Username</span>
                  </label>
                  <input 
                    type="text" 
                    class="input input-bordered w-full"
                    value={editingAdmin.username}
                    disabled
                  />
                </div>
                <div class="form-control mb-4">
                  <label class="label">
                    <span class="label-text">New Password (leave empty to keep current)</span>
                  </label>
                  <input 
                    type="password" 
                    placeholder="Enter new password" 
                    class="input input-bordered w-full"
                    bind:value={adminFormData.password}
                  />
                </div>
                <div class="form-control mb-4">
                  <label class="label cursor-pointer">
                    <input 
                      type="checkbox" 
                      class="checkbox checkbox-primary"
                      bind:checked={adminFormData.is_super_admin}
                    />
                    <span class="label-text ml-2">Super Admin (Full Access)</span>
                  </label>
                </div>
                {#if !adminFormData.is_super_admin}
                  <div class="form-control mb-4">
                    <label class="label">
                      <span class="label-text">Allowed Applications</span>
                    </label>
                    <div class="border rounded-lg p-4 max-h-60 overflow-y-auto">
                      {#each applications as app}
                        <label class="label cursor-pointer justify-start">
                          <input 
                            type="checkbox" 
                            class="checkbox checkbox-sm checkbox-primary mr-2"
                            checked={adminFormData.application_ids.includes(app.id)}
                            on:change={() => toggleApplication(app.id)}
                          />
                          <span class="label-text">{app.name}</span>
                        </label>
                      {/each}
                    </div>
                  </div>
                {/if}
                <div class="modal-action">
                  <button class="btn btn-ghost" on:click={() => { showEditAdminModal = false; editingAdmin = null; adminFormData = { username: '', password: '', is_super_admin: false, application_ids: [] }; }}>Cancel</button>
                  <button class="btn btn-primary" on:click={updateAdmin} disabled={isLoading}>
                    {isLoading ? 'Updating...' : 'Update Admin'}
                  </button>
                </div>
              </div>
            </div>
          {/if}

          <!-- Change Password Modal -->
          {#if showChangePasswordModal}
            <div class="modal modal-open">
              <div class="modal-box">
                <h3 class="font-bold text-lg mb-4">Change Password</h3>
                <div class="form-control mb-4">
                  <label class="label">
                    <span class="label-text">Current Password *</span>
                  </label>
                  <input 
                    type="password" 
                    placeholder="Enter current password" 
                    class="input input-bordered w-full"
                    bind:value={changePasswordData.current_password}
                  />
                </div>
                <div class="form-control mb-4">
                  <label class="label">
                    <span class="label-text">New Password *</span>
                  </label>
                  <input 
                    type="password" 
                    placeholder="Enter new password (min 6 characters)" 
                    class="input input-bordered w-full"
                    bind:value={changePasswordData.new_password}
                  />
                </div>
                <div class="form-control mb-4">
                  <label class="label">
                    <span class="label-text">Confirm New Password *</span>
                  </label>
                  <input 
                    type="password" 
                    placeholder="Confirm new password" 
                    class="input input-bordered w-full"
                    bind:value={changePasswordData.confirm_password}
                  />
                </div>
                <div class="modal-action">
                  <button class="btn btn-ghost" on:click={() => { showChangePasswordModal = false; changePasswordData = { current_password: '', new_password: '', confirm_password: '' }; }}>Cancel</button>
                  <button class="btn btn-primary" on:click={changePassword} disabled={isLoading}>
                    {isLoading ? 'Changing...' : 'Change Password'}
                  </button>
                </div>
              </div>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>
